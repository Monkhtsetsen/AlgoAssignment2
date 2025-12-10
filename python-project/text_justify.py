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
        self.assertEqual(
            bd.split_words("Сайн байна уу"),
            ["Сайн", "байна", "уу"]
        )
        self.assertEqual(
            bd.split_words("Hello   world  from   Python"),
            ["Hello", "world", "from", "Python"]
        )
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
        self.assertGreaterEqual(len(lines), 1)
        for line in lines:
            line_str = " ".join(line)
            self.assertLessEqual(len(line_str), 5)


    def test_greedy_hyphenation(self):
        words = ["энэ", "бол", "монгол"]
        result = bd.greedy_justify_with_hyphenation(words, 8, self.mock_hyph)
        self.assertIsInstance(result, list)
        for line in result:
            self.assertIsInstance(line, str)

    def test_format_by_type(self):
        lines = [["Hello", "world"]]
        width = 15

        # Left align
        result = bd.format_by_type(lines, 1, width, False, None)
        self.assertEqual(result[0], "Hello world    ")

        # Right align
        result = bd.format_by_type(lines, 2, width, False, None)
        self.assertEqual(result[0], "    Hello world")

        # Full justify (хоёр талд)
        result = bd.format_by_type(lines, 4, width, False, None)
        self.assertIn("Hello", result[0])
        self.assertIn("world", result[0])
        self.assertEqual(len(result[0]), width)

    @patch("pyphen.Pyphen")
    def test_mongolian_class_hyphenate(self, mock_pyphen):
        """
        Mongolian (эсвэл MultiLangHyphenator wrapper) Pyphen-ийг зөв дуудаж,
        inserted() дээр үндэслээд зөв индекс буцааж байгааг шалгана.
        """
        mock_instance = MagicMock()
        # "мон-гол" -> '-' байрлалын индекс 3 гэж үзнэ
        mock_instance.inserted.return_value = "мон-гол"
        mock_pyphen.return_value = mock_instance

        # Хэрвээ чи Mongolian wrapper-тай бол:
        if hasattr(bd, "Mongolian"):
            h = bd.Mongolian()
        else:
            h = bd.MultiLangHyphenator()

        cuts = h.hyphenate("монгол")
        self.assertEqual(cuts, [3])
        mock_instance.inserted.assert_called_with("монгол")

    def test_detect_lang_in_multilang_hyphenator(self):
        """
        MultiLangHyphenator.detect_lang() логик зөв ажиллаж байгаа эсэх.
        """
        # Dic-үүд нь энд хэрэггүй тул жоохон hack – объект үүсгэчихээд detect_lang-ийг л ашиглая.
        # Хэрвээ init дотор pyphen.Pyphen унаж байвал энэ тест дээр patch хийж болох байсан ч
        # ихэнх орчинд асуудалгүй.
        try:
            h = bd.MultiLangHyphenator()
        except Exception:
            # Хэрвээ dict байхгүйгээс болж init унавал dummy class хийж болох ч
            # ихэнх тохиолдолд dict байгаа гэж үзье.
            self.skipTest("MultiLangHyphenator init failed (dictionary not available).")

        self.assertEqual(h.detect_lang("монгол"), "mn")
        self.assertEqual(h.detect_lang("English"), "en")
        # Mixed → default нь mn
        self.assertEqual(h.detect_lang("монgol"), "mn")
        self.assertEqual(h.detect_lang("1234"), "mn")

class TestIntegration(unittest.TestCase):
    def test_full_pipeline_greedy_left(self):
        """
        Full pipeline:
          text -> split_words -> greedy_break -> format_by_type
        """
        text = "Монгол хэл бол Монгол улсын албан ёсны хэл юм"
        words = bd.split_words(text)

        greedy_lines = bd.greedy_break(words, 20)
        self.assertGreater(len(greedy_lines), 0)

        formatted = bd.format_by_type(greedy_lines, 1, 20, False, None)
        self.assertEqual(len(formatted), len(greedy_lines))
        for line in formatted:
            self.assertEqual(len(line), 20)

    def test_full_pipeline_dp_full_justify(self):
        """
        DP + full justify (-гүй хувилбар).
        """
        text = "This is an English sentence that should be wrapped nicely."
        words = bd.split_words(text)

        dp_lines = bd.dp_break(words, 25)
        self.assertGreater(len(dp_lines), 0)

        formatted = bd.format_by_type(dp_lines, 4, 25, False, None)
        for line in formatted[:-1]:  # сүүлийн мөрөнд бага зэрэг хоосон зай байж болно
            self.assertEqual(len(line), 25)


if __name__ == '__main__':
    unittest.main(verbosity=2)
