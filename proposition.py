class Tag(str):
    def __new__(cls, value, name):
        lines = value.splitlines()
        indent = '    '
        value = '\n'.join([f"{indent}{line}" for line in lines])
        return super().__new__(cls, f"<{name}>\n{value}\n</{name}>")

    def __init__(self, value, name):
        self.value = value
        self.name = name

class Context(Tag):
    name = 'context'
    def __new__(cls, value):
        return super().__new__(cls, value, cls.name)
    def __init__(self, value):
        super().__init__(value, self.name)

class Propersition(Tag):
    name = 'proposition'
    def __new__(cls, value, context=''):
        return super().__new__(cls, value, cls.name)

    def __init__(self, value, context=''):
        super().__init__(value, self.name)
        self.context = context

    def __invert__(p):
        return Propersition(f'{Propersition(p.value)}\nis false.\n', p.context)

    def __and__(p, q):
        if p.context.value == q.context.value:
            context = p.context
            p, q = Propersition(p.value), Propersition(q.value)
            return Propersition(f'{p}\nand\n{q}\nare both true.\n', context)
        else:
            return Propersition(f'{p}\nand\n{q}\nare both true.\n')

    def __or__(p, q):
        if p.context.value == q.context.value:
            context = p.context
            p, q = Propersition(p.value), Propersition(q.value)
            return Propersition(f'At least one of\n{p}\nand\n{q}\nis true.\n', context)
        else:
            return Propersition(f'At least one of\n{p}\nand\n{q}\nis true.\n')
    def __eq__(p, q):
        if p.context.value == q.context.value:
            context = p.context
            p, q = Propersition(p.value), Propersition(q.value)
            return Propersition(f'{p}\nis true, if and only if\n{q}\nis true.\n', context)
        else:
            return Propersition(f'{p}\nis true, if and only if\n{q}\nis true.\n')
    def __lshift__(p, q):
        if p.context.value == q.context.value:
            context = p.context
            p, q = Propersition(p.value), Propersition(q.value)
            return Propersition(f'{p}\nis true, if\n{q}\nis true.\n', context)
        else:
            return Propersition(f'{p}\nis true, if\n{q}\nis true.\n')

    def __rshift__(p, q):
        if p.context.value == q.context.value:
            context = p.context
            p, q = Propersition(p.value), Propersition(q.value)
            return Propersition(f'{p}\nis true, only if\n{q}\nis true.\n', context)
        else:
            return Propersition(f'{p}\nis true, only if\n{q}\nis true.\n')
        

