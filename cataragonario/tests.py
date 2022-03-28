import os
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase

from cataragonario.management.commands.importmultivariation import extract_regions

BASE_DIR = Path(__file__).resolve().parent

class RowEntryTest(TestCase):
    def extract_and_assert(self, value, expected):
        self.assertEqual(extract_regions(value), expected)

    def test_only_region(self):
        value = "ribagorza"
        expected = [("ribagorza", []), ]
        self.extract_and_assert(value, expected)

    def test_single_region_extra_spaces(self):
        value = "  ribagorza "
        expected = [("ribagorza", []), ]
        self.extract_and_assert(value, expected)

    def test_single_region_with_variation(self):
        value = "bajoara (la Codonyera)"
        expected = [("bajoara", ["la codonyera"]), ]
        self.extract_and_assert(value, expected)

    def test_single_region_multi_variation(self):
        value = "bajoara (Torrevilella, Aiguaviva)"
        expected = [("bajoara", ["torrevilella", "aiguaviva"]), ]
        self.extract_and_assert(value, expected)

    def test_multi_region(self):
        value = "ribagorza (Sopeira), cinca (Saidí, Mequinensa)"
        expected = [("ribagorza", ["sopeira"]), ("cinca", ["saidí", "mequinensa"])]
        self.extract_and_assert(value, expected)

    def test_multi_region_without_variation(self):
        value = "ribagorza, litera"
        expected = [("ribagorza", []), ("litera", [])]
        self.extract_and_assert(value, expected)

    def test_several_regions(self):
        value = "ribagorza (Sopeira), cinca (Saidí, Mequinensa), bajoara"
        expected = [("ribagorza", ["sopeira"]), ("cinca", ["saidí", "mequinensa"]), ("bajoara", [])]
        self.extract_and_assert(value, expected)

    def test_several_regions_without_variation(self):
        value = "ribagorza, litera, bajoara"
        expected = [("ribagorza", []), ("litera", []), ("bajoara", [])]
        self.extract_and_assert(value, expected)

    def test_unbalanced_parenthesis(self):
        value = "ribagorza (Les Paüls), matarranya (Vall-de-roures("
        self.assertRaises(ValidationError, extract_regions, value)

class RowEntryRegionTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("init_project")
        call_command("importgramcat", os.path.join(
            BASE_DIR, "../env/src/linguatec-lexicon/tests/fixtures/gramcat-es-ar.csv"))

    def extract_and_assert(self, value, expected):
        from cataragonario.management.commands.importmultivariation import RowEntry
        row = RowEntry(('bota', 's. f.', value, 'bota', 'bota'), 2)
        row.errors = []

        try:
            row.clean()
        except ValidationError:
            row.clean_regions(value)

        cleaned_data = [variation.name for variation in row.variations]

        self.assertEqual(cleaned_data, expected)

    def test_general(self):
        value = None
        expected = ["general"]
        self.extract_and_assert(value, expected)

    def test_only_region(self):
        value = "ribagorza"
        expected = ["Ribagorza"]
        self.extract_and_assert(value, expected)

    def test_only_variation(self):
        value = "la codonyera"
        expected = ["La Codonyera"]
        self.extract_and_assert(value, expected)

    def test_several_regions_without_variation(self):
        value = "ribagorza, litera, bajoara"
        expected = ["Ribagorza", "Litera", "Bajoara"]
        self.extract_and_assert(value, expected)

    def test_single_region_with_variation(self):
        value = "bajoara (la Codonyera)"
        expected = ["La Codonyera"]
        self.extract_and_assert(value, expected)

    def test_single_region_multi_variation(self):
        value = "bajoara (Torrevelilla, Aiguaviva)"
        expected = ["Torrevelilla", "Aiguaviva"]
        self.extract_and_assert(value, expected)

    def test_multi_region(self):
        value = "ribagorza (Sopeira), cinca (Saidí, Mequinensa)"
        expected = ["Sopeira", "Saidí", "Mequinensa"]
        self.extract_and_assert(value, expected)

    def test_multi_region_without_variation(self):
        value = "ribagorza, litera"
        expected = ["Ribagorza", "Litera"]
        self.extract_and_assert(value, expected)

    def test_several_regions(self):
        value = "ribagorza (Sopeira), cinca (Saidí, Mequinensa), bajoara"
        expected = ["Sopeira", "Saidí", "Mequinensa", "Bajoara"]
        self.extract_and_assert(value, expected)

    def test_region_case_insensitive_match(self):
        value = "riBagOrza"
        expected = ["Ribagorza"]
        self.extract_and_assert(value, expected)
