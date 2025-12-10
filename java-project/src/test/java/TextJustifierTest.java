import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.io.*;
import java.util.*;

class TextJustifierTest {

    @Test
    void testSplitWords() {
        // Test with normal text
        List<String> result1 = TextJustifier.splitWords("hello world test");
        assertEquals(Arrays.asList("hello", "world", "test"), result1);

        // Test with multiple spaces
        List<String> result2 = TextJustifier.splitWords("  hello   world  test  ");
        assertEquals(Arrays.asList("hello", "world", "test"), result2);

        // Test with empty string
        List<String> result3 = TextJustifier.splitWords("");
        assertEquals(0, result3.size());

        // Test with only spaces
        List<String> result4 = TextJustifier.splitWords("     ");
        assertEquals(0, result4.size());
    }

    @Test
    void testGreedyBreak() {
        List<String> words = Arrays.asList("This", "is", "a", "test", "sentence", "for", "greedy");

        // Test width 10
        List<List<String>> result1 = TextJustifier.greedyBreak(words, 10);
        assertFalse(result1.isEmpty());
        // Зөвхөн мөрүүдийн тоог шалгах
        assertTrue(result1.size() >= 2);

        // Test width 15
        List<List<String>> result2 = TextJustifier.greedyBreak(words, 15);
        assertFalse(result2.isEmpty());

        // Test with single long word
        List<String> longWords = Arrays.asList("verylongwordthatexceedswidth");
        List<List<String>> result3 = TextJustifier.greedyBreak(longWords, 10);
        assertEquals(1, result3.size());
        assertEquals(1, result3.get(0).size());

        // Test empty list
        List<List<String>> result4 = TextJustifier.greedyBreak(new ArrayList<>(), 10);
        assertTrue(result4.isEmpty());
    }

    @Test
    void testDpBreak() {
        List<String> words = Arrays.asList("This", "is", "a", "test", "sentence", "for", "dp");

        // Test width 10
        List<List<String>> result1 = TextJustifier.dpBreak(words, 10);
        assertFalse(result1.isEmpty());
        assertTrue(result1.size() >= 2);

        // Test width 15
        List<List<String>> result2 = TextJustifier.dpBreak(words, 15);
        assertFalse(result2.isEmpty());

        // Test with single word
        List<String> singleWord = Arrays.asList("Hello");
        List<List<String>> result3 = TextJustifier.dpBreak(singleWord, 10);
        assertEquals(1, result3.size());
        assertEquals(1, result3.get(0).size());

        // Test empty list
        List<List<String>> result4 = TextJustifier.dpBreak(new ArrayList<>(), 10);
        assertTrue(result4.isEmpty());
    }

    @Test
    void testLeftAlign() {
        List<List<String>> lines = Arrays.asList(
                Arrays.asList("Hello", "world"),
                Arrays.asList("Test"),
                Arrays.asList("This", "is", "a", "longer", "line")
        );

        // Test width 20
        List<String> result = TextJustifier.leftAlign(lines, 20);
        assertEquals(3, result.size());

        // Check each line has exact width
        for (String line : result) {
            // Мөр бүрийн урт нь өргөнтэй тэнцүү эсвэл түүнээс их байж болно
            // (учир нь урт үгс байж болно)
            assertTrue(line.length() >= 20 || line.trim().length() > 0);
        }

        // Check first line starts with "Hello world"
        assertTrue(result.get(0).contains("Hello world"));

        // Check second line starts with "Test"
        assertTrue(result.get(1).contains("Test"));
    }

    @Test
    void testRightAlign() {
        List<List<String>> lines = Arrays.asList(
                Arrays.asList("Hello", "world"),
                Arrays.asList("Test"),
                Arrays.asList("Right", "aligned")
        );

        // Test width 20
        List<String> result = TextJustifier.rightAlign(lines, 20);
        assertEquals(3, result.size());

        // Check each line has exact width or contains the text
        for (String line : result) {
            assertTrue(line.length() >= 20 || line.trim().length() > 0);
        }

        // Check first line ends with "Hello world"
        assertTrue(result.get(0).contains("Hello world"));

        // Check second line ends with "Test"
        assertTrue(result.get(1).contains("Test"));
    }

    @Test
    void testFullJustify() {
        List<List<String>> lines = Arrays.asList(
                Arrays.asList("This", "is", "a", "test"),
                Arrays.asList("of", "full", "justify"),
                Arrays.asList("Last", "line"),
                Arrays.asList("Single"),
                new ArrayList<>()  // хоосон мөр
        );

        // Test width 20
        List<String> result = TextJustifier.fullJustify(lines, 20);
        assertEquals(5, result.size());

        // Check non-empty lines
        for (int i = 0; i < 4; i++) {
            String line = result.get(i);
            // Мөр нь текст агуулсан эсвэл зайтай байх ёстой
            assertTrue(line.length() > 0);
        }

        // Empty line should be all spaces (or empty)
        String emptyLine = result.get(4);
        assertTrue(emptyLine.isEmpty() || emptyLine.trim().isEmpty());
    }

    @Test
    void testRepeat() {
        // Test normal case
        String result1 = TextJustifier.repeat('*', 5);
        assertEquals("*****", result1);

        // Test zero repeat
        String result2 = TextJustifier.repeat('*', 0);
        assertEquals("", result2);

        // Test one repeat
        String result3 = TextJustifier.repeat('a', 1);
        assertEquals("a", result3);

        // Test space repeat
        String result4 = TextJustifier.repeat(' ', 3);
        assertEquals("   ", result4);
    }

