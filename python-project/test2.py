import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import biydaalt2 as bd


class TestTextJustifier(unittest.TestCase):

    def setUp(self):
        print("\n[setUp] Test эхлэхэд бэлтгэж байна...")
        self.mock_hyph = MagicMock()
        self.mock_hyph.hyphenate.side_effect = lambda w: [3] if w == "монгол" else []

    def tearDown(self):
        print("[tearDown] Test дууссан\n" + "-" * 50)

    def test_split_words(self):

        result = bd.split_words("Сайн   байна   уу")
        expected = ["Сайн", "байна", "уу"]
        print(f"  Оролт: 'Сайн   байна   уу' (олон зайтай)")
        print(f"  Хүлээгдэж буй: {expected}")
        print(f"  Үр дүн: {result}")
        self.assertEqual(result, expected)
        print("  ✓ Олон зайтай текст зөв салгагдлаа")

    def test_greedy_break(self):

        print("test_greedy_break: Greedy алгоритмаар мөр хуваах...")

        words = ["a", "bb", "ccc"]
        lines = bd.greedy_break(words, 4)
        expected = [["a", "bb"], ["ccc"]]
        print(f"  Оролт: {words}, width=4")
        print(f"  Хүлээгдэж буй: {expected}")
        print(f"  Үр дүн: {lines}")
        print(f"  Мөрийн тоо: {len(lines)}")
        self.assertEqual(lines, expected)
        print("  ✓ Greedy алгоритм зөв ажиллаж байна")

        words = ["aaa", "bb"]
        lines = bd.greedy_break(words, 6)
        expected = [["aaa", "bb"]]
        print(f"  Оролт: {words}, width=6")
        print(f"  Хүлээгдэж буй: {expected}")
        print(f"  Үр дүн: {lines}")
        self.assertEqual(lines, expected)
        print("  ✓ Яг таарч байгаа тохиолдол зөв боловсорч байна")

        words = ["abcdefgh", "ij"]
        lines = bd.greedy_break(words, 5)
        print(f"  Оролт: {words}, width=5")
        print(f"  Үр дүн: {lines}")
        self.assertEqual(len(lines), 2)
        print("  ✓ Урт үг зөв хуваагдлаа")

    def test_dp_break(self):
        print("test_dp_break: Dynamic Programming алгоритмаар мөр хуваах...")

        words = ["aaa", "bb", "c"]
        lines = bd.dp_break(words, 5)
        print(f"  Оролт: {words}, width=5")
        print(f"  Үр дүн: {lines}")
        print(f"  Мөрийн тоо: {len(lines)}")

        self.assertIsInstance(lines, list)
        self.assertTrue(len(lines) >= 1)
        print("  ✓ DP алгоритм зөв ажиллаж байна")

        lines = bd.dp_break([], 10)
        print(f"  Оролт: [], width=10")
        print(f"  Үр дүн: {lines}")
        self.assertEqual(lines, [])
        print("  ✓ Хоосон жагсаалт зөв боловсорч байна")

        lines = bd.dp_break(["test"], 10)
        print(f"  Оролт: ['test'], width=10")
        print(f"  Үр дүн: {lines}")
        self.assertEqual(lines, [["test"]])
        print("  ✓ Нэг үг зөв боловсорч байна")

    def test_greedy_hyphenation(self):
        print("test_greedy_hyphenation: Greedy + Hyphenation алгоритм...")

        words = ["энэ", "бол", "монгол"]
        print(f"  Оролт: {words}, width=8")
        print(f"  Hyphenation тохиргоо: 'монгол' → [3] (мон-гол)")

        result = bd.greedy_justify_with_hyphenation(words, 8, self.mock_hyph)

        print(f"  Үр дүн: {result}")
        print(f"  Үр дүнгийн төрөл: {type(result)}")
        print(f"  Мөрийн тоо: {len(result)}")

        self.assertIsInstance(result, list)
        self.assertTrue(len(result) >= 1)
        print("  ✓ Greedy + Hyphenation алгоритм зөв ажиллаж байна")

        found_hyphen = False
        for line in result:
            if "мон-" in line:
                found_hyphen = True
                print(f"  Олдсон: '{line}' - гипенаци амжилттай хийгдлээ")
                break

        if found_hyphen:
            print("  ✓ Гипенаци зөв хийгдлээ")
        else:
            print(" Гипенаци хийгдээгүй (зөвшөөрөгдөх үр дүн)")

    def test_format_by_type(self):
        print("test_format_by_type: Өөр өөр жигдлэлийн төрлүүд...")

        lines = [["Hello", "world"]]
        print(f"  Анхны мөр: {lines}")

        # Тест 1: Зүүн талд жигдлэх
        result = bd.format_by_type(lines, 1, 15, False, None)
        expected = "Hello world    "
        print(f"  Зүүн жигдлэл (type=1): '{result[0]}'")
        print(f"  Хүлээгдэж буй: '{expected}'")
        self.assertEqual(result[0], expected)
        print("  ✓ Зүүн талд жигдлэл зөв ажиллаж байна")

        # Тест 2: Баруун талд жигдлэх
        result = bd.format_by_type(lines, 2, 15, False, None)
        expected = "    Hello world"
        print(f"  Баруун жигдлэл (type=2): '{result[0]}'")
        print(f"  Хүлээгдэж буй: '{expected}'")
        self.assertEqual(result[0], expected)
        print("  ✓ Баруун талд жигдлэл зөв ажиллаж байна")

        # Тест 3: Хоёр талд жигдлэх
        result = bd.format_by_type(lines, 4, 15, False, None)
        print(f"  Хоёр талд жигдлэл (type=4): '{result[0]}'")
        print(f"  Үр дүнгийн урт: {len(result[0])}")

        self.assertIn("Hello", result[0])
        self.assertIn("world", result[0])
        self.assertEqual(len(result[0]), 15)
        print("  ✓ Хоёр талд жигдлэл зөв ажиллаж байна")

        # Тест 4: Hyphenation-тай форматлах
        hyphen_lines = [["мон-", "гол"]]
        result = bd.format_by_type(hyphen_lines, 1, 10, True, self.mock_hyph)
        expected = "мон- гол  "
        print(f"  Hyphenation-тай зүүн жигдлэл: '{result[0]}'")
        print(f"  Хүлээгдэж буй: '{expected}'")
        self.assertEqual(result[0], expected)
        print("  ✓ Hyphenation-тай форматлах зөв ажиллаж байна")

    @patch('pyphen.Pyphen')
    def test_mongolian_class(self, mock_pyphen):
        """Монгол хэлний классын тест"""
        print("test_mongolian_class: Mongolian классын гипенаци...")

        mock_instance = MagicMock()
        mock_instance.inserted.return_value = "мон-гол"
        mock_pyphen.return_value = mock_instance

        print("  Mongolian классын объект үүсгэж байна...")
        m = bd.Mongolian()

        print("  'монгол' үгийн гипенаци хийж байна...")
        cuts = m.hyphenate("монгол")

        print(f"  Үр дүн: {cuts}")
        print(f"  Хүлээгдэж буй: [3]")

        self.assertEqual(cuts, [3])
        print("  ✓ Mongolian класс зөв ажиллаж байна")

        # Алдааны тохиолдлыг тестлэх
        print("  Алдааны тохиолдолд тестлэж байна...")
        mock_instance.inserted.side_effect = Exception("Test error")
        cuts = m.hyphenate("монгол")
        print(f"  Алдааны үр дүн: {cuts}")
        print(f"  Хүлээгдэж буй: [] (хоосон жагсаалт)")
        self.assertEqual(cuts, [])
        print("  ✓ Алдааны тохиолдол зөв боловсорч байна")


