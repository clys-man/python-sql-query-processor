import re

from metadata import (
    column_exists_in_table,
    table_exists,
)


class SQLParser:
    def __init__(self):
        self.valid_operators = ["=", ">", "<", "<=", ">=", "<>", "AND"]

    def parse(self, sql_query):
        try:
            sql_query = self._normalize_query(sql_query)

            if not self._validate_basic_syntax(sql_query):
                return False, "Sintaxe SQL inválida", None

            parsed = self._extract_query_components(sql_query)

            if not parsed:
                return False, "Não foi possível fazer o parsing da consulta", None

            table_validation = self._validate_tables(parsed)
            if not table_validation[0]:
                return False, table_validation[1], None

            column_validation = self._validate_columns(parsed)
            if not column_validation[0]:
                return False, column_validation[1], None

            operator_validation = self._validate_operators(parsed)
            if not operator_validation[0]:
                return False, operator_validation[1], None

            return True, "Consulta válida", parsed

        except Exception as e:
            return False, f"Erro no parsing: {str(e)}", None

    def _normalize_query(self, query):
        query = re.sub(r"\s+", " ", query)
        query = query.strip()
        return query

    def _validate_basic_syntax(self, query):
        query_upper = query.upper()

        if "SELECT" not in query_upper or "FROM" not in query_upper:
            return False

        # SELECT deve vir antes de FROM
        select_pos = query_upper.index("SELECT")
        from_pos = query_upper.index("FROM")

        if select_pos >= from_pos:
            return False

        return True

    def _extract_query_components(self, query):
        """Extrai os componentes da consulta SQL"""
        try:
            parsed = {
                "select": [],
                "from": [],
                "joins": [],
                "where": None,
                "original": query,
            }

            # Padrão para extrair partes da consulta
            # SELECT ... FROM ... [JOIN ... ON ...] [WHERE ...]

            query_upper = query.upper()

            # Extrair SELECT
            select_start = query_upper.index("SELECT") + 6
            from_start = query_upper.index("FROM")
            select_clause = query[select_start:from_start].strip()

            # Processar colunas do SELECT
            parsed["select"] = [col.strip() for col in select_clause.split(",")]

            # Extrair FROM e JOINs
            from_clause = query[from_start:]

            # Encontrar WHERE se existir
            where_match = re.search(r"\bWHERE\b", from_clause, re.IGNORECASE)
            if where_match:
                where_start = where_match.start()
                where_clause = from_clause[where_start + 5 :].strip()
                parsed["where"] = where_clause
                from_clause = from_clause[:where_start]

            # Processar FROM e JOINs
            self._parse_from_joins(from_clause, parsed)

            return parsed

        except Exception as e:
            print(f"Erro ao extrair componentes: {e}")
            return None

    def _parse_from_joins(self, from_clause, parsed):
        from_clause = re.sub(r"\bFROM\b", "", from_clause, flags=re.IGNORECASE).strip()

        # Separar por JOIN
        parts = re.split(r"\bJOIN\b", from_clause, flags=re.IGNORECASE)

        # Primeira parte é a tabela FROM
        first_table = parts[0].strip()
        parsed["from"].append(first_table)

        # Processar JOINs
        for i in range(1, len(parts)):
            join_part = parts[i].strip()

            # Extrair tabela e condição ON
            on_match = re.search(r"\bON\b", join_part, re.IGNORECASE)
            if on_match:
                table = join_part[: on_match.start()].strip()
                condition = join_part[on_match.start() + 2 :].strip()

                parsed["joins"].append({"table": table, "condition": condition})

    def _validate_tables(self, parsed):
        for table in parsed["from"]:
            if not table_exists(table):
                return False, f"Tabela '{table}' não existe no esquema"

        # Validar tabelas dos JOINs
        for join in parsed["joins"]:
            table = join["table"]
            if not table_exists(table):
                return False, f"Tabela '{table}' não existe no esquema"

        return True, "Tabelas válidas"

    def _validate_columns(self, parsed):
        all_tables = parsed["from"] + [join["table"] for join in parsed["joins"]]

        # Validar colunas do SELECT
        for col_expr in parsed["select"]:
            if "." in col_expr:
                # Formato: tabela.coluna
                parts = col_expr.split(".")
                if len(parts) == 2:
                    table, column = parts[0].strip(), parts[1].strip()
                    if not table_exists(table):
                        return (
                            False,
                            f"Tabela '{table}' não encontrada para coluna '{column}'",
                        )
                    if not column_exists_in_table(table, column):
                        return (
                            False,
                            f"Coluna '{column}' não existe na tabela '{table}'",
                        )
            else:
                # Coluna sem qualificação - verificar se existe em alguma tabela
                column = col_expr.strip()
                found = False
                for table in all_tables:
                    if column_exists_in_table(table, column):
                        found = True
                        break
                if not found:
                    return (
                        False,
                        f"Coluna '{
                            column
                        }' não encontrada em nenhuma tabela da consulta",
                    )

        # Validar colunas nas condições JOIN
        for join in parsed["joins"]:
            condition = join["condition"]
            # Extrair colunas da condição (formato: tabela.coluna = tabela.coluna)
            columns_in_condition = re.findall(r"(\w+\.\w+)", condition)
            for col_expr in columns_in_condition:
                parts = col_expr.split(".")
                table, column = parts[0], parts[1]
                if not table_exists(table):
                    return False, f"Tabela '{table}' não encontrada na condição JOIN"
                if not column_exists_in_table(table, column):
                    return (
                        False,
                        f"Coluna '{column}' não existe na tabela '{
                            table
                        }' (condição JOIN)",
                    )

        # Validar colunas no WHERE
        if parsed["where"]:
            columns_in_where = re.findall(r"(\w+\.\w+)", parsed["where"])
            for col_expr in columns_in_where:
                parts = col_expr.split(".")
                table, column = parts[0], parts[1]
                if not table_exists(table):
                    return False, f"Tabela '{table}' não encontrada na cláusula WHERE"
                if not column_exists_in_table(table, column):
                    return (
                        False,
                        f"Coluna '{column}' não existe na tabela '{table}' (WHERE)",
                    )

        return True, "Colunas válidas"

    def _validate_operators(self, parsed):
        if parsed["where"]:
            where_clause = parsed["where"].upper()

            # Verificar operadores
            for op in ["<>", "<=", ">=", "=", "<", ">", "AND"]:
                if op in where_clause:
                    if op not in self.valid_operators:
                        return False, f"Operador '{op}' não é válido"

        return True, "Operadores válidos"
