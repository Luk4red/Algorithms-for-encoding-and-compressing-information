from huffman import huffman_encode, huffman_decode, compare_files

original = "example.txt"
encoded = "example.huff"
decoded = "example_decode.txt"
k = 0
while True:
    k = int(input("Выберете действие: \n 0. Выход \n 1. Закодировать \n 2. Декодировать \n 3. Сравнить файлы на совпадения \n "))
    match k:
        case 0:
            print("Удачи")
            break
        case 1:
            original = input("Введите местоположения файла: ")
            encoded = input("Как будет называться файл? (без .huff)") + ".huff"
            huffman_encode(original, encoded)
            print("Файл закодирован.")
        case 2:
            encoded = input("Введите местоположения файла: ")
            decoded = input("Как будет называться файл? (без .txt)") + "_decoded.txt"
            huffman_decode(encoded, decoded)
            print("Файл декодирован.")
        case 3:
            original = input("Введите местоположения первого файла: ") 
            decoded = input("Введите местоположения второго файла: ") 
            if compare_files(original, decoded):
                print("✅ Файлы совпадают!")
            else:
                print("❌ Файлы не совпадают.")
        case _:
            print("Выберите от 0-3")
