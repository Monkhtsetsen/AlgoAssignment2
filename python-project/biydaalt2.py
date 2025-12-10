import pyphen
import math
import time
import sys
import os


class Mongolian:
    def __init__(self):
        try:
            self.dic = pyphen.Pyphen(filename='hyph_mn_MN.dic')
        except Exception as e:
            print(f"Салбарын толь олдсонгүй: {e}")
            print("Анхдагч толь ашиглаж байна...")
            self.dic = pyphen.Pyphen(lang='mn')

    def hyphenate(self, word):
        try:
            inserted = self.dic.inserted(word)
            cuts = [i for i, c in enumerate(inserted) if c == "-"]
            return cuts
        except Exception:
            return []


def split_words(text):
    return [w for w in text.split() if w]


def greedy_justify_with_hyphenation(words, width, hyph):
    """Хууны кодны Greedy + Hyphenation"""
    result = []
    line_words = []
    current_len = 0

    for w in words:
        if current_len + len(w) + len(line_words) <= width:
            line_words.append(w)
            current_len += len(w)
        else:
            cuts = hyph.hyphenate(w)
            placed = False

            for c in reversed(cuts):
                left = w[:c] + "-"
                right = w[c:]

                if current_len + len(left) + len(line_words) <= width:
                    line_words.append(left)
                    result.append(justify_line(line_words, width))
                    line_words = [right]
                    current_len = len(right)
                    placed = True
                    break

            if not placed:
                result.append(justify_line(line_words, width))
                line_words = [w]
                current_len = len(w)

    if line_words:
        result.append(justify_line(line_words, width))
    return result


def greedy_break(words, width):
    """Java кодын Greedy (hyphenation байхгүй)"""
    lines = []
    i = 0
    while i < len(words):
        line = []
        length = 0
        while i < len(words):
            w = words[i]
            if not line:
                line.append(w)
                length = len(w)
                i += 1
                if length > width:
                    break
            else:
                if length + 1 + len(w) <= width:
                    length += 1 + len(w)
                    line.append(w)
                    i += 1
                else:
                    break
        lines.append(line)
    return lines


# ==================== DP ALGORITHMS ====================

def dp_justify_with_hyphenation(text, width):
    """Хууны кодны DP (hyphenation байхгүй)"""
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

    lines = []
    i = 0
    while i < n:
        j = nxt[i]
        lines.append(justify_line(words[i:j], width))
        i = j

    return lines


def dp_break(words, width):
    """Java кодын DP (hyphenation байхгүй)"""
    n = len(words)
    INF = float('inf')
    dp = [INF] * (n + 1)
    next_idx = [-1] * (n + 1)
    dp[n] = 0

    for i in range(n - 1, -1, -1):
        best = INF
        best_j = -1
        length = 0

        for j in range(i, n):
            if j == i:
                length = len(words[j])
            else:
                length += 1 + len(words[j])

            if j == i and length > width:
                cost = 0
                if dp[j + 1] != INF and dp[j + 1] + cost < best:
                    best = dp[j + 1] + cost
                    best_j = j + 1
                break

            if length > width:
                break

            cost = 0 if j == n - 1 else (width - length) ** 3

            if dp[j + 1] != INF and dp[j + 1] + cost < best:
                best = dp[j + 1] + cost
                best_j = j + 1

        dp[i] = best
        next_idx[i] = best_j

    lines = []
    i = 0
    while i < n:
        j = next_idx[i]
        if j <= i or j == -1:
            lines.extend(greedy_break(words[i:], width))
            break
        lines.append(words[i:j])
        i = j

    return lines


# ==================== DP + HYPHENATION АЛГОРИТМ ====================

