import pyphen
import math
import time
import sys
import os

class MultiLangHyphenator:
    def __init__(self):
        try:
            self.mn_dic = pyphen.Pyphen(filename='hyph_mn_MN.dic')
        except Exception as e:
            print(f"hyph_mn_MN.dic олдсонгүй: {e} -> lang='mn'")
            self.mn_dic = pyphen.Pyphen(lang='mn')

        try:
            self.en_dic = pyphen.Pyphen(filename='hyph_en_US.dic')
        except Exception as e:
            print(f"hyph_en_US.dic олдсонгүй: {e} -> lang='en_US'")
            try:
                self.en_dic = pyphen.Pyphen(lang='en_US')
            except Exception:
                print("English dictionary байхгүй, зөвхөн Mongolian ашиглана.")
                self.en_dic = None

    def detect_lang(self, word: str) -> str:
        has_cyr = any('\u0400' <= ch <= '\u04FF' for ch in word)
        has_lat = any(('A' <= ch <= 'Z') or ('a' <= ch <= 'z') for ch in word)
        if has_cyr and not has_lat:
            return 'mn'
        if has_lat and not has_cyr:
            return 'en'
        return 'mn'

    def hyphenate(self, word):
        try:
            dic = self.en_dic if self.detect_lang(word) == 'en' and self.en_dic else self.mn_dic
            inserted = dic.inserted(word)
            return [i for i, c in enumerate(inserted) if c == "-"]
        except Exception:
            return []

def split_words(text):
    return [w for w in text.split() if w]


def greedy_justify_with_hyphenation(words, width, hyph):
    result, line_words, current_len = [], [], 0
    for w in words:
        if current_len + len(w) + len(line_words) <= width:
            line_words.append(w)
            current_len += len(w)
        else:
            cuts = hyph.hyphenate(w)
            placed = False
            for c in reversed(cuts):
                left, right = w[:c] + "-", w[c:]
                if current_len + len(left) + len(line_words) <= width:
                    line_words.append(left)
                    result.append(justify_line(line_words, width))
                    line_words, current_len, placed = [right], len(right), True
                    break
            if not placed:
                result.append(justify_line(line_words, width))
                line_words, current_len = [w], len(w)
    if line_words:
        result.append(justify_line(line_words, width))
    return result


def greedy_break(words, width):
    lines, i = [], 0
    while i < len(words):
        line, length = [], 0
        while i < len(words):
            w = words[i]
            if not line:
                line.append(w)
                length = len(w)
                i += 1
                if length > width:
                    break
            elif length + 1 + len(w) <= width:
                length += 1 + len(w)
                line.append(w)
                i += 1
            else:
                break
        lines.append(line)
    return lines


def dp_justify_with_hyphenation(text, width):
    words = text.split()
    n = len(words)

    def badness(i, j):
        line_words = words[i:j]
        total_chars = sum(len(w) for w in line_words)
        spaces = j - i - 1
        length = total_chars + spaces
        if length > width:
            return math.inf
        return (width - length) ** 2

    dp = [math.inf] * (n + 1)
    nxt = [0] * (n + 1)
    dp[n] = 0

    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n + 1):
            cost = badness(i, j)
            if cost == math.inf:
                break
            if dp[j] + cost < dp[i]:
                dp[i] = dp[j] + cost
                nxt[i] = j

    lines, i = [], 0
    while i < n:
        j = nxt[i]
        lines.append(justify_line(words[i:j], width))
        i = j
    return lines


def dp_break(words, width):
    n = len(words)
    INF = float('inf')
    dp = [INF] * (n + 1)
    next_idx = [-1] * (n + 1)
    dp[n] = 0

    for i in range(n - 1, -1, -1):
        best, best_j, length = INF, -1, 0
        for j in range(i, n):
            length = len(words[j]) if j == i else length + 1 + len(words[j])
            if j == i and length > width:
                if dp[j + 1] != INF and dp[j + 1] < best:
                    best, best_j = dp[j + 1], j + 1
                break
            if length > width:
                break
            cost = 0 if j == n - 1 else (width - length) ** 3
            if dp[j + 1] != INF and dp[j + 1] + cost < best:
                best, best_j = dp[j + 1] + cost, j + 1
        dp[i], next_idx[i] = best, best_j

    lines, i = [], 0
    while i < n:
        j = next_idx[i]
        if j <= i or j == -1:
            lines.extend(greedy_break(words[i:], width))
            break
        lines.append(words[i:j])
        i = j
    return lines


