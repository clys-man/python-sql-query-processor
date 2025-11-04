import re

from algebra_expressions import *


class QueryOptimizer:
    def optimize(self, algebra_expr):
        """
        Aplica heurísticas de otimização em 3 passos conforme o enunciado:
        Passo 1: Heurística de Junção (álgebra inicial)
        Passo 2: Heurística de redução de tuplas (push selections)
        Passo 3: Heurística de redução de campos (push projections)
        """
        # Passo 2: Redução de tuplas
        step2 = self._apply_tuple_reduction(algebra_expr)

        # Passo 3: Redução de campos
        step3 = self._apply_field_reduction(step2)

        return step3

    def _apply_tuple_reduction(self, expr):
        if isinstance(expr, Projection):
            if isinstance(expr.child, Selection):
                # Empurrar seleção através das junções
                new_child = self._push_selection_to_tables(
                    expr.child.condition, expr.child.child
                )
                return Projection(expr.attributes, new_child)
            else:
                return expr
        return expr

    def _push_selection_to_tables(self, condition, join_expr):
        # Separar condições por AND
        conditions = re.split(r"\s+and\s+", condition, flags=re.IGNORECASE)

        # Classificar condições por tabela
        table_conditions = {}
        for cond in conditions:
            # Extrair tabela da condição (ex: tb1.id > 300)
            match = re.match(r"(\w+)\.", cond)
            if match:
                table = match.group(1)
                if table not in table_conditions:
                    table_conditions[table] = []
                table_conditions[table].append(cond)

        # Aplicar seleções recursivamente na árvore de junções
        return self._apply_selections_to_tree(join_expr, table_conditions)

    def _apply_selections_to_tree(self, expr, table_conditions):
        """
        Aplica seleções na árvore de junções
        """
        if isinstance(expr, Join):
            # Processar recursivamente ambos os lados
            left = self._apply_selections_to_tree(expr.left, table_conditions)
            right = self._apply_selections_to_tree(expr.right, table_conditions)
            return Join(expr.condition, left, right)

        elif isinstance(expr, Table):
            # Aplicar seleção se houver condições para esta tabela
            table_name = expr.name
            # Tentar match case-insensitive
            for key in table_conditions:
                if key.lower() == table_name.lower():
                    conds = table_conditions[key]
                    if conds:
                        condition_str = " AND ".join(conds)
                        return Selection(condition_str, expr)
            return expr

        else:
            return expr

    def _apply_field_reduction(self, expr):
        """
        Passo 3: Adiciona projeções (π) após seleções para reduzir campos
        """
        if isinstance(expr, Projection):
            final_attrs = expr.attributes
            new_child = self._add_projections_after_selections(
                expr.child, set(final_attrs)
            )
            return Projection(final_attrs, new_child)
        return expr

    def _add_projections_after_selections(self, expr, needed_attrs):
        if isinstance(expr, Join):
            # Coletar atributos necessários incluindo os do join
            join_attrs = self._extract_attributes_from_condition(expr.condition)
            all_needed = needed_attrs.union(set(join_attrs))

            # Determinar quais atributos vêm de cada lado
            left_tables = self._get_tables_from_expr(expr.left)
            right_tables = self._get_tables_from_expr(expr.right)

            left_attrs = []
            right_attrs = []

            for attr in all_needed:
                table = attr.split(".")[0] if "." in attr else ""
                if table.lower() in [t.lower() for t in left_tables]:
                    left_attrs.append(attr)
                elif table.lower() in [t.lower() for t in right_tables]:
                    right_attrs.append(attr)

            # Processar recursivamente
            left_child = self._add_projections_after_selections(
                expr.left, set(left_attrs)
            )
            right_child = self._add_projections_after_selections(
                expr.right, set(right_attrs)
            )

            return Join(expr.condition, left_child, right_child)

        elif isinstance(expr, Selection):
            # Primeiro processar o filho (que deve ser uma tabela)
            # NÃO adicionar projeção antes da tabela

            # Coletar atributos da condição também
            cond_attrs = self._extract_attributes_from_condition(expr.condition)
            all_attrs = needed_attrs.union(set(cond_attrs))

            # Construir: Projeção(Seleção(Tabela))
            result = Selection(expr.condition, expr.child)

            # Adicionar projeção APÓS a seleção
            if all_attrs:
                return Projection(sorted(list(all_attrs)), result)
            return result

        elif isinstance(expr, Table):
            # Tabela sem seleção: adicionar projeção direto
            if needed_attrs:
                return Projection(sorted(list(needed_attrs)), expr)
            return expr

        else:
            return expr

    def _extract_attributes_from_condition(self, condition):
        return re.findall(r"(\w+\.\w+)", condition)

    def _get_tables_from_expr(self, expr):
        if isinstance(expr, Table):
            return [expr.name]
        elif isinstance(expr, Join):
            return self._get_tables_from_expr(expr.left) + self._get_tables_from_expr(
                expr.right
            )
        elif isinstance(expr, Selection):
            return self._get_tables_from_expr(expr.child)
        elif isinstance(expr, Projection):
            return self._get_tables_from_expr(expr.child)
        else:
            return []
