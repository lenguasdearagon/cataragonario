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
        data = {
            'Bajoara': {
                'Bajoara',
                'Aiguaviva',
                'Bellmunt',
                'Bellmunt de Mesquí',
                'La Codonyera',
                'La Ginebrosa',
                'Torrevelilla'
            },
            'Casp': {
                'Casp', 'Faió', 'Favara'
            },
            'Cinca': {
                'Cinca', 'Fraga', 'Mequinensa', 'Saidí'
            },
            'Litera': {
                'Litera', 'Açanui', 'Albelda', 'Peralta de la Sal'
            },
            'Matarranya': {
                'Matarranya', 'Calaceit', 'Massalió', 'Pena-roja', 'Vall-de-roures', 'Valljunquera'
            },
            'Ribagorza': {
                'Ribagorza',
                'Areny',
                'Estanya',
                'La Pobla de Roda',
                'Noals',
                'Les Paüls',
                'Sopeira',
                'Tolba',
            }
        }

        # Add special value to handle general usage of the term
        data['Franja'] = {'general'}

        for region, variations in data.items():
            r = Region.objects.create(name=region)
            DiatopicVariation.objects.bulk_create([
                DiatopicVariation(name=name, abbreviation=name, region=r) for name in variations
            ])
