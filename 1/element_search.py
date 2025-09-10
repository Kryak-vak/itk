


def search(number: int, elements: list) -> bool:
    length = len(elements)
    print(length, elements)

    if length == 1:
        return elements[0] == number
    
    middle_index = int(length / 2)
    middle_element = elements[middle_index]
    if middle_element == number:
        return True
    elif middle_element > number:
        return search(number, elements[:middle_index])
    else:
        return search(number, elements[middle_index + 1:])


if __name__ == "__main__":
    numbers = [1, 2, 3, 45, 356, 569, 600, 705, 923]
    print(search(933, numbers))

