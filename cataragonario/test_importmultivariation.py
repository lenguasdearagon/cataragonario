from pathlib import Path

import linguatec_lexicon
from django.core.management import call_command
from django.test import TestCase

from linguatec_lexicon.models import Entry, Word

BASE_DIR = Path(__file__).resolve().parent
LINGUATEC_DIR = Path(linguatec_lexicon.__file__).parent


class ImportMultivariationTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        call_command("init_project")
        call_command("importgramcat", LINGUATEC_DIR.parent.joinpath('tests/fixtures/gramcat-es-ar.csv'))
        super().setUpTestData()

    def get_data_full_path(self, filename):
        return BASE_DIR.parent.joinpath("tests/data/", filename)

    def test_a(self):
        call_command("importmultivariation", self.get_data_full_path("multiple-items.xlsx"))
        self.assertEqual(2, Word.objects.count())
        self.assertEqual(2, Entry.objects.filter(variation__isnull=True).count())
        self.assertEqual(10, Entry.objects.filter(variation__isnull=False).count())

    def test_b(self):
        call_command("importmultivariation", self.get_data_full_path("entry-with-multiple-variations.xlsx"))
        self.assertEqual(1, Word.objects.count())
        self.assertEqual(1, Entry.objects.filter(variation__isnull=True).count())
        self.assertEqual(3, Entry.objects.filter(variation__isnull=False).count())

    def test_c(self):
        call_command("importmultivariation", self.get_data_full_path("entry-with-different-words.xlsx"))
        self.assertEqual(2, Word.objects.count())
        self.assertEqual(2, Entry.objects.filter(variation__isnull=True).count())
        self.assertEqual(3, Entry.objects.filter(variation__isnull=False).count())
