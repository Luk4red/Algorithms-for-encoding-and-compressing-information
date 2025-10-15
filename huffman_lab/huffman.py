class Node: # Узел дерева
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

def serialize_tree(node): # Дерево в строку
    if node.char is not None:
        return '1' + format(ord(node.char), '016b')  # 1 + 16 бит символа
    else:
        return '0' + serialize_tree(node.left) + serialize_tree(node.right)

def deserialize_tree(bits, index=0): # Из строки в дерево
    if bits[index] == '1':
        char_bits = bits[index + 1:index + 17]
        char = chr(int(char_bits, 2))
        return Node(char, 0), index + 17
    else:
        left, next_index = deserialize_tree(bits, index + 1)
        right, next_index = deserialize_tree(bits, next_index)
        node = Node(None, 0)
        node.left = left
        node.right = right
        return node, next_index
        
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

def huffman_encode(input_path, output_path): # Кодируем
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    freq = count_frequencies(text)
    root = build_tree(freq)
    codes = generate_codes(root)
    encoded_text = ''.join(codes[ch] for ch in text)

    tree_bits = serialize_tree(root)
    tree_bytes = bits_to_bytes(tree_bits)
    encoded_bytes = bits_to_bytes(encoded_text)

    with open(output_path, 'wb') as f:
        f.write(len(tree_bytes).to_bytes(2, 'big'))
        f.write(tree_bytes)
        f.write(encoded_bytes)   

def huffman_decode(input_path, output_path): # Декодируем
    with open(input_path, 'rb') as f:
        size_bytes = f.read(2)
        tree_size = int.from_bytes(size_bytes, 'big')

        tree_data = f.read(tree_size)
        encoded_data = f.read()

    tree_bits = bytes_to_bits(tree_data)
    root, _ = deserialize_tree(tree_bits)

    encoded_bits = bytes_to_bits(encoded_data)
    
    node = root
    decoded_text = ''
    for bit in encoded_bits:
        node = node.left if bit == '0' else node.right
        if node.char is not None:
            decoded_text += node.char
            node = root

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(decoded_text)

def compare_files(file1, file2): # Сравнение
    with open(file1, 'r', encoding='utf-8') as f1:
        text1 = f1.read()
    with open(file2, 'r', encoding='utf-8') as f2:
        text2 = f2.read()
    return text1 == text2
