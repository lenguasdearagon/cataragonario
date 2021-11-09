from django.test import TestCase

from cataragonario.management.commands.importmultivariation import extract_regions



class RowEntryTest(TestCase):
    def extract_and_assert(self, value, expected):
        self.assertListEqual(extract_regions(value), expected)

    def test_only_region(self):
        value = "ribagorza"
        expected = ["ribagorza"]
        self.extract_and_assert(value, expected)

    def test_single_region_extra_spaces(self):
        value = "  ribagorza "
        expected = ["ribagorza"]
        self.extract_and_assert(value, expected)

    def test_single_region_with_variation(self):
        value = "bajoara (la Codonyera)"
        expected = ["bajoara"]
        self.extract_and_assert(value, expected)

    def test_single_region_multi_variation(self):
        value = "bajoara (Torrevilella, Aiguaviva)"
        expected = ["bajoara"]
        self.extract_and_assert(value, expected)

    def test_multi_region(self):
        value = "ribagorza (Sopeira), cinca (Saidí, Mequinensa)"
        expected = ["ribagorza", "cinca"]
        self.extract_and_assert(value, expected)

    def test_multi_region_without_variation(self):
        value = "ribagorza, litera"
        expected = ["ribagorza", "litera"]
        self.extract_and_assert(value, expected)

    def test_several_region(self):
        value = "ribagorza (Sopeira), cinca (Saidí, Mequinensa), bajoara"
        expected = ["ribagorza", "cinca", "bajoara"]
        self.extract_and_assert(value, expected)

    def test_multi_region_without_variation(self):
        value = "ribagorza, litera, bajoara"
        expected = ["ribagorza", "litera", "bajoara"]
        self.extract_and_assert(value, expected)