def dp_with_hyphenation(words, width, hyph):
    """
    Dynamic Programming + Hyphenation алгоритм
    Энэ нь DP-г гипенацитай хослуулсан шинэ алгоритм юм
    """
    n = len(words)
    INF = float('inf')

    # DP хүснэгтүүд
    dp = [INF] * (n + 1)
    next_idx = [-1] * (n + 1)
    dp[n] = 0

    # Мөрийн үгсийг хадгалах
    line_contents = [None] * (n + 1)

    for i in range(n - 1, -1, -1):
        best_cost = INF
        best_j = -1
        best_line = None

        # j нь дараагийн мөрийн эхлэл
        for j in range(i + 1, n + 1):
            # i:j хүртэлх үгсээс мөрийг бүтээх
            line_words = []
            current_len = 0
            valid_line = True

            for k in range(i, j):
                word = words[k]

                # Хэрэв энэ үг орохгүй бол гипенаци хийх боломж шалгах
                if current_len + len(word) + (1 if line_words else 0) > width:
                    # Гипенаци хийх боломжтой эсэхийг шалгах
                    cuts = hyph.hyphenate(word)
                    hyphen_used = False

                    for c in reversed(cuts):
                        left_part = word[:c] + "-"
                        right_part = word[c:]

                        if current_len + len(left_part) + (1 if line_words else 0) <= width:
                            # Гипенаци хийж болно
                            line_words.append(left_part)
                            # Баруун хэсгийг дараагийн үг болгох
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

            # Мөрийн уртыг тооцоолох
            line_length = sum(len(w) for w in line_words) + max(0, len(line_words) - 1)

            if line_length > width:
                break

            # Өрөөний муужилтыг тооцоолох (cubed cost - Java кодын адил)
            if j == n:
                cost = 0  # Сүүлийн мөр
            else:
                cost = (width - line_length) ** 3

            if dp[j] != INF and dp[j] + cost < best_cost:
                best_cost = dp[j] + cost
                best_j = j
                best_line = line_words

        if best_j != -1:
            dp[i] = best_cost
            next_idx[i] = best_j
            line_contents[i] = best_line

    # Үр дүнг бүтээх
    lines = []
    i = 0
    while i < n:
        j = next_idx[i]
        if j <= i or j == -1:
            # DP амжилтгүй болвол Greedy + Hyphenation ашиглах
            remaining_words = words[i:]
            greedy_result = greedy_justify_with_hyphenation(remaining_words, width, hyph)
            lines.extend([[w] if isinstance(w, str) else w for w in greedy_result])
            break

        if line_contents[i] is not None:
            lines.append(line_contents[i])

        i = j

    return lines


# ==================== JUSTIFICATION FORMATTING ====================

def justify_line(words, width):
    """Хоёр талд жигдлэх (full justify)"""
    if len(words) == 1:
        return words[0].ljust(width)

    total_chars = sum(len(w) for w in words)
    spaces_needed = width - total_chars
    gaps = len(words) - 1

    if gaps <= 0:
        return words[0].ljust(width)

    base = spaces_needed // gaps
    extra = spaces_needed % gaps

    line = ""
    for i, w in enumerate(words):
        line += w
        if i < gaps:
            line += " " * (base + (1 if i < extra else 0))

    return line


def left_align(lines, width):
    """Зүүн талд жигдлэх"""
    result = []
    for line_words in lines:
        line = " ".join(line_words)
        if len(line) < width:
            line += " " * (width - len(line))
        result.append(line)
    return result


def right_align(lines, width):
    """Баруун талд жигдлэх"""
    result = []
    for line_words in lines:
        line = " ".join(line_words)
        if len(line) < width:
            line = " " * (width - len(line)) + line
        result.append(line)
    return result


def full_justify(lines, width):
    """Java кодын full justify"""
    result = []
    for idx, line_words in enumerate(lines):
        is_last = (idx == len(lines) - 1)

        if len(line_words) == 0:
            result.append(" " * width)
            continue

        if len(line_words) == 1 or is_last:
            line = " ".join(line_words)
            if len(line) < width:
                line += " " * (width - len(line))
            result.append(line)
            continue

        words_len = sum(len(w) for w in line_words)
        total_spaces = width - words_len
        gaps = len(line_words) - 1

        base = total_spaces // gaps
        extra = total_spaces % gaps

        line = ""
        for i, w in enumerate(line_words):
            line += w
            if i < gaps:
                line += " " * (base + (1 if i < extra else 0))

        result.append(line)

    return result


def center_align(lines, width):
    """Төвд жигдлэх"""
    result = []
    for line_words in lines:
        line = " ".join(line_words)
        padding = (width - len(line)) // 2
        result.append((" " * padding + line).ljust(width))
    return result


