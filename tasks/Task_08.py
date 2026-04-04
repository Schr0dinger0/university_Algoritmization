def find_unique_elements(lst):
    element_count = {}
    for num in lst:
        if num in element_count:
            element_count[num] += 1
        else:
            element_count[num] = 1

    unique_elements = [key for key, value in element_count.items() if value == 1]
    return unique_elements


try:
    count = int(input("Введите количество элементов: "))
    if count <= 0:
        print("Ошибка: Количество элементов должно быть положительным числом.")
    else:
        print("Введите элементы списка один за другим:")
        lst = []
        for i in range(count):
            num = int(input(f"Элемент {i + 1}: "))
            lst.append(num)

        unique_elements = find_unique_elements(lst)
        if unique_elements:
            print("Элементы, которые встречаются по одному разу в последовательности:", unique_elements)
        else:
            print("Все элементы встречаются более одного раза в последовательности.")
except ValueError:
    print("Ошибка: Некорректный ввод. Пожалуйста, введите целое число.")