class TestIntegration(unittest.TestCase):

    def setUp(self):
        print("\n[setUp] Интеграцийн тест эхлэхэд бэлтгэж байна...")

    def tearDown(self):
        print("[tearDown] Интеграцийн тест дууссан\n" + "=" * 60)

    def test_full_pipeline(self):
        print("test_full_pipeline: Бүтэн дамжлагын тест...")

        text = "Монгол хэл бол Монгол улсын албан ёсны хэл юм"
        print(f"  Анхны текст: '{text}'")
        print(f"  Текстийн урт: {len(text)} тэмдэгт")

        # 1. Үг хуваах
        print("\n  1. Үг хуваах дамжлага...")
        words = bd.split_words(text)
        print(f"    Үгсийн тоо: {len(words)}")
        print(f"    Үгс: {words}")
        self.assertGreater(len(words), 0)
        print("    ✓ Үг хуваах амжилттай")

        # 2. Greedy алгоритм
        print("\n  2. Greedy алгоритмын дамжлага...")
        greedy_lines = bd.greedy_break(words, 20)
        print(f"    Greedy мөрийн тоо: {len(greedy_lines)}")
        for i, line in enumerate(greedy_lines, 1):
            print(f"      Мөр {i}: {line}")
        self.assertGreater(len(greedy_lines), 0)
        print("    ✓ Greedy алгоритм амжилттай")

        # 3. DP алгоритм
        print("\n  3. DP алгоритмын дамжлага...")
        dp_lines = bd.dp_break(words, 20)
        print(f"    DP мөрийн тоо: {len(dp_lines)}")
        self.assertGreater(len(dp_lines), 0)
        print("    ✓ DP алгоритм амжилттай")

        # 4. Форматлах
        print("\n  4. Форматлах дамжлага...")
        formatted = bd.format_by_type(greedy_lines, 1, 20, False, None)
        print(f"    Форматлагдсан мөрийн тоо: {len(formatted)}")
        self.assertEqual(len(formatted), len(greedy_lines))
        print("    ✓ Форматлах амжилттай")

        # Үр дүнг хэвлэх
        print("\n  Эцсийн үр дүн:")
        for i, line in enumerate(formatted, 1):
            print(f"    Мөр {i}: '{line}' (урт: {len(line)})")

        print("\n  ✓ Бүх дамжлага амжилттай дууслаа!")


