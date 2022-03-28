import os
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from linguatec_lexicon.models import Entry, Word

BASE_DIR = Path(__file__).resolve().parent


class ImportMultivariationTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        call_command("init_project")
        call_command("importgramcat", os.path.join(BASE_DIR, "../env/src/linguatec-lexicon/tests/fixtures/gramcat-es-ar.csv"))
        super().setUpTestData()

    def test_a(self):
        call_command("importmultivariation", os.path.join(BASE_DIR, "../tests/data/multiple-items.xlsx"))

        self.assertEqual(2, Word.objects.count())
        self.assertEqual(2, Entry.objects.filter(variation__isnull=True).count())
        self.assertEqual(10, Entry.objects.filter(variation__isnull=False).count())

    def test_b(self):
        call_command("importmultivariation", os.path.join(BASE_DIR, "../tests/data/entry-with-multiple-variations.xlsx"))
        self.assertEqual(1, Word.objects.count())
        self.assertEqual(1, Entry.objects.filter(variation__isnull=True).count())
        self.assertEqual(3, Entry.objects.filter(variation__isnull=False).count())
