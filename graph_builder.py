import graphviz

from algebra_expressions import *


class GraphNode:
    def __init__(self, operator, details, children=None):
        self.operator = (
            operator  # Tipo de operador (Projection, Selection, Join, Table)
        )
        self.details = details  # Detalhes do operador
        # Filhos (operadores abaixo)
        self.children = children if children else []
        self.id = None  # ID único para o nó no grafo

    def add_child(self, child):
        self.children.append(child)


class OperatorGraph:
    def __init__(self, root):
        self.root = root  # Nó raiz (última operação)
        self.node_counter = 0  # Contador para IDs únicos

    def render_graphviz(self, filename="query_graph", view=False):
        dot = graphviz.Digraph(comment="Query Execution Graph")
        dot.attr(rankdir="TB")  # Top to Bottom
        dot.attr("node", shape="box", style="rounded,filled", fontname="Arial")

        # Configurar estilos
        self.node_counter = 0
        self._add_nodes_to_graphviz(dot, self.root)

        # Renderizar
        output_path = f"/tmp/{filename}"
        dot.render(output_path, format="png", cleanup=True, view=view)

        return f"{output_path}.png"

    def _add_nodes_to_graphviz(self, dot, node, parent_id=None):
        """Adiciona nós recursivamente ao grafo Graphviz"""
        # Gerar ID único
        node.id = f"node_{self.node_counter}"
        self.node_counter += 1

        # Determinar cor e label baseado no tipo de operador
        if node.operator == "Projeção (π)":
            color = "#E3F2FD"  # Azul claro
            label = f"π\n{node.details}"
        elif node.operator == "Seleção (σ)":
            color = "#FFF3E0"  # Laranja claro
            label = f"σ\n{node.details}"
        elif node.operator == "Junção (⋈)":
            color = "#F3E5F5"  # Roxo claro
            label = f"⋈\n{node.details}"
        elif node.operator == "Tabela":
            color = "#E8F5E9"  # Verde claro
            label = node.details
        else:
            color = "#F5F5F5"  # Cinza claro
            label = f"{node.operator}\n{node.details}"

        # Adicionar nó
        dot.node(node.id, label, fillcolor=color)

        # Conectar ao pai se existir
        if parent_id:
            dot.edge(parent_id, node.id)

        # Processar filhos
        for child in node.children:
            self._add_nodes_to_graphviz(dot, child, node.id)


class GraphBuilder:
    def build_graph(self, algebra_expr):
        root = self._build_node(algebra_expr)
        return OperatorGraph(root)

    def _build_node(self, expr):
        if isinstance(expr, Projection):
            # Nó de projeção
            attrs = ", ".join(expr.attributes)
            node = GraphNode("Projeção (π)", attrs)
            child = self._build_node(expr.child)
            node.add_child(child)
            return node

        elif isinstance(expr, Selection):
            # Nó de seleção
            node = GraphNode("Seleção (σ)", expr.condition)
            child = self._build_node(expr.child)
            node.add_child(child)
            return node

        elif isinstance(expr, Join):
            # Nó de junção
            node = GraphNode("Junção (⋈)", expr.condition)
            left_child = self._build_node(expr.left)
            right_child = self._build_node(expr.right)
            node.add_child(left_child)
            node.add_child(right_child)
            return node

        elif isinstance(expr, Table):
            # Nó folha (tabela)
            node = GraphNode("Tabela", expr.name)
            return node

        else:
            # Tipo desconhecido
            node = GraphNode("Desconhecido", str(expr))
            return node
