class ExecutionStep:
    def __init__(self, step_number, operation, details, dependencies=None):
        self.step_number = step_number
        self.operation = operation
        self.details = details
        self.dependencies = dependencies if dependencies else []

    def __str__(self):
        deps = (
            f" (depende de: {', '.join(map(str, self.dependencies))})"
            if self.dependencies
            else ""
        )
        return f"Passo {self.step_number}: {self.operation} - {self.details}{deps}"


class ExecutionPlan:
    def __init__(self):
        self.steps = []

    def add_step(self, step):
        self.steps.append(step)

    def to_string(self):
        result = "PLANO DE EXECUÇÃO\n"
        result += "=" * 80 + "\n\n"
        result += "Ordem de execução (sequencial, das folhas para a raiz):\n\n"

        for step in self.steps:
            result += str(step) + "\n"

        return result


class ExecutionPlanner:
    def __init__(self):
        self.step_counter = 0

    def create_plan(self, operator_graph):
        plan = ExecutionPlan()
        self.step_counter = 0

        self._traverse_postorder(operator_graph.root, plan)

        return plan

    def _traverse_postorder(self, node, plan, parent_steps=None):
        if parent_steps is None:
            parent_steps = []

        current_dependencies = []

        # Processar filhos primeiro
        for child in node.children:
            child_step = self._traverse_postorder(child, plan, current_dependencies)
            if child_step:
                current_dependencies.append(child_step)

        self.step_counter += 1

        if node.operator == "Tabela":
            step = ExecutionStep(
                self.step_counter,
                "Scan de Tabela",
                f"Ler dados da tabela '{node.details}'",
                [],
            )

        elif node.operator == "Seleção (σ)":
            step = ExecutionStep(
                self.step_counter,
                "Aplicar Seleção",
                f"Filtrar tuplas usando condição: {node.details}",
                current_dependencies,
            )

        elif node.operator == "Projeção (π)":
            step = ExecutionStep(
                self.step_counter,
                "Aplicar Projeção",
                f"Selecionar colunas: {node.details}",
                current_dependencies,
            )

        elif node.operator == "Junção (⋈)":
            step = ExecutionStep(
                self.step_counter,
                "Executar Junção",
                f"Juntar tabelas usando condição: {node.details}",
                current_dependencies,
            )

        else:
            step = ExecutionStep(
                self.step_counter, node.operator, node.details, current_dependencies
            )

        plan.add_step(step)
        return self.step_counter