def format_by_type(lines, just_type, width, use_hyphenation=False, hyph=None):
    """Өөр өөр жигдлэлийн төрлүүд"""
    if just_type == 1:  # Зүүн талд
        if use_hyphenation and hyph:
            # Hyphenation-тай зүүн жигдлэл
            result = []
            for line in lines:
                if isinstance(line, str):
                    result.append(line.ljust(width))
                else:
                    result.append(" ".join(line).ljust(width))
            return result
        else:
            return left_align(lines, width)
    elif just_type == 2:  # Баруун талд
        if use_hyphenation and hyph:
            # Hyphenation-тай баруун жигдлэл
            result = []
            for line in lines:
                if isinstance(line, str):
                    result.append(line.rjust(width))
                else:
                    result.append(" ".join(line).rjust(width))
            return result
        else:
            return right_align(lines, width)
    elif just_type == 3:  # Төвд
        if use_hyphenation and hyph:
            # Hyphenation-тай төвд жигдлэл
            result = []
            for line in lines:
                if isinstance(line, str):
                    text = line
                else:
                    text = " ".join(line)
                padding = (width - len(text)) // 2
                result.append((" " * padding + text).ljust(width))
            return result
        else:
            return center_align(lines, width)
    else:  # just_type == 4: Хоёр талд
        if use_hyphenation and hyph:
            # Hyphenation-тай хоёр талд жигдлэл
            result = []
            for line in lines:
                if isinstance(line, str):
                    result.append(line)
                else:
                    result.append(justify_line(line, width))
            return result
        else:
            return full_justify(lines, width)


# ==================== UTILITY FUNCTIONS ====================

def read_int_with_prompt(prompt, valid_values=None, allow_empty=False):
    """Тоон утга авах валидацитай"""
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
            print(f"Буруу сонголт. Дахин оролт оруулна уу.")
        except ValueError:
            print("Тоог зөв оруулна уу.")
        except KeyboardInterrupt:
            print("\nПрограмаас гарлаа")
            sys.exit(0)


def print_lines(lines):
    """Мөрүүдийг хэвлэх"""
    for i, line in enumerate(lines, 1):
        print(f"{i:3}: {line}")


def format_ms(ms):
    """Миллисекундыг форматлах"""
    return f"{ms:.3f} ms"


def clear_screen():
    """Дэлгэцийг цэвэрлэх"""
    os.system('cls' if os.name == 'nt' else 'clear')


# ==================== MAIN PROGRAM ====================

