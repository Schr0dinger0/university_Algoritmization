def count_unique_elements(sorted_list):
    if not sorted_list:
        return 0

    unique_count = 1
    for i in range(1, len(sorted_list)):
        if sorted_list[i] != sorted_list[i - 1]:
            unique_count += 1

    return unique_count


sorted_list = []
while True:
    user_input = input("Введите элемент списка (для завершения введите любой символ): ")
    if not user_input.isdigit():
        break
    num = int(user_input)
    if sorted_list and num < sorted_list[-1]:
        print(
            "Ошибка: Элемент не упорядочен по неубыванию. Пожалуйста, введите элемент, больший или равный предыдущему.")
        continue
    sorted_list.append(num)

unique_count = count_unique_elements(sorted_list)
print("Количество различных элементов в упорядоченном списке:", unique_count)
