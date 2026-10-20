def add(a, b):
    return a + b


def divide(a, b):
    return a / b


def average(numbers):
    return sum(numbers) / len(numbers)


if __name__ == "__main__":
    print(add(10, 5))
    print(divide(10, 0))
    print(average([]))
