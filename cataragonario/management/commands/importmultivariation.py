import os
import pprint
import sys

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from linguatec_lexicon.models import DiatopicVariation, Entry, Lexicon, Word
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
        # xlsx = pd.read_excel(self.input_file, sheet_name=None, header=None, usecols="A:E",
        #                      names=['term', 'gramcats', 'regions', 'cat', 'es'])

        # TODO remove me
        lex = Lexicon.objects.get(name='es-ca')
        lex.words.all().delete()
        Entry.objects.all().delete()
        # TODO /remove me

        wb = load_workbook(filename=self.input_file, read_only=True)

        for ws in wb:
            for i, row in enumerate(ws.values):
                if i == 0:
                    continue    # skip first row because contains headers

                try:
                    row = RowEntry(row)
                except ValidationError as e:
                    print(e)
                    raise

                print(row.term, row.gramcats, row.regions, row.cat, row.es)

                for es_term in row.es:
                    word, created = Word.objects.get_or_create(lexicon=lex, term=es_term)

                    # create entries of normalized catalan
                    for cat_term in row.cat:
                        try:
                            entry = Entry.objects.get_or_create(word=word, translation=cat_term)
                        except:
                            continue

                        # TODO set gramcats

                    # create entries of dialectal catalan
                    # DiatopicVariation == Cities | Valleys
                    # Region == County
                    # TODO extract first regions & diatopic variations
                    for variation in row.variations:
                        import pdb; pdb.set_trace()
                        variation = DiatopicVariation.objects.get(XXX)
                        entry = Entry.objects.get_or_create(word=word, translation=row.term, variation__name=variation)

                        # TODO set gramcats


                if i > 35:
                    break

    def extract_regions_from_spreadsheet(self):
        wb = load_workbook(filename=self.input_file, read_only=True)
        ws = wb.worksheets[0]

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

            self.stdout.write(pprint.pformat(row.regions))

        return regions


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


class RowEntry:
    term = ''
    gramcats = []
    regions = []
    cat = ''
    es = ''

    def __init__(self, row) -> None:
        self.row = row
        self.term = self.clean_term(row[0])
        self.gramcats = self.clean_gramcats(row[1])
        self.regions = self.clean_regions(row[2])
        self.cat = self.clean_cat(row[3])
        self.es = self.clean_es(row[4])

    def clean_term(self, value):
        try:
            return value.strip()
        except Exception as e:
            print(e)
            import pdb; pdb.set_trace()
            raise

    def clean_gramcats(self, value):
        return split_and_strip(value)

    def clean_regions(self, value):
        return extract_regions(value)

    def clean_cat(self, value):
        return split_and_strip(value)

    def clean_es(self, value):
        return split_and_strip(value)
