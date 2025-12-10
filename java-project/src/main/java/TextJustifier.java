import java.io.*;
import java.nio.file.*;
import java.util.*;

public class TextJustifier {

    public static void main(String[] args) {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(System.in, "UTF-8"))) {
            println("БИЧВЭР ЖИГДЛЭГЧ");

            MAIN_LOOP:
            while (true) {
                println("\nМеню:");
                println("1) Текст оруулах (консол) \n2) Файлаас унших \n3) Гарах");
                int mainChoice = readIntWithPrompt(reader, "Сонголтоо оруулна уу (1-3): ", Arrays.asList(1,2,3,4));

                if (mainChoice == 4) {
                    println("Програмыг дуусгаж байна!");
                    break;
                }

                String text = "";
                if (mainChoice == 1) {
                    println("Текстээ оруулна уу. Дуусгахдаа шинэ мөрөнд зөвхөн END гэж бичээд Enter дарна.");
                    StringBuilder sb = new StringBuilder();
                    while (true) {
                        String line = reader.readLine();
                        if (line == null) break; // EOF
                        if ("END".equals(line.trim())) break;
                        if (sb.length() > 0) sb.append(' ');
                        sb.append(line.trim());
                    }
                    text = sb.toString().trim();
                } else if (mainChoice == 2) {
                    while (true) {
                        print("Файлын зам оруулна уу: ");
                        String path = reader.readLine();
                        if (path == null) break;
                        path = path.trim();
                        if (path.isEmpty()) { println("Файлын зам хоосон байна. Дахин оруулна уу."); continue; }
                        try {
                            byte[] bytes = Files.readAllBytes(Paths.get(path));
                            text = new String(bytes, "UTF-8").trim();
                            break;
                        } catch (IOException ioe) {
                            println("Файлыг уншихад алдаа гарлаа: " + ioe.getMessage());
                            println("Дахин оролт оруулна уу эсвэл буцахын тулд 'back' гэж бичнэ үү.");
                            String opt = reader.readLine();
                            if (opt != null && opt.trim().equalsIgnoreCase("back")) break;
                        }
                    }
                }

                if (text == null || text.isEmpty()) {
                    println("Текст оруулаагүй байна. Гэхдээ цэс рүү буцаж байна.");
                    continue;
                }

                println("\nАлгоритм сонгох:\n1) Greedy\n2) Dynamic Programming (DP)\n3) Эхлээд DP, дараа Greedy-ийг ажиллуулж харьцуулах\n4) Буцах");
                int algoChoice = readIntWithPrompt(reader, "Сонголт (1-4): ", Arrays.asList(1,2,3,4));
                if (algoChoice == 4) continue;

                println("\nЖигдлэх төрөл:\n1) Зүүн талдаа\n2) Баруун талдаа\n3) Хоёр талдаа (Full)");
                int justType = readIntWithPrompt(reader, "Сонголт (1-3): ", Arrays.asList(1,2,3));

                int maxWidth;
                while (true) {
                    print("\nМөрийн хамгийн их өргөнийг оруулна уу (тоду: 10 - 200): ");
                    String w = reader.readLine();
                    try {
                        maxWidth = Integer.parseInt(w.trim());
                        if (maxWidth < 1) { println("Өргөн 1-с их байх ёстой."); continue; }
                        break;
                    } catch (Exception e) { println("Буруу тоо. Дахин оруулна уу."); }
                }

                List<String> words = splitWords(text);

                if (algoChoice == 1) {
                    long t0 = System.nanoTime();
                    List<List<String>> gLines = greedyBreak(words, maxWidth);
                    long t1 = System.nanoTime();
                    List<String> out = formatByType(gLines, justType, maxWidth);
                    println("\n--- Greedy үр дүн (цаг: " + formatMs(t1 - t0) + ") ---");
                    printLines(out);
                } else if (algoChoice == 2) {
                    long t0 = System.nanoTime();
                    List<List<String>> dpLines = dpBreak(words, maxWidth);
                    long t1 = System.nanoTime();
                    List<String> out = formatByType(dpLines, justType, maxWidth);
                    println("\n--- Dynamic Programming үр дүн (цаг: " + formatMs(t1 - t0) + ") ---");
                    printLines(out);
                } else {
                    long t0 = System.nanoTime();
                    List<List<String>> dpLines = dpBreak(words, maxWidth);
                    long t1 = System.nanoTime();

                    long t2 = System.nanoTime();
                    List<List<String>> gLines = greedyBreak(words, maxWidth);
                    long t3 = System.nanoTime();

                    List<String> dpOut = formatByType(dpLines, justType, maxWidth);
                    List<String> gOut = formatByType(gLines, justType, maxWidth);

                    println("\n--- Dynamic Programming үр дүн (цаг: " + formatMs(t1 - t0) + ") ---");
                    printLines(dpOut);
                    println("\n--- Greedy үр дүн (цаг: " + formatMs(t3 - t2) + ") ---");
                    printLines(gOut);

                    if ((t1 - t0) < (t3 - t2)) println("\nХарьцуулалт: DP нь Greedy-ээс түргэн ажиллалаа.");
                    else if ((t3 - t2) < (t1 - t0)) println("\nХарьцуулалт: Greedy нь DP-ээс түргэн ажиллалаа.");
                    else println("\nХарьцуулалт: Аль аль нь ойролцоогоор адил хурдтай байлаа.");
                }

                println("\nҮр дүнг харлаа. Цэс рүү буцах уу? (y/n): ");
                String again = reader.readLine();
                if (again == null || !again.trim().equalsIgnoreCase("y")) {
                    println("Програмыг дуусгаж байна. Баярлалаа!");
                    break MAIN_LOOP;
                }
            }

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void println(String s) { System.out.println(s); }
    private static void print(String s) { System.out.print(s); }

    static int readIntWithPrompt(BufferedReader reader, String prompt, List<Integer> valid) throws IOException {
        while (true) {
            print(prompt);
            String line = reader.readLine();
            if (line == null) throw new IOException("No input");
            try {
                int v = Integer.parseInt(line.trim());
                if (valid == null || valid.contains(v)) return v;
                println("Буруу сонголт. Дахин оролт оруулна уу.");
            } catch (NumberFormatException e) {
                println("Тоог зөв оруулна уу.");
            }
        }
    }

    static List<String> splitWords(String text) {
        String[] arr = text.split("\\s+");
        List<String> out = new ArrayList<>();
        for (String s : arr) if (!s.isEmpty()) out.add(s);
        return out;
    }

    static List<List<String>> greedyBreak(List<String> words, int width) {
        List<List<String>> lines = new ArrayList<>();
        int i = 0;
        while (i < words.size()) {
            List<String> line = new ArrayList<>();
            int len = 0;
            while (i < words.size()) {
                String w = words.get(i);
                if (line.isEmpty()) {
                    line.add(w);
                    len = w.length();
                    i++;
                    if (len > width) break;
                } else {
                    if (len + 1 + w.length() <= width) {
                        len += 1 + w.length();
                        line.add(w);
                        i++;
                    } else break;
                }
            }
            lines.add(line);
        }
        return lines;
    }

    static List<List<String>> dpBreak(List<String> words, int width) {
        int n = words.size();
        long INF = Long.MAX_VALUE / 4;
        long[] dp = new long[n + 1];
        int[] next = new int[n + 1];
        Arrays.fill(dp, INF);
        Arrays.fill(next, -1);
        dp[n] = 0;

        for (int i = n - 1; i >= 0; i--) {
            long best = INF;
            int bestJ = -1;
            int len = 0;
            for (int j = i; j < n; j++) {
                if (j == i) len = words.get(j).length(); else len += 1 + words.get(j).length();
                if (j == i && len > width) {
                    long cost = 0;
                    if (dp[j + 1] != INF && dp[j + 1] + cost < best) {
                        best = dp[j + 1] + cost; bestJ = j + 1;
                    }
                    break;
                }
                if (len > width) break;
                long cost = (j == n - 1) ? 0 : (long)(width - len) * (width - len) * (width - len);
                if (dp[j + 1] != INF && dp[j + 1] + cost < best) {
                    best = dp[j + 1] + cost; bestJ = j + 1;
                }
            }
            dp[i] = best; next[i] = bestJ;
        }

        List<List<String>> lines = new ArrayList<>();
        int i = 0;
        while (i < n) {
            int j = next[i];
            if (j <= i || j == -1) {
                lines.addAll(greedyBreak(words.subList(i, n), width));
                break;
            }
            lines.add(new ArrayList<>(words.subList(i, j)));
            i = j;
        }
        return lines;
    }

    static List<String> formatByType(List<List<String>> lines, int justType, int width) {
        if (justType == 1) return leftAlign(lines, width);
        if (justType == 2) return rightAlign(lines, width);
        return fullJustify(lines, width);
    }

    static List<String> leftAlign(List<List<String>> lines, int width) {
        List<String> out = new ArrayList<>();
        for (List<String> line : lines) {
            String s = String.join(" ", line);
            if (s.length() < width) s += repeat(' ', width - s.length());
            out.add(s);
        }
        return out;
    }

    static List<String> rightAlign(List<List<String>> lines, int width) {
        List<String> out = new ArrayList<>();
        for (List<String> line : lines) {
            String s = String.join(" ", line);
            if (s.length() < width) s = repeat(' ', width - s.length()) + s;
            out.add(s);
        }
        return out;
    }

    static List<String> fullJustify(List<List<String>> lines, int width) {
        List<String> out = new ArrayList<>();
        for (int idx = 0; idx < lines.size(); idx++) {
            List<String> line = lines.get(idx);
            boolean isLast = (idx == lines.size() - 1);
            if (line.size() == 0) { out.add(repeat(' ', width)); continue; }
            if (line.size() == 1 || isLast) {
                String s = String.join(" ", line);
                if (s.length() < width) s += repeat(' ', width - s.length());
                out.add(s); continue;
            }
            int wordsLen = 0; for (String w : line) wordsLen += w.length();
            int totalSpaces = width - wordsLen; int gaps = line.size() - 1;
            int base = totalSpaces / gaps; int extra = totalSpaces % gaps;
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < line.size(); i++) {
                sb.append(line.get(i));
                if (i < gaps) sb.append(repeat(' ', base + (i < extra ? 1 : 0)));
            }
            out.add(sb.toString());
        }
        return out;
    }

    static void printLines(List<String> lines) {
        for (String l : lines) System.out.println(l);
    }

    static String repeat(char c, int n) {
        if (n <= 0) return ""; char[] a = new char[n]; Arrays.fill(a, c); return new String(a);
    }

    static String formatMs(long ns) {
        return String.format("%.3f ms", ns / 1_000_000.0);
    }
}
