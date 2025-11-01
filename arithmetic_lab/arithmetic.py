import time
from collections import Counter
from pathlib import Path

MAX_VALUE = 65535
FIRST_QTR = (MAX_VALUE + 1) // 4
HALF = FIRST_QTR * 2
THIRD_QTR = FIRST_QTR * 3


def arithmetic_encode(input_file, output_file): #Кодирование
    data = list(Path(input_file).read_bytes())

    freq = Counter(data)  #Таблица частот
    for i in range(256):
        if freq.get(i, 0) == 0:
            freq[i] = 1

    counts = [freq[i] for i in range(256)]
    done = [0]
    for v in counts:
        done.append(done[-1] + v)
    total = done[-1]

    lo, hi = 0, MAX_VALUE
    bits_to_follow = 0
    out_bits = []

    def bits_plus_follow(bit):
        nonlocal bits_to_follow
        out_bits.append(bit)
        while bits_to_follow > 0:
            out_bits.append(1 - bit)
            bits_to_follow -= 1

    start = time.time()
    for c in data:
        r = hi - lo + 1
        lo = lo + (r * done[c]) // total
        hi = lo + (r * (done[c + 1] - done[c])) // total - 1

        while True:
            if hi < HALF:
                bits_plus_follow(0)
                lo *= 2
                hi = hi * 2 + 1
            elif lo >= HALF:
                bits_plus_follow(1)
                lo = 2 * (lo - HALF)
                hi = 2 * (hi - HALF) + 1
            elif lo >= FIRST_QTR and hi < THIRD_QTR:
                bits_to_follow += 1
                lo = 2 * (lo - FIRST_QTR)
                hi = 2 * (hi - FIRST_QTR) + 1
            else:
                break

    bits_to_follow += 1
    bits_plus_follow(0 if lo < FIRST_QTR else 1)
    enc_time = time.time() - start

    byte = 0
    out_bytes = bytearray()
    for i, b in enumerate(out_bits):
        byte = (byte << 1) | b
        if (i + 1) % 8 == 0:
            out_bytes.append(byte)
            byte = 0
    if len(out_bits) % 8 != 0:
        out_bytes.append(byte << (8 - (len(out_bits) % 8)))

    with open(output_file, "wb") as f:
        f.write(len(data).to_bytes(4, "big"))
        for v in counts:
            f.write(v.to_bytes(4, "big"))
        f.write(out_bytes)


    header = 4 + 256 * 4
    compressed = header + len(out_bytes)
    ratio = len(data) / compressed if compressed else 1
    print(f"Кодирование завершено за {enc_time:.4f} сек")
    print(f"Исходный размер: {len(data)} байт")
    print(f"Сжатый размер:  {compressed} байт")
    print(f"Степень сжатия: {ratio:.2f}x")


def arithmetic_decode(input_file, output_file): #Декодирование
    raw = Path(input_file).read_bytes()
    n = int.from_bytes(raw[0:4], "big")
    pos = 4

    counts = [int.from_bytes(raw[pos + i * 4:pos + (i + 1) * 4], "big") for i in range(256)]
    pos += 256 * 4

    done = [0]
    for v in counts:
        done.append(done[-1] + v)
    total = done[-1]

    bits = []
    for byte in raw[pos:]:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    bit_pos = 0

    def read_bit():
        nonlocal bit_pos
        if bit_pos < len(bits):
            bit = bits[bit_pos]
            bit_pos += 1
            return bit
        return 0

    lo, hi = 0, MAX_VALUE
    value = 0
    for _ in range(16):
        value = (value << 1) | read_bit()

    decoded = bytearray()
    start = time.time()

    
    for _ in range(n):
        r = hi - lo + 1
        freq = ((value - lo + 1) * total - 1) // r

        for j in range(256):
            if done[j] <= freq < done[j + 1]:
                c = j
                break

        decoded.append(c)
        lo = lo + (r * done[c]) // total
        hi = lo + (r * (done[c + 1] - done[c])) // total - 1

        while True:
            if hi < HALF:
                pass
            elif lo >= HALF:
                lo -= HALF
                hi -= HALF
                value -= HALF
            elif lo >= FIRST_QTR and hi < THIRD_QTR:
                lo -= FIRST_QTR
                hi -= FIRST_QTR
                value -= FIRST_QTR
            else:
                break
            lo = lo * 2
            hi = hi * 2 + 1
            value = (value * 2) | read_bit()

    Path(output_file).write_bytes(decoded)
    dec_time = time.time() - start
    print(f"Декодирование завершено за {dec_time:.4f} сек")
    print(f"Размер восстановленного файла: {len(decoded)} байт")


def compare_files(file1, file2): #Сравнение
    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        return f1.read() == f2.read()
