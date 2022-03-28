from django.core.exceptions import ValidationError
from django.test import TestCase

from cataragonario.management.commands.importmultivariation import extract_regions


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
