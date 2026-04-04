def find_second_largest():
    sequence = []

    while True:
        try:
            num = int(input("Введите натуральное число (для завершения введите 0): "))
            if num == 0:
                break
            if num < 0:
                print("Пожалуйста, введите натуральное число.")
                continue
            sequence.append(num)
        except ValueError:
            print("Ошибка: Введены некорректные данные. Пожалуйста, введите целое число.")

    if len(sequence) < 2:
        print("В последовательности должно быть как минимум два числа.")
        return None

    sequence.sort(reverse=True)

    second_largest = sequence[1]

    return second_largest


while True:
    result = find_second_largest()
    if result is not None:
        print("Второй по величине элемент в последовательности:", result)
    choice = input("Хотите продолжить (да/нет)? ").lower()
    if choice != 'да':
        break