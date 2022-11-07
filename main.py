from typing import List


class EmptyStack(Exception):
    pass


class Stack:
    def __init__(self):
        self._items = []
        self._size = 0

    def is_empty(self):
        return self._size == 0

    def push(self, item):
        self._items.append(item)
        self._size += 1

    def pop(self):
        if self._size:
            self._size -= 1
            return self._items.pop()
        raise EmptyStack

    def peek(self):
        return self._items[-1] if self._size else None

    def size(self):
        return self._size


def bracket_validator(text: str, brackets: List[tuple] = [('(', ')',), ('[', ']',), ('{', '}',)]):
    """
    :param text: текст для проверки
    :param brackets: список кортежей, в которых первый элемент это открывающая скобка, второй - закрывающая.
    :return: True если все открытые скобки закрыты и не осталось открытых скобок
    """
    stacks = [Stack() for _ in brackets]
    for char in text:
        item = [(index, bracket,) for index, bracket in enumerate(brackets) if char in bracket]
        if len(item):
            stack_index, bracket = item[0]
            stack = stacks[stack_index]
            if bracket.index(char) == 1:
                if not stack.size():
                    return False
            else:
                stack.push(True)
    return not any([True for stack in stacks if stack.size() > 0])


if __name__ == '__main__':
    user_input = input("Введите текст для проверки: ")
    if bracket_validator(user_input):
        print("Сбалансированно")
    else:
        print("Несбалансированно")
