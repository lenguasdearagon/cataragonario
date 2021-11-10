from django.core.management.base import BaseCommand
from linguatec_lexicon.models import DiatopicVariation, Lexicon, Region


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--drop', action='store_true', dest='drop',
            help="Drop existing data before initializing.",
        )
    def handle(self, *args, **options):
        if options['drop']:
            self.drop_all()

        self.init_lexicon()
        self.init_diatopic_variations()

    def drop_all(self):
        DiatopicVariation.objects.all().delete()
        Region.objects.all().delete()
        Lexicon.objects.all().delete()

    def init_lexicon(self):
        Lexicon.objects.create(
            name="castellano-catalán",
            description="Diccionario dialectal del catalán de Aragón",
            src_language="es",
            dst_language="ca"
        )

    def init_diatopic_variations(self):
        data = {'bajoara': {'Aiguaviva',
                            'Bellmunt',
                            'Belmunt',
                            'Torrevilella',
                            'la Codonyera',
                            'la Ginebrosa'},
                'caspe': {'Favara'},
                'cinca': {'Fraga', 'Mequinensa', 'Mequinenza', 'Saidí'},
                'litera': {'Peralta de la Sal'},
                'matarranya': {'Massalió',
                               'Massalíó',
                               'Vall-de-roures',
                               'Valljunquera'},
                'ribagorza': {'Estanya',
                              'Sopeira',
                              'Tolba',
                              'la Pobla de Roda',
                              'les Paúls',
                              'les Paüls'}}

        for region, variations in data.items():
            r = Region.objects.create(name=region)
            DiatopicVariation.objects.bulk_create([
                DiatopicVariation(name=name, abbreviation=name, region=r) for name in variations
            ])