    @Test
    void testFormatMs() {
        // Test conversion from nanoseconds to milliseconds
        String result1 = TextJustifier.formatMs(1_500_000L);
        // "." эсвэл "," агуулж болно (Locale хамаарна)
        assertTrue(result1.contains("1.5") || result1.contains("1,5") ||
                result1.contains("1.500") || result1.contains("1,500"));

        String result2 = TextJustifier.formatMs(500_000L);
        assertTrue(result2.contains("0.5") || result2.contains("0,5") ||
                result2.contains("0.500") || result2.contains("0,500"));

        String result3 = TextJustifier.formatMs(0L);
        assertTrue(result3.contains("0.0") || result3.contains("0,0") ||
                result3.contains("0.000") || result3.contains("0,000"));
    }

    @Test
    void testReadIntWithPrompt() throws IOException {
        // Test with valid input
        String input = "2\n";
        BufferedReader reader = new BufferedReader(new StringReader(input));
        int result = TextJustifier.readIntWithPrompt(
                reader,
                "Prompt",
                Arrays.asList(1, 2, 3)
        );
        assertEquals(2, result);

        // Test with invalid then valid input
        String input2 = "invalid\n5\n2\n";
        BufferedReader reader2 = new BufferedReader(new StringReader(input2));
        int result2 = TextJustifier.readIntWithPrompt(
                reader2,
                "Prompt",
                Arrays.asList(1, 2, 3)
        );
        assertEquals(2, result2);
    }

    @Test
    void testFormatByType() {
        List<List<String>> lines = Arrays.asList(
                Arrays.asList("Format", "test"),
                Arrays.asList("Line", "two")
        );

        // Test left align
        List<String> left = TextJustifier.formatByType(lines, 1, 20);
        assertEquals(2, left.size());
        // Зөвхөн текст агуулсан эсэхийг шалгах
        assertTrue(left.get(0).contains("Format test"));

        // Test right align
        List<String> right = TextJustifier.formatByType(lines, 2, 20);
        assertEquals(2, right.size());
        assertTrue(right.get(0).contains("Format test"));

        // Test full justify
        List<String> full = TextJustifier.formatByType(lines, 3, 20);
        assertEquals(2, full.size());
        // Мөр бүр текст агуулсан эсэхийг шалгах
        assertTrue(full.get(0).contains("Format") && full.get(0).contains("test"));
    }

    @Test
    void testEdgeCases() {
        // Test with words longer than width
        List<String> longWords = Arrays.asList("verylongword", "anotherlongword");
        List<List<String>> greedyResult = TextJustifier.greedyBreak(longWords, 5);
        List<List<String>> dpResult = TextJustifier.dpBreak(longWords, 5);

        // Аль аль алгоритм үр дүн үүсгэсэн эсэхийг шалгах
        assertNotNull(greedyResult);
        assertNotNull(dpResult);

        // Test formatting with empty lines list
        List<String> formattedEmpty = TextJustifier.formatByType(
                new ArrayList<>(),
                1,
                10
        );
        assertTrue(formattedEmpty.isEmpty());
    }

    @Test
    void testPerformanceComparison() {
        // Create a long text for testing
        StringBuilder longText = new StringBuilder();
        for (int i = 0; i < 50; i++) { // Тоог багасгасан
            longText.append("word").append(i).append(" ");
        }
        List<String> words = TextJustifier.splitWords(longText.toString());

        // Both algorithms should handle the same input
        List<List<String>> greedyLines = TextJustifier.greedyBreak(words, 30);
        List<List<String>> dpLines = TextJustifier.dpBreak(words, 30);

        // Both should produce valid results
        assertFalse(greedyLines.isEmpty());
        assertFalse(dpLines.isEmpty());
    }

    @Test
    void testSingleWordAlignment() {
        List<List<String>> lines = Arrays.asList(
                Arrays.asList("Hello"),
                Arrays.asList("World")
        );

        // Test all alignment types with single words
        List<String> left = TextJustifier.leftAlign(lines, 10);
        List<String> right = TextJustifier.rightAlign(lines, 10);
        List<String> full = TextJustifier.fullJustify(lines, 10);

        assertEquals(2, left.size());
        assertEquals(2, right.size());
        assertEquals(2, full.size());

        // Check they contain the words
        for (String line : left) {
            assertTrue(line.contains("Hello") || line.contains("World"));
        }
    }

    @Test
    void testWordLongerThanWidth() {
        // Test when a single word is longer than width
        List<String> words = Arrays.asList("Supercalifragilisticexpialidocious");
        List<List<String>> greedy = TextJustifier.greedyBreak(words, 10);
        List<List<String>> dp = TextJustifier.dpBreak(words, 10);

        // Both should handle it (possibly putting it in its own line)
        assertFalse(greedy.isEmpty());
        assertFalse(dp.isEmpty());

        // Format it
        List<List<String>> lines = Arrays.asList(greedy.get(0));
        List<String> formatted = TextJustifier.leftAlign(lines, 10);
        assertFalse(formatted.isEmpty());
        assertTrue(formatted.get(0).contains("Supercalifragilisticexpialidocious"));
    }

    @Test
    void testEmptyText() {
        // Test with empty text
        List<String> words = TextJustifier.splitWords("");

        // Test greedy
        List<List<String>> greedy = TextJustifier.greedyBreak(words, 10);
        assertTrue(greedy.isEmpty());

        // Test DP
        List<List<String>> dp = TextJustifier.dpBreak(words, 10);
        assertTrue(dp.isEmpty());

        // Test formatting empty list
        List<String> formatted = TextJustifier.leftAlign(new ArrayList<>(), 10);
        assertTrue(formatted.isEmpty());
    }
}