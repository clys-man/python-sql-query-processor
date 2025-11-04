from algebra_expressions import *


class AlgebraConverter:
    def convert(self, parsed_query):
        tables = parsed_query["from"] + [
            join["table"] for join in parsed_query["joins"]
        ]

        # Construir junções
        if len(tables) == 1:
            # Sem junções
            result = Table(tables[0])
        else:
            # Com junções
            result = self._build_joins(parsed_query)

        # Aplicar seleção (WHERE)
        if parsed_query["where"]:
            result = Selection(parsed_query["where"], result)

        # Aplicar projeção (SELECT)
        result = Projection(parsed_query["select"], result)

        return result

    def _build_joins(self, parsed_query):
        # Começar com a primeira tabela
        result = Table(parsed_query["from"][0])

        # Adicionar cada junção
        for join in parsed_query["joins"]:
            right_table = Table(join["table"])
            condition = join["condition"]
            result = Join(condition, result, right_table)

        return result
