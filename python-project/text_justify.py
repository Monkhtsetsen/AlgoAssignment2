import unittest
from unittest.mock import MagicMock
from biydaalt2 import (
    split_words, justify_line, greedy_break, dp_break,
    greedy_justify_with_hyphenation, Mongolian, format_by_type
)


class TestTextJustifier(unittest.TestCase):

    def setUp(self):
        """Mock hyphenator: 'монгол' → ['мон-', 'гол']"""
        self.mock_hyph = MagicMock()
        # “монгол” гэдэг үгийг 3-р байрлалд таслана.
        self.mock_hyph.hyphenate.side_effect = lambda w: [3] if w == "монгол" else []

    # split_words tests
    def test_split_words_basic(self):
        self.assertEqual(split_words("Сайн байна уу"), ["Сайн", "байна", "уу"])

    def test_split_words_multiple_spaces(self):
        self.assertEqual(split_words("Сайн   байна   уу"), ["Сайн", "байна", "уу"])

    # -----------------------------
    # justify_line tests
    # -----------------------------
    def test_justify_line_single_word(self):
        res = justify_line(["Hello"], 10)
        self.assertEqual(res, "Hello     ")

    def test_justify_line_multiple_words(self):
        res = justify_line(["Hello", "world"], 15)
        # 5 chars + 5 chars = 10 → need 5 spaces
        self.assertEqual(res, "Hello     world")

    # -----------------------------
    # greedy_break tests
    # -----------------------------
    def test_greedy_break_simple(self):
        words = ["a", "bb", "ccc"]
        lines = greedy_break(words, 4)
        self.assertEqual(lines, [["a", "bb"], ["ccc"]])

    # -----------------------------
    # dp_break tests
    # -----------------------------
    def test_dp_break_simple(self):
        words = ["aaa", "bb", "c"]
        lines = dp_break(words, 5)
        # possible optimal: ["aaa"], ["bb", "c"]
        self.assertEqual(lines, [["aaa"], ["bb", "c"]])

    # -----------------------------
    # hyphenation (Mongolian class)
    # -----------------------------
    def test_mongolian_hyphenate(self):
        m = Mongolian()
        cuts = m.hyphenate("монгол")
        self.assertIsInstance(cuts, list)

    # -----------------------------
    # greedy + hyphenation
    # -----------------------------
    def test_greedy_hyphenation_split(self):
        words = ["энэ", "бол", "монгол"]
        result = greedy_justify_with_hyphenation(words, 8, self.mock_hyph)
        # монгол → мон- / гол
        # 8 өргөндөө: ["энэ бол мон-"] дараа нь ["гол"]
        self.assertTrue(any("мон-" in line for line in result))
        self.assertTrue(any("гол" in line for line in result))

    # -----------------------------
    # format_by_type tests
    # -----------------------------
    def test_left_align(self):
        lines = [["Hello", "world"]]
        res = format_by_type(lines, 1, 15)
        self.assertEqual(res[0], "Hello world    ")

    def test_right_align(self):
        lines = [["Hello", "world"]]
        res = format_by_type(lines, 2, 15)
        self.assertEqual(res[0], "    Hello world")

    def test_center_align(self):
        lines = [["hi"]]
        res = format_by_type(lines, 3, 6)
        self.assertEqual(res[0], "  hi  ")

    def test_full_justify(self):
        lines = [["Hello", "world"]]
        res = format_by_type(lines, 4, 15)
        self.assertEqual(res[0], "Hello     world")


if __name__ == "__main__":
    unittest.main()
