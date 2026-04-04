def find_longest_sequence():
    sequence = []

    while True:
        try:
            num = int(input("Введите число (для завершения введите 0): "))
            if num == 0:
                break
            sequence.append(num)
        except ValueError:
            print("Ошибка: Введены некорректные данные. Пожалуйста, введите целое число.")

    max_sequence = []
    current_sequence = [sequence[0]]
    for i in range(1, len(sequence)):
        if sequence[i] == sequence[i - 1]:
            current_sequence.append(sequence[i])
        else:
            if len(current_sequence) > len(max_sequence):
                max_sequence = current_sequence.copy()
            current_sequence = [sequence[i]]

    if len(current_sequence) > len(max_sequence):
        max_sequence = current_sequence

    return max_sequence


while True:
    result = find_longest_sequence()
    if len(result) > 0:
        print("Наибольшая последовательность элементов равных друг другу:", result)
    else:
        print("В последовательности нет повторяющихся элементов.")

    choice = input("Хотите продолжить (да/нет)? ").lower()
    if choice != 'да':
        break