def dp_with_hyphenation(words, width, hyph):
    n = len(words)
    INF = float('inf')
    dp = [INF] * (n + 1)
    next_idx = [-1] * (n + 1)
    line_contents = [None] * (n + 1)
    dp[n] = 0

    for i in range(n - 1, -1, -1):
        best_cost, best_j, best_line = INF, -1, None

        for j in range(i + 1, n + 1):
            line_words, current_len, valid_line = [], 0, True
            for k in range(i, j):
                word = words[k]
                if current_len + len(word) + (1 if line_words else 0) > width:
                    cuts = hyph.hyphenate(word)
                    hyphen_used = False
                    for c in reversed(cuts):
                        left_part, right_part = word[:c] + "-", word[c:]
                        if current_len + len(left_part) + (1 if line_words else 0) <= width:
                            line_words.append(left_part)
                            words.insert(k + 1, right_part)
                            n += 1
                            dp.append(INF)
                            next_idx.append(-1)
                            line_contents.append(None)
                            hyphen_used = True
                            break
                    if not hyphen_used:
                        valid_line = False
                        break
                else:
                    line_words.append(word)
                    current_len += len(word) + (1 if line_words else 0) - (0 if len(line_words) == 1 else 1)

            if not valid_line:
                break

            line_length = sum(len(w) for w in line_words) + max(0, len(line_words) - 1)
            if line_length > width:
                break

            cost = 0 if j == n else (width - line_length) ** 3
            if dp[j] != INF and dp[j] + cost < best_cost:
                best_cost, best_j, best_line = dp[j] + cost, j, line_words

        if best_j != -1:
            dp[i], next_idx[i], line_contents[i] = best_cost, best_j, best_line

    lines, i = [], 0
    while i < n:
        j = next_idx[i]
        if j <= i or j == -1:
            remaining = words[i:]
            greedy_result = greedy_justify_with_hyphenation(remaining, width, hyph)
            lines.extend([[w] if isinstance(w, str) else w for w in greedy_result])
            break
        if line_contents[i] is not None:
            lines.append(line_contents[i])
        i = j
    return lines


# ==================== FORMATTING ====================

def justify_line(words, width):
    if len(words) == 1:
        return words[0].ljust(width)
    total_chars = sum(len(w) for w in words)
    spaces_needed = width - total_chars
    gaps = len(words) - 1
    if gaps <= 0:
        return words[0].ljust(width)

    base, extra = spaces_needed // gaps, spaces_needed % gaps
    line = ""
    for i, w in enumerate(words):
        line += w
        if i < gaps:
            line += " " * (base + (1 if i < extra else 0))
    return line


def left_align(lines, width):
    return [(" ".join(line_words)).ljust(width) for line_words in lines]


def right_align(lines, width):
    return [(" ".join(line_words)).rjust(width) for line_words in lines]


def full_justify(lines, width):
    result = []
    for idx, line_words in enumerate(lines):
        is_last = (idx == len(lines) - 1)
        if not line_words:
            result.append(" " * width)
            continue
        if len(line_words) == 1 or is_last:
            line = " ".join(line_words)
            result.append(line.ljust(width))
            continue

        words_len = sum(len(w) for w in line_words)
        total_spaces = width - words_len
        gaps = len(line_words) - 1
        base, extra = total_spaces // gaps, total_spaces % gaps
        line = ""
        for i, w in enumerate(line_words):
            line += w
            if i < gaps:
                line += " " * (base + (1 if i < extra else 0))
        result.append(line)
    return result


def center_align(lines, width):
    result = []
    for line_words in lines:
        line = " ".join(line_words)
        padding = (width - len(line)) // 2
        result.append((" " * padding + line).ljust(width))
    return result


def format_by_type(lines, just_type, width, use_hyphenation=False, hyph=None):
    if just_type == 1:
        if use_hyphenation and hyph:
            return [(line if isinstance(line, str) else " ".join(line)).ljust(width) for line in lines]
        return left_align(lines, width)
    if just_type == 2:
        if use_hyphenation and hyph:
            return [(line if isinstance(line, str) else " ".join(line)).rjust(width) for line in lines]
        return right_align(lines, width)
    if just_type == 3:
        if use_hyphenation and hyph:
            res = []
            for line in lines:
                text = line if isinstance(line, str) else " ".join(line)
                padding = (width - len(text)) // 2
                res.append((" " * padding + text).ljust(width))
            return res
        return center_align(lines, width)
    # just_type == 4
    if use_hyphenation and hyph:
        return [line if isinstance(line, str) else justify_line(line, width) for line in lines]
    return full_justify(lines, width)


# ==================== IO HELPERS ====================

def read_int_with_prompt(prompt, valid_values=None, allow_empty=False):
    while True:
        try:
            value = input(prompt).strip()
            if allow_empty and value == "":
                return None
            if not value:
                continue
            v = int(value)
            if valid_values is None or v in valid_values:
                return v
            print("Буруу сонголт.")
        except ValueError:
            print("Тоог зөв оруулна уу.")
        except KeyboardInterrupt:
            print("\nПрограмаас гарлаа")
            sys.exit(0)


