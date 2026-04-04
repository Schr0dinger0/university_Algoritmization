def find_minimum_distance():
    sequence = []

    while True:
        try:
            num = int(input("Введите натуральное число (для завершения введите 0): "))
            if num == 0:
                break
            sequence.append(num)
        except ValueError:
            print("Ошибка: Введены некорректные данные. Пожалуйста, введите целое число.")

    if len(sequence) < 2:
        print("В последовательности должно быть как минимум два числа.")
        return 0

    max_dist = 0
    max1 = max2 = None
    for i in range(1, len(sequence) - 1):
        if sequence[i] > sequence[i - 1] and sequence[i] > sequence[i + 1]:
            if max1 is None:
                max1 = i
            elif max2 is None:
                max2 = i
                max_dist = max2 - max1
            else:
                max1 = max2
                max2 = i
                max_dist = min(max_dist, max2 - max1)

    return max_dist


while True:
    result = find_minimum_distance()
    print("Наименьшее расстояние между двумя локальными максимумами:", result)

    choice = input("Хотите продолжить (да/нет)? ").lower()
    if choice != 'да':
        break
