class A:
    def __init__(self):
        print(type(self))

    def copy(self):
        return type(self)()

a = A()
b = a.copy()
print(b, a)