def print_lines(lines):
    for i, line in enumerate(lines, 1):
        print(f"{i:3}: {line}")


def format_ms(ms):
    return f"{ms:.3f} ms"


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def read_text():
    print("\n1) Консол  2) Файл  3) Жишээ")
    src = read_int_with_prompt("Эх сурвалж (1-3): ", [1, 2, 3])
    if src == 1:
        print("Текстээ оруул; END гэж бичээд дуусгана:")
        lines = []
        while True:
            try:
                line = input()
                if line is None or line.strip().upper() == "END":
                    break
                lines.append(line.strip())
            except (EOFError, KeyboardInterrupt):
                print("\nПрограмаас гарлаа")
                sys.exit(0)
        return " ".join(lines)
    if src == 2:
        while True:
            try:
                path = input("Файлын зам: ").strip()
                if not path:
                    continue
                if path.lower() == "back":
                    return ""
                with open(path, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except FileNotFoundError:
                print("Файл олдсонгүй.")
            except Exception as e:
                print(f"Алдаа: {e}")
    # src == 3
    return (
        "Монгол хэл бол монгол үндэстний эртнээс хэрэглэж ирсэн бичиг үсэг юм. "
        "English text can also be hyphenated with this program, including words like "
        "hyphenation, programming, and impossible."
    )


def save_output(filename, text, max_width, just_type, algo_choice, out=None, algorithms=None, results=None, times=None):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\nТЕКСТИЙГ ЖИГДЛЭХ ПРОГРАМ - ҮР ДҮН\n" + "=" * 60 + "\n\n")
            f.write(f"Текст урт: {len(text)} тэмдэгт\n")
            f.write(f"Мөрийн өргөн: {max_width}\n")
            f.write(f"Жигдлэлийн төрөл: {['Зүүн','Баруун','Төв','Хоёр талд'][just_type-1]}\n")
            if algo_choice != 5:
                f.write(f"Алгоритм: {['Greedy','Greedy+Hyphenation','DP','DP+Hyphenation'][algo_choice-1]}\n\n")
                if out:
                    for i, line in enumerate(out, 1):
                        f.write(f"{i:3}: {line}\n")
            else:
                f.write("Алгоритм: Бүх алгоритмын харьцуулалт\n\n")
                for i, (name, out_lines) in enumerate(zip(algorithms, results)):
                    f.write(f"\n{name} ({format_ms(times[i])}):\n")
                    for j, line in enumerate(out_lines, 1):
                        f.write(f"{j:3}: {line}\n")
        print(f"Хадгаллаа: {filename}")
    except Exception as e:
        print(f"Файл хадгалахад алдаа: {e}")


# ==================== MAIN ====================

def main():
    hy = MultiLangHyphenator()
    clear_screen()

    while True:
        print("\nМеню:\n1) Текст оруулах/унших\n2) Гарах")
        main_choice = read_int_with_prompt("Сонголт (1-2): ", [1, 2])
        if main_choice == 2:
            print("Баяртай!")
            break

        text = read_text()
        if not text:
            print("Текст алга, буцлаа.")
            continue

        while True:
            print("\nАЛГОРИТМ:")
            print("1) Greedy")
            print("2) Greedy + Hyphenation")
            print("3) DP")
            print("4) DP + Hyphenation")
            print("5) Бүх алгоритмыг жиших")
            print("6) Буцах")
            algo_choice = read_int_with_prompt("Сонголт (1-6): ", [1, 2, 3, 4, 5, 6])
            if algo_choice == 6:
                break

            print("\nЖИГДЛЭЛ:")
            print("1) Зүүн  2) Баруун  3) Төв  4) Хоёр талд")
            just_type = read_int_with_prompt("Сонголт (1-4): ", [1, 2, 3, 4])

            max_width = read_int_with_prompt("Мөрийн өргөн (20-200): ")
            if max_width < 20 or max_width > 200:
                max_width = 60

            words = split_words(text)

            if algo_choice == 1:
                t0 = time.perf_counter() * 1_000_000
                g_lines = greedy_break(words, max_width)
                t1 = time.perf_counter() * 1_000_000
                out = format_by_type(g_lines, just_type, max_width)
                elapsed_ms = (t1 - t0) / 1_000_000
                print(f"\nGREEDY ({format_ms(elapsed_ms)})")
                print_lines(out)

            elif algo_choice == 2:
                t0 = time.perf_counter() * 1_000_000
                if just_type == 4:
                    out = greedy_justify_with_hyphenation(words, max_width, hy)
                else:
                    g_lines = greedy_break(words, max_width)
                    out = format_by_type(g_lines, just_type, max_width, True, hy)
                t1 = time.perf_counter() * 1_000_000
                elapsed_ms = (t1 - t0) / 1_000_000
                print(f"\nGREEDY+HYPHEN ({format_ms(elapsed_ms)})")
                print_lines(out)

            elif algo_choice == 3:
                t0 = time.perf_counter() * 1_000_000
                if just_type == 4:
                    out = dp_justify_with_hyphenation(" ".join(words), max_width)
                else:
                    dp_lines = dp_break(words, max_width)
                    out = format_by_type(dp_lines, just_type, max_width)
                t1 = time.perf_counter() * 1_000_000
                elapsed_ms = (t1 - t0) / 1_000_000
                print(f"\nDP ({format_ms(elapsed_ms)})")
                print_lines(out)

            elif algo_choice == 4:
                t0 = time.perf_counter() * 1_000_000
                dp_hyphen_lines = dp_with_hyphenation(words.copy(), max_width, hy)
                out = format_by_type(dp_hyphen_lines, just_type, max_width, True, hy)
                t1 = time.perf_counter() * 1_000_000
                elapsed_ms = (t1 - t0) / 1_000_000
                print(f"\nDP+HYPHEN ({format_ms(elapsed_ms)})")
                print_lines(out)

            else:  # compare all
                print("\nБҮХ АЛГОРИТМЫН ХАРЬЦУУЛАЛТ")
                algorithms = ["Greedy", "Greedy+Hyphen", "DP", "DP+Hyphen"]
                results, times = [], []

                # 1) Greedy
                t0 = time.perf_counter() * 1_000_000
                g_lines = greedy_break(words, max_width)
                g_out = format_by_type(g_lines, just_type, max_width)
                t1 = time.perf_counter() * 1_000_000
                times.append((t1 - t0) / 1_000_000)
                results.append(g_out)

                # 2) Greedy+Hyphen
                t0 = time.perf_counter() * 1_000_000
                if just_type == 4:
                    gh_out = greedy_justify_with_hyphenation(words, max_width, hy)
                else:
                    gh_lines = greedy_break(words, max_width)
                    gh_out = format_by_type(gh_lines, just_type, max_width, True, hy)
                t1 = time.perf_counter() * 1_000_000
                times.append((t1 - t0) / 1_000_000)
                results.append(gh_out)

                # 3) DP
                t0 = time.perf_counter() * 1_000_000
                if just_type == 4:
                    dp_out = dp_justify_with_hyphenation(" ".join(words), max_width)
                else:
                    dp_lines = dp_break(words, max_width)
                    dp_out = format_by_type(dp_lines, just_type, max_width)
                t1 = time.perf_counter() * 1_000_000
                times.append((t1 - t0) / 1_000_000)
                results.append(dp_out)

                # 4) DP+Hyphen
                t0 = time.perf_counter() * 1_000_000
                dp_hyphen_lines = dp_with_hyphenation(words.copy(), max_width, hy)
                dp_hyphen_out = format_by_type(dp_hyphen_lines, just_type, max_width, True, hy)
                t1 = time.perf_counter() * 1_000_000
                times.append((t1 - t0) / 1_000_000)
                results.append(dp_hyphen_out)

                print("\nГҮЙЦЭТГЭЛ:")
                for name, t in zip(algorithms, times):
                    print(f"{name:15}: {format_ms(t)}")
                fastest_idx = times.index(min(times))
                print(f"\n✓ Хамгийн хурдан: {algorithms[fastest_idx]}")

                print("\nАль алгоритмын үр дүнг харах вэ?")
                print("0) Бүгд  1) Greedy  2) Greedy+Hyphen  3) DP  4) DP+Hyphen")
                view_choice = read_int_with_prompt("Сонголт (0-4): ", [0, 1, 2, 3, 4])
                if view_choice == 0:
                    for i, (name, out_lines) in enumerate(zip(algorithms, results)):
                        print(f"\n{name} ({format_ms(times[i])})")
                        print_lines(out_lines)
                else:
                    idx = view_choice - 1
                    print(f"\n{algorithms[idx]} ({format_ms(times[idx])})")
                    print_lines(results[idx])

            # save?
            print("\nҮр дүнг файлд хадгалах уу? (Y/N)")
            if input("> ").strip().lower() in ["y", "yes"]:
                filename = f"output_{int(time.time())}.txt"
                if algo_choice != 5:
                    save_output(filename, text, max_width, just_type, algo_choice, out=out)
                else:
                    save_output(filename, text, max_width, just_type, algo_choice,
                                algorithms=algorithms, results=results, times=times)

            print("\n1) Дахин ажиллуулах  2) Буцах  3) Гарах")
            next_choice = read_int_with_prompt("Сонголт (1-3): ", [1, 2, 3])
            if next_choice == 2:
                break
            if next_choice == 3:
                print("Баяртай!")
                return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмаас гарлаа. Баяртай!")
    except Exception as e:
        print(f"\nҮндсэн алдаа гарлаа: {e}")
        print("Програмыг дахин эхлүүлнэ үү.")
