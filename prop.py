class Tag(str):
    def __new__(cls, value, name):
        lines = value.splitlines()
        indent = '    '
        value = '\n'.join([f"{indent}{line}" for line in lines])
        return super().__new__(cls, f"<{name}>\n{value}\n</{name}>")

    def __init__(self, value, name):
        self.value = value
        self.name = name

class Ctxt(Tag):
    name = 'context'
    def __new__(cls, value):
        return super().__new__(cls, value, cls.name)
    def __init__(self, value):
        super().__init__(value, self.name)

class Prop(Tag):
    name = 'proposition'
    def __new__(cls, value, context=''):
        return super().__new__(cls, value, cls.name)

    def __init__(self, value, context=''):
        super().__init__(value, self.name)
        self.context = context

    def __invert__(p):
        return Prop(f'{Prop(p.value)}\nis false.\n', p.context)

    def __and__(p, q):
        if p.context.value == q.context.value:
            context = p.context
            p, q = Prop(p.value), Prop(q.value)
            return Prop(f'{p}\nand\n{q}\nare both true.\n', context)
        else:
            return Prop(f'{p}\nand\n{q}\nare both true.\n')

    def __or__(p, q):
        if p.context.value == q.context.value:
            context = p.context
            p, q = Prop(p.value), Prop(q.value)
            return Prop(f'At least one of\n{p}\nand\n{q}\nis true.\n', context)
        else:
            return Prop(f'At least one of\n{p}\nand\n{q}\nis true.\n')
    def __eq__(p, q):
        if p.context.value == q.context.value:
            context = p.context
            p, q = Prop(p.value), Prop(q.value)
            return Prop(f'{p}\nis true, if and only if\n{q}\nis true.\n', context)
        else:
            return Prop(f'{p}\nis true, if and only if\n{q}\nis true.\n')
    def __lshift__(p, q):
        if p.context.value == q.context.value:
            context = p.context
            p, q = Prop(p.value), Prop(q.value)
            return Prop(f'{p}\nis true, if\n{q}\nis true.\n', context)
        else:
            return Prop(f'{p}\nis true, if\n{q}\nis true.\n')

    def __rshift__(p, q):
        if p.context.value == q.context.value:
            context = p.context
            p, q = Prop(p.value), Prop(q.value)
            return Prop(f'{p}\nis true, only if\n{q}\nis true.\n', context)
        else:
            return Prop(f'{p}\nis true, only if\n{q}\nis true.\n')
        

