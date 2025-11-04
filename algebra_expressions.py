class AlgebraExpression:
    def to_string(self, indent=0):
        raise NotImplementedError

    def to_linear_string(self, indent=0):
        raise NotImplementedError

    def get_tables(self):
        raise NotImplementedError


class Projection(AlgebraExpression):
    """Projeção (π)"""

    def __init__(self, attributes, child):
        self.attributes = attributes
        self.child = child

    def to_linear_string(self, indent=0):
        attrs = ", ".join(self.attributes)
        indent_str = "  " * indent
        child_str = self.child.to_linear_string(indent + 1)
        return f"{indent_str}π {attrs} (\n{child_str}\n{indent_str})"

    def get_tables(self):
        return self.child.get_tables()


class Selection(AlgebraExpression):
    """Seleção (σ)"""

    def __init__(self, condition, child):
        self.condition = condition
        self.child = child

    def to_linear_string(self, indent=0):
        cond = self.condition.replace(" and ", " ^ ").replace(" AND ", " ^ ")
        indent_str = "  " * indent
        child_str = self.child.to_linear_string(indent + 1)
        return f"{indent_str}σ {cond} (\n{child_str}\n{indent_str})"

    def get_tables(self):
        return self.child.get_tables()


class Join(AlgebraExpression):
    """Junção (⋈)"""

    def __init__(self, condition, left, right):
        self.condition = condition
        self.left = left
        self.right = right

    def to_linear_string(self, indent=0):
        indent_str = "  " * indent
        left_str = self.left.to_linear_string(indent + 1)
        right_str = self.right.to_linear_string(indent + 1)
        return f"{indent_str}(\n{left_str}\n{indent_str}  ⋈ {self.condition}\n{right_str}\n{indent_str})"

    def get_tables(self):
        return self.left.get_tables() + self.right.get_tables()


class Table(AlgebraExpression):
    """Tabela (relação base)"""

    def __init__(self, name):
        self.name = name

    def to_linear_string(self, indent=0):
        indent_str = "  " * indent
        return f"{indent_str}{self.name}"

    def get_tables(self):
        return [self.name]
