import pickle

class Node: # Узел дерева
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

def count_frequencies(text): # Подсчет частоты
    freq = {}
    for ch in text:
        if ch in freq:
            freq[ch] += 1
        else:
            freq[ch] = 1
    return freq

def build_tree(freq_dict): # Строим дерево по частоте
    nodes = [Node(ch, fr) for ch, fr in freq_dict.items()]

    while len(nodes) > 1:
        nodes.sort(key=lambda node: node.freq)
        left = nodes.pop(0)
        right = nodes.pop(0)

        parent = Node(None, left.freq + right.freq)
        parent.left = left
        parent.right = right
        nodes.append(parent)

    return nodes[0]

def generate_codes(node, prefix="", code_dict=None): # Код из дерева
    if code_dict is None:
        code_dict = {}
    if node.char is not None:
        code_dict[node.char] = prefix
    else:
        generate_codes(node.left, prefix + "0", code_dict)
        generate_codes(node.right, prefix + "1", code_dict)
    return code_dict

def bits_to_bytes(bit_string): # Бит в байт
    padding = 8 - (len(bit_string) % 8)
    if padding == 8:
        padding = 0
    bit_string += '0' * padding
    byte_array = bytearray()
    for i in range(0, len(bit_string), 8):
        byte_array.append(int(bit_string[i:i+8], 2))
    return bytes([padding]) + bytes(byte_array)

def bytes_to_bits(byte_data): # Байт в бит
    padding = byte_data[0]
    bits = ''.join(f'{b:08b}' for b in byte_data[1:])
    if padding:
        bits = bits[:-padding]
    return bits

def huffman_encode(input_path, output_path): # Кодирование
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    freq = count_frequencies(text)
    root = build_tree(freq)
    codes = generate_codes(root)
    encoded_text = ''.join(codes[ch] for ch in text)
    encoded_bytes = bits_to_bytes(encoded_text)

    with open(output_path, 'wb') as f:
        pickle.dump(codes, f)      
        f.write(encoded_bytes)       

def huffman_decode(input_path, output_path): # Декодирование
    with open(input_path, 'rb') as f:
        codes = pickle.load(f)  
        encoded_bytes = f.read()

    inverse_codes = {v: k for k, v in codes.items()}
    encoded_text = bytes_to_bits(encoded_bytes)

    current_code = ''
    decoded_text = ''
    for bit in encoded_text:
        current_code += bit
        if current_code in inverse_codes:
            decoded_text += inverse_codes[current_code]
            current_code = ''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(decoded_text)

def compare_files(file1, file2): # Сравнение
    with open(file1, 'r', encoding='utf-8') as f1:
        text1 = f1.read()
    with open(file2, 'r', encoding='utf-8') as f2:
        text2 = f2.read()
    return text1 == text2
