import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import biydaalt2 as bd


class TestTextJustifier(unittest.TestCase):

    def setUp(self):
        self.mock_hyph = MagicMock()
        self.mock_hyph.hyphenate.side_effect = lambda w: [3] if w == "монгол" else []

    def test_split_words(self):
        self.assertEqual(bd.split_words("Сайн байна уу"), ["Сайн", "байна", "уу"])
        self.assertEqual(bd.split_words(""), [])

    def test_justify_line(self):
        self.assertEqual(bd.justify_line(["Hello"], 10), "Hello     ")
        self.assertEqual(bd.justify_line(["Hello", "world"], 15), "Hello     world")

    def test_greedy_break(self):
        words = ["a", "bb", "ccc"]
        lines = bd.greedy_break(words, 4)
        self.assertEqual(lines, [["a", "bb"], ["ccc"]])

    def test_dp_break(self):
        words = ["aaa", "bb", "c"]
        lines = bd.dp_break(words, 5)
        self.assertIsInstance(lines, list)
        self.assertTrue(len(lines) >= 1)

    def test_greedy_hyphenation(self):
        words = ["энэ", "бол", "монгол"]
        result = bd.greedy_justify_with_hyphenation(words, 8, self.mock_hyph)
        self.assertIsInstance(result, list)

    def test_format_by_type(self):
        lines = [["Hello", "world"]]

        result = bd.format_by_type(lines, 1, 15, False, None)
        self.assertEqual(result[0], "Hello world    ")

        result = bd.format_by_type(lines, 2, 15, False, None)
        self.assertEqual(result[0], "    Hello world")

        result = bd.format_by_type(lines, 4, 15, False, None)
        self.assertIn("Hello", result[0])
        self.assertIn("world", result[0])

    @patch('pyphen.Pyphen')
    def test_mongolian_class(self, mock_pyphen):
        mock_instance = MagicMock()
        mock_instance.inserted.return_value = "мон-гол"
        mock_pyphen.return_value = mock_instance

        m = bd.Mongolian()
        cuts = m.hyphenate("монгол")
        self.assertEqual(cuts, [3])


class TestIntegration(unittest.TestCase):

    def test_full_pipeline(self):
        text = "Монгол хэл бол Монгол улсын албан ёсны хэл юм"
        words = bd.split_words(text)

        greedy_lines = bd.greedy_break(words, 20)
        self.assertGreater(len(greedy_lines), 0)

        formatted = bd.format_by_type(greedy_lines, 1, 20, False, None)
        self.assertEqual(len(formatted), len(greedy_lines))


if __name__ == '__main__':
    unittest.main(verbosity=2)