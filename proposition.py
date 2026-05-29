from os import name


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

class Proposition(Tag):
    name = 'proposition'
    def __new__(cls, value, context=''):
        ctx =  Context(context).value
        lines = ctx.splitlines()
        indent = '    '
        context = '\n'.join([f"{indent}{line}" for line in lines])

        return super().__new__(cls, f'''<context>
{context}
</context>
{value}
''', cls.name)

    def __init__(self, value, context=''):
        super().__init__(value, self.name)
        self.context = Context(context)

    def __invert__(p):
        return Proposition(f'{Proposition(p.value)}\nis false.\n', p.context)

    def __and__(p, q):
        if p.context.value == q.context.value:
            context = p.context
            p, q = Proposition(p.value), Proposition(q.value)
            return Proposition(f'{p}\nand\n{q}\nare both true.\n', context)
        else:
            return Proposition(f'{p}\nand\n{q}\nare both true.\n')

    def __or__(p, q):
        if p.context.value == q.context.value:
            context = p.context
            p, q = Proposition(p.value), Proposition(q.value)
            return Proposition(f'At least one of\n{p}\nand\n{q}\nis true.\n', context)
        else:
            return Proposition(f'At least one of\n{p}\nand\n{q}\nis true.\n')
    def __eq__(p, q):
        if p.context.value == q.context.value:
            context = p.context
            p, q = Proposition(p.value), Proposition(q.value)
            return Proposition(f'{p}\nis true, if and only if\n{q}\nis true.\n', context)
        else:
            return Proposition(f'{p}\nis true, if and only if\n{q}\nis true.\n')
    def __lshift__(p, q):
        if p.context.value == q.context.value:
            context = p.context
            p, q = Proposition(p.value), Proposition(q.value)
            return Proposition(f'{p}\nis true, if\n{q}\nis true.\n', context)
        else:
            return Proposition(f'{p}\nis true, if\n{q}\nis true.\n')

    def __rshift__(p, q):
        if p.context.value == q.context.value:
            context = p.context
            p, q = Proposition(p.value), Proposition(q.value)
            return Proposition(f'{p}\nis true, only if\n{q}\nis true.\n', context)
        else:
            return Proposition(f'{p}\nis true, only if\n{q}\nis true.\n')
        

