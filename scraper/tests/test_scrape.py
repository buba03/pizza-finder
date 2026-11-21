import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scrape  # noqa: E402

FIXTURE = Path(__file__).with_name("fixture_openpage.json")


def labels(p):
    return [t["label"] for t in p["toppings"]]


class ParseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pizzas, cls.unknown = scrape.extract(json.loads(FIXTURE.read_text("utf-8")))
        cls.by_name = {p["name"]: p for p in cls.pizzas if not p["badge"]}

    def test_count_and_no_unknowns(self):
        self.assertEqual(len(self.pizzas), 31)
        self.assertEqual(self.unknown, [])

    def test_deals_and_addons_skipped(self):
        names = {p["name"] for p in self.pizzas}
        for bad in ("RandiMix™", "Randi Trió", "Páros pizza menü", "+ feltét", "Gulyásleves"):
            self.assertNotIn(bad, names)

    def test_crust_dropped_and_base_found(self):
        p = self.by_name["Ámor"]
        self.assertEqual(p["base"]["group"], "paradicsomos")
        self.assertEqual(labels(p), ["füstölt sonka", "gomba", "kukorica", "mozzarella"])

    def test_missing_comma_split(self):
        self.assertIn("kaliforniai paprika", labels(self.by_name["Loki"]))
        self.assertIn("lilahagyma", labels(self.by_name["Loki"]))

    def test_sizes_merged(self):
        sizes = [(s["cm"], s["price"]) for s in self.by_name["Lucifer"]["sizes"]]
        self.assertEqual(sizes, [(32, 4220), (50, 10350)])

    def test_family_keys(self):
        ozirisz = {k for t in self.by_name["Ozirisz"]["toppings"] for k in t["keys"]}
        self.assertTrue({"sonka", "szalámi", "sajt"} <= ozirisz)

    def test_spicy_and_optional_spice(self):
        self.assertTrue(self.by_name["Lucifer"]["spicy"])
        self.assertFalse(self.by_name["Ámor"]["spicy"])
        self.assertIn("Mimir", self.by_name)

    def test_month_pizza_badge(self):
        month = [p for p in self.pizzas if p["badge"] == "A hónap pizzája"]
        self.assertEqual(len(month), 1)
        self.assertEqual(month[0]["name"], "Afrodité")


if __name__ == "__main__":
    unittest.main()
