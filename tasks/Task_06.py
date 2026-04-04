def swap_neighbours(lst):
    for i in range(0, len(lst) - 1, 2):
        lst[i], lst[i + 1] = lst[i + 1], lst[i]

user_input = input("Введите элементы списка через пробел: ")
my_list = [int(x) for x in user_input.split()]

print("Исходный список:", my_list)
swap_neighbours(my_list)
print("Список после перестановки соседних элементов:", my_list)