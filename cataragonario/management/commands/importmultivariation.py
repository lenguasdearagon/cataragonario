import os
import pprint
import sys

from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.core.management.base import BaseCommand, CommandError
from linguatec_lexicon.models import DiatopicVariation, Entry, GramaticalCategory, Lexicon, Word
from linguatec_lexicon.validators import validate_balanced_parenthesis
from openpyxl import load_workbook


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str)
        parser.add_argument(
            '--extract-regions', action='store_true', dest='extract_regions',
            help="Extract regions from input file.",
        )

    def handle(self, *args, **options):
        self.input_file = options['input_file']
        self.verbosity = options['verbosity']

        self.validate_input_file()

        if options['extract_regions']:
            self.extract_regions_from_spreadsheet()
            sys.exit(0)

        self.populate_models()

    def validate_input_file(self):
        _, file_extension = os.path.splitext(self.input_file)
        if file_extension.lower() != '.xlsx':
            raise CommandError(
                'Unexpected filetype "{}". Should be an Excel document (XLSX)'.format(file_extension))

    def populate_models(self):
        # TODO remove me
        lex = Lexicon.objects.get(name='castellano-catalán')
        lex.words.all().delete()
        Entry.objects.all().delete()
        # TODO /remove me

        ws = self.load_first_worksheet()
        for i, row in enumerate(ws.values):
            if i == 0:
                continue    # skip first row because contains headers

            try:
                row = RowEntry(row)
            except EmptyRow:
                continue
            except ValidationError as e:
                print(e)
                raise

            gramcats = row.gramcats
            for es_term in row.es:
                word, created = Word.objects.get_or_create(lexicon=lex, term=es_term)

                # create entries of normalized catalan
                for cat_term in row.cat:
                    entry = Entry.objects.create(word=word, translation=cat_term)
                    entry.gramcats.set(gramcats)

                # create entries of dialectal catalan
                # DiatopicVariation == Cities | Valleys
                # Region == County
                for variation in row.variations:
                    entry = Entry.objects.create(word=word, translation=row.term, variation=variation)
                    entry.gramcats.set(gramcats)

    def extract_regions_from_spreadsheet(self):
        ws = self.load_first_worksheet()

        regions = []
        for i, row in enumerate(ws.values):
            # skip first row because contains headers
            # skip empty rows
            if i == 0 or not any(row):
                continue

            try:
                row = RowEntry(row)
            except ValidationError as e:
                self.stderr.write(e)
                raise

            regions += row.regions

        regions_grouped = {}
        for region, cities in regions:
            if region not in regions_grouped:
                regions_grouped[region] = set()
            regions_grouped[region].update(set(cities))

        self.stdout.write(pprint.pformat(regions_grouped))

        return regions_grouped

    def load_first_worksheet(self):
        wb = load_workbook(filename=self.input_file, read_only=True)

        if len(wb.worksheets) > 1:
            self.stderr.write("WARNING: only data of first worksheet will be imported.")

        return wb.worksheets[0]


def extract_regions(value):
    value = value.strip()
    validate_balanced_parenthesis(value)

    comma_position = value.find(",")
    regions = []
    if comma_position == -1:
        extracted_region = split_region_and_variants(value)
    else:
        parenthesis_beg_position = value.find("(")
        parenthesis_end_position = value.find(")")
        if comma_position > parenthesis_beg_position and comma_position < parenthesis_end_position:
            extracted_region = split_region_and_variants(value)
            next_comma_position = value.find(",", parenthesis_end_position)
            if next_comma_position == -1:
                raw = ''
            else:
                raw = value[next_comma_position + 1:]
        else:
            region_left = value[:comma_position]
            extracted_region = split_region_and_variants(region_left)
            raw = value[comma_position + 1:]

        if raw:
            regions += extract_regions(raw)

    regions = [extracted_region] + regions

    return regions


def split_region_and_variants(value):
    parenthesis_beg_position = value.find("(")
    parenthesis_end_position = value.find(")")

    if parenthesis_beg_position == -1:
        region = value
        variants = []
    else:
        region = value[:parenthesis_beg_position]
        variants = value[parenthesis_beg_position + 1:parenthesis_end_position]
        variants = split_and_strip(variants)

    return (region.strip(), variants)


def extract_variants(value):
    z = split_and_strip(value)
    print("VARIANT: ", z)
    return z


def split_and_strip(value):
    return [item.strip() for item in value.split(',')]


class EmptyRow(Exception):
    pass


class RowEntry:
    fields = ['term', 'gramcats', 'regions', 'cat', 'es']

    def __init__(self, row) -> None:
        self.row = row
        self.clean()

    def clean(self):
        if not any(self.row):
            raise EmptyRow()

        self.cleaned_data = {}
        for i, fieldname in enumerate(self.fields):
            value = self.row[i]
            clean_method = getattr(self, "clean_{}".format(fieldname))
            self.cleaned_data[fieldname] = clean_method(value)
            setattr(self, fieldname, self.cleaned_data[fieldname])

        return self.cleaned_data

    def clean_term(self, value):
        return value.strip()

    def clean_gramcats(self, value):
        # TODO(@slamora) optimize queries
        gramcats = []
        for abbr in split_and_strip(value):
            try:
                gramcats.append(GramaticalCategory.objects.get(abbreviation=abbr))
            except GramaticalCategory.DoesNotExist as e:
                raise ValidationError(e)

        return gramcats

    def clean_regions(self, value):
        return extract_regions(value)

    def clean_cat(self, value):
        return split_and_strip(value)

    def clean_es(self, value):
        return split_and_strip(value)

    @property
    def variations(self):
        variation_names = []
        for reg in self.regions:
            variation_names += reg[1]

        # TODO(@slamora) optimize queries
        variations = []
        for name in variation_names:
            try:
                variations.append(DiatopicVariation.objects.get(name=name))
            except DiatopicVariation.DoesNotExist as e:
                raise ValidationError(e)

        return variations