def main():
    hy = Mongolian()

    clear_screen()
    print("=" * 70)
    print("БИЧВЭР ЖИГДЛЭГЧ - ДП + ГИПЕНАЦИТАЙ ШИНЭ АЛГОРИТМ")
    print("=" * 70)

    MAIN_LOOP = True
    while MAIN_LOOP:
        print("\nМеню:")
        print("1) Текст оруулах (консол)")
        print("2) Файлаас унших")
        print("3) Жишээ текст ашиглах")
        print("4) Гарах")

        main_choice = read_int_with_prompt("Сонголтоо оруулна уу (1-4): ", [1, 2, 3, 4])

        if main_choice == 4:
            print("Програмыг дуусгаж байна!")
            break

        text = ""
        if main_choice == 1:
            print("\nТекстээ оруулна уу. Дуусгахдаа шинэ мөрөнд зөвхөн END гэж бичээд Enter дарна.")
            lines = []
            while True:
                try:
                    line = input()
                    if line is None:
                        break
                    if line.strip().upper() == "END":
                        break
                    lines.append(line.strip())
                except EOFError:
                    break
                except KeyboardInterrupt:
                    print("\nПрограмаас гарлаа")
                    sys.exit(0)

            text = " ".join(lines)

        elif main_choice == 2:
            while True:
                try:
                    path = input("\nФайлын зам оруулна уу: ").strip()
                    if not path:
                        print("Файлын зам хоосон байна. Дахин оруулна уу.")
                        continue

                    if path.lower() == 'back':
                        break

                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            text = f.read().strip()
                        break
                    except FileNotFoundError:
                        print(f"Файл олдсонгүй: {path}")
                    except Exception as e:
                        print(f"Файлыг уншихад алдаа гарлаа: {e}")

                    print("Дахин оролт оруулна уу эсвэл буцахын тулд 'back' гэж бичнэ үү.")
                    opt = input().strip()
                    if opt.lower() == 'back':
                        break

                except KeyboardInterrupt:
                    print("\nПрограмаас гарлаа")
                    sys.exit(0)

        elif main_choice == 3:
            text = """Монгол хэл бол монгол үндэстний эртнээс хэрэглэж ирсэн бичиг үсэг юм. 
Хуучин монгол үсэг нь дээдээс доош бичигддэг онцлогтой. 
Орчин үеийн кирилл үсэг нь зүүнээс баруун тийш бичигддэг. 
Монгол хэл нь агглютинатив хэлний бүлэгт хамаардаг."""
            print("\nЖишээ текст ашиглаж байна...")

        if not text:
            print("Текст оруулаагүй байна. Цэс рүү буцаж байна.")
            continue

        print(f"\nТекст амжилттай уншигдлаа. Текстийн урт: {len(text)} тэмдэгт")

        while True:
            print("\n" + "=" * 50)
            print("АЛГОРИТМ СОНГОХ:")
            print("1) Greedy (энгийн, hyphenation байхгүй)")
            print("2) Greedy + Hyphenation (салаалсан үгс)")
            print("3) Dynamic Programming (энгийн)")
            print("4) Dynamic Programming + Hyphenation (шинэ алгоритм)")
            print("5) Бүх алгоритмыг харьцуулах")
            print("6) Буцах")

            algo_choice = read_int_with_prompt("Сонголт (1-6): ", [1, 2, 3, 4, 5, 6])

            if algo_choice == 6:
                break

            print("\nЖИГДЛЭХ ТӨРӨЛ:")
            print("1) Зүүн талд жигдлэх")
            print("2) Баруун талд жигдлэх")
            print("3) Төвд жигдлэх")
            print("4) Хоёр талд жигдлэх (Full justify)")

            just_type = read_int_with_prompt("Сонголт (1-4): ", [1, 2, 3, 4])

            print("\nМӨРИЙН ӨРГӨН:")
            print("Тайлбар: Ихэнх текстэд 40-80 хооронд өргөн тохиромжтой.")

            max_width = read_int_with_prompt("Мөрийн өргөн оруулна уу (20-200): ", None)
            if max_width < 20 or max_width > 200:
                print("Өргөн 20-200 хооронд байх ёстой. 60 гэж үзье.")
                max_width = 60

            words = split_words(text)

            if algo_choice == 1:  # Greedy (энгийн)
                t0 = time.perf_counter() * 1_000_000
                g_lines = greedy_break(words, max_width)
                t1 = time.perf_counter() * 1_000_000
                out = format_by_type(g_lines, just_type, max_width, False, None)
                elapsed_ms = (t1 - t0) / 1_000_000

                print(f"\n{'=' * 60}")
                print(f"GREEDY АЛГОРИТМ (Үр дүн: {format_ms(elapsed_ms)})")
                print(f"{'=' * 60}")
                print_lines(out)

            elif algo_choice == 2:  # Greedy + Hyphenation
                t0 = time.perf_counter() * 1_000_000

                if just_type == 4:  # Хоёр талд жигдлэх
                    # Greedy + Hyphenation + Full justify
                    result_lines = greedy_justify_with_hyphenation(words, max_width, hy)
                    out = result_lines
                else:
                    # Бусад жигдлэлийн төрлүүд
                    g_lines = greedy_break(words, max_width)
                    out = format_by_type(g_lines, just_type, max_width, True, hy)

                t1 = time.perf_counter() * 1_000_000
                elapsed_ms = (t1 - t0) / 1_000_000

                print(f"\n{'=' * 60}")
                print(f"GREEDY + HYPHENATION АЛГОРИТМ (Үр дүн: {format_ms(elapsed_ms)})")
                print(f"{'=' * 60}")
                print_lines(out)

            elif algo_choice == 3:  # DP (энгийн)
                t0 = time.perf_counter() * 1_000_000

                if just_type == 4:  # Хоёр талд жигдлэх
                    # DP + Full justify
                    result_lines = dp_justify_with_hyphenation(" ".join(words), max_width)
                    out = result_lines
                else:
                    # Бусад жигдлэлийн төрлүүд
                    dp_lines = dp_break(words, max_width)
                    out = format_by_type(dp_lines, just_type, max_width, False, None)

                t1 = time.perf_counter() * 1_000_000
                elapsed_ms = (t1 - t0) / 1_000_000

                print(f"\n{'=' * 60}")
                print(f"DYNAMIC PROGRAMMING АЛГОРИТМ (Үр дүн: {format_ms(elapsed_ms)})")
                print(f"{'=' * 60}")
                print_lines(out)

            elif algo_choice == 4:  # DP + Hyphenation (шинэ алгоритм)
                t0 = time.perf_counter() * 1_000_000
                dp_hyphen_lines = dp_with_hyphenation(words.copy(), max_width, hy)
                t1 = time.perf_counter() * 1_000_000
                out = format_by_type(dp_hyphen_lines, just_type, max_width, True, hy)
                elapsed_ms = (t1 - t0) / 1_000_000

                print(f"\n{'=' * 60}")
                print(f"DP + HYPHENATION АЛГОРИТМ (Үр дүн: {format_ms(elapsed_ms)})")
                print(f"{'=' * 60}")
                print(f"Тайлбар: Энэ нь Dynamic Programming алгоритмыг")
                print(f"гипенацитай хослуулсан шинэ алгоритм юм.")
                print(f"{'=' * 60}")
                print_lines(out)

            else:  # algo_choice == 5: Бүх алгоритмыг харьцуулах
                print(f"\n{'=' * 60}")
                print("БҮХ АЛГОРИТМЫН ХАРЬЦУУЛАЛТ")
                print(f"{'=' * 60}")

                results = []
                times = []
                algorithms = [
                    "Greedy",
                    "Greedy+Hyphen",
                    "DP",
                    "DP+Hyphen"
                ]

                # 1. Greedy (энгийн)
                t0 = time.perf_counter() * 1_000_000
                g_lines = greedy_break(words, max_width)
                g_out = format_by_type(g_lines, just_type, max_width, False, None)
                t1 = time.perf_counter() * 1_000_000
                greedy_time = (t1 - t0) / 1_000_000
                results.append(g_out)
                times.append(greedy_time)

                # 2. Greedy + Hyphenation
                t0 = time.perf_counter() * 1_000_000
                if just_type == 4:
                    gh_out = greedy_justify_with_hyphenation(words, max_width, hy)
                else:
                    gh_lines = greedy_break(words, max_width)
                    gh_out = format_by_type(gh_lines, just_type, max_width, True, hy)
                t1 = time.perf_counter() * 1_000_000
                greedy_hyphen_time = (t1 - t0) / 1_000_000
                results.append(gh_out)
                times.append(greedy_hyphen_time)

                # 3. DP (энгийн)
                t0 = time.perf_counter() * 1_000_000
                if just_type == 4:
                    dp_out = dp_justify_with_hyphenation(" ".join(words), max_width)
                else:
                    dp_lines = dp_break(words, max_width)
                    dp_out = format_by_type(dp_lines, just_type, max_width, False, None)
                t1 = time.perf_counter() * 1_000_000
                dp_time = (t1 - t0) / 1_000_000
                results.append(dp_out)
                times.append(dp_time)

                # 4. DP + Hyphenation
                t0 = time.perf_counter() * 1_000_000
                dp_hyphen_lines = dp_with_hyphenation(words.copy(), max_width, hy)
                dp_hyphen_out = format_by_type(dp_hyphen_lines, just_type, max_width, True, hy)
                t1 = time.perf_counter() * 1_000_000
                dp_hyphen_time = (t1 - t0) / 1_000_000
                results.append(dp_hyphen_out)
                times.append(dp_hyphen_time)

                # Харьцуулалтыг хэвлэх
                print(f"\nГҮЙЦЭТГЭЛИЙН ХАРЬЦУУЛАЛТ:")
                print(f"{'-' * 40}")
                for i, (name, time_val) in enumerate(zip(algorithms, times)):
                    print(f"{name:20} : {format_ms(time_val)}")

                # Хамгийн хурдыг тодруулах
                fastest_idx = times.index(min(times))
                fastest_name = algorithms[fastest_idx]
                fastest_time = times[fastest_idx]

                print(f"\n✓ ХАМГИЙН ХУРД АЛГОРИТМ: {fastest_name} ({format_ms(fastest_time)})")

                # Үр дүнг харах сонголт
                print(f"\nАль алгоритмын үр дүнг харах вэ?")
                print("0) Бүгдийг дараалан харах")
                for i, name in enumerate(algorithms, 1):
                    print(f"{i}) {name}")

                view_choice = read_int_with_prompt("Сонголт (0-4): ", [0, 1, 2, 3, 4])

                if view_choice == 0:
                    for i, (name, out_lines) in enumerate(zip(algorithms, results)):
                        print(f"\n{'=' * 60}")
                        print(f"{name} - ҮР ДҮН ({format_ms(times[i])})")
                        print(f"{'=' * 60}")
                        print_lines(out_lines)
                else:
                    out_lines = results[view_choice - 1]
                    name = algorithms[view_choice - 1]
                    print(f"\n{'=' * 60}")
                    print(f"{name} - ҮР ДҮН ({format_ms(times[view_choice - 1])})")
                    print(f"{'=' * 60}")
                    print_lines(out_lines)

            # Үр дүнг файлд хадгалах
            print(f"\n{'=' * 60}")
            save_choice = input("Үр дүнг файлд хадгалах уу? (т/ү): ").strip().lower()
            if save_choice in ['т', 'y', 'yes']:
                filename = f"output_{int(time.time())}.txt"
                try:
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write("=" * 60 + "\n")
                        f.write("ТЕКСТИЙГ ЖИГДЛЭХ ПРОГРАМ - ҮР ДҮН\n")
                        f.write("=" * 60 + "\n\n")
                        f.write(f"Текст урт: {len(text)} тэмдэгт\n")
                        f.write(f"Мөрийн өргөн: {max_width}\n")
                        f.write(
                            f"Жигдлэлийн төрөл: {'Зүүн' if just_type == 1 else 'Баруун' if just_type == 2 else 'Төв' if just_type == 3 else 'Хоёр талд'}\n")

                        if algo_choice != 5:
                            f.write(
                                f"Алгоритм: {['Greedy', 'Greedy+Hyphenation', 'DP', 'DP+Hyphenation'][algo_choice - 1]}\n")
                            f.write("=" * 60 + "\n\n")
                            if 'out' in locals():
                                for i, line in enumerate(out, 1):
                                    f.write(f"{i:3}: {line}\n")
                        else:
                            f.write("Алгоритм: Бүх алгоритмын харьцуулалт\n")
                            f.write("=" * 60 + "\n\n")
                            for i, (name, out_lines) in enumerate(zip(algorithms, results)):
                                f.write(f"\n{name}:\n")
                                for j, line in enumerate(out_lines, 1):
                                    f.write(f"{j:3}: {line}\n")
                    print(f"Үр дүн амжилттай хадгалагдлаа: {filename}")
                except Exception as e:
                    print(f"Файл хадгалахад алдаа: {e}")

            # Дахин ажиллуулах эсвэл цэс рүү буцах
            print(f"\n{'=' * 60}")
            print("Дараах үйлдлүүд:")
            print("1) Ижил текстээр дахин ажиллуулах")
            print("2) Цэс рүү буцах")
            print("3) Програмаас гарах")

            next_choice = read_int_with_prompt("Сонголт (1-3): ", [1, 2, 3])

            if next_choice == 2:
                break
            elif next_choice == 3:
                MAIN_LOOP = False
                print("Програмыг дуусгаж байна. Баярлалаа!")
                break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмаас гарлаа. Баяртай!")
    except Exception as e:
        print(f"\nҮндсэн алдаа гарлаа: {e}")
        print("Програмыг дахин эхлүүлнэ үү.")