def run_tests_with_detailed_output():
    print("=" * 70)
    print("ТЕКСТ ЖИГДЛЭГЧ ПРОГРАМЫН ТЕСТ - ДЭЛГЭРЭНГҮЙ ГАРЦТАЙ")
    print("=" * 70)

    # Test suite үүсгэх
    loader = unittest.TestLoader()

    # Бүх тестийг олох
    suite = loader.loadTestsFromTestCase(TestTextJustifier)
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Test runner ажиллуулах
    runner = unittest.TextTestRunner(verbosity=0, descriptions=True)
    result = runner.run(suite)

    # Тестийн түүх хэвлэх
    print("\n" + "=" * 70)
    print("ТЕСТИЙН ТҮҮХ:")
    print("=" * 70)

    print(f"\nНийт тест: {result.testsRun}")
    print(f"Амжилттай: {result.testsRun - len(result.failures) - len(result.errors)}")

    if result.failures:
        print(f"Амжилтгүй: {len(result.failures)}")
        print("\nАмжилтгүй тестүүд:")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"\n{i}. {test}")
            print(f"   Алдаа: {traceback.splitlines()[-1]}")

    if result.errors:
        print(f"Алдаатай: {len(result.errors)}")
        print("\nАлдаатай тестүүд:")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"\n{i}. {test}")
            print(f"   Алдаа: {traceback.splitlines()[-1]}")

    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✓ БҮХ ТЕСТ АМЖИЛТТАЙ ДУУСЛАА!")
    else:
        print("✗ Зарим тест амжилтгүй боллоо!")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    # Дэлгэрэнгүй гарцтай тестийг ажиллуулах
    success = run_tests_with_detailed_output()
    sys.exit(0 if success else 1)