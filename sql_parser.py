import re

from metadata import (
    column_exists_in_table,
    table_exists,
)


class SQLParser:
    def __init__(self):
        self.valid_operators = ["=", ">", "<", "<=", ">=", "<>", "AND", "OR"]

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
                table, column = map(str.strip, col_expr.split("."))
                if not table_exists(table):
                    return (
                        False,
                        f"Tabela '{table}' não encontrada para coluna '{column}'",
                    )
                if not column_exists_in_table(table, column):
                    return False, f"Coluna '{column}' não existe na tabela '{table}'"
            else:
                column = col_expr.strip()
                found = any(column_exists_in_table(t, column) for t in all_tables)
                if not found:
                    return False, f"Coluna '{column}' não encontrada em nenhuma tabela"

        # Validar colunas em JOINs
        for join in parsed["joins"]:
            condition = re.sub(r"'(?:''|[^'])*'", "", join["condition"])
            columns_in_condition = re.findall(r"(\w+\.\w+)", condition)
            for col_expr in columns_in_condition:
                table, column = col_expr.split(".")
                if not table_exists(table):
                    return False, f"Tabela '{table}' não encontrada na condição JOIN"
                if not column_exists_in_table(table, column):
                    return (
                        False,
                        f"Coluna '{column}' não existe na tabela '{table}' (JOIN)",
                    )

        # Validar colunas no WHERE
        if parsed["where"]:
            where_cleaned = re.sub(r"'(?:''|[^'])*'", "", parsed["where"])
            columns_in_where = re.findall(
                r"\b([A-Za-z_]\w*\.[A-Za-z_]\w*)\b", where_cleaned
            )

            for col_expr in columns_in_where:
                table, column = col_expr.split(".")
                if not table_exists(table):
                    return False, f"Tabela '{table}' não encontrada na cláusula WHERE"
                if not column_exists_in_table(table, column):
                    return (
                        False,
                        f"Coluna '{column}' não existe na tabela '{table}' (WHERE)",
                    )

        return True, "Colunas válidas"

    def _validate_operators(self, parsed):
        if not parsed["where"]:
            return True, "Sem cláusula WHERE"

        where_clause = parsed["where"].strip()

        if re.search(r"[^<>!]=[^=]", where_clause):  # evita '=='
            pass
        if re.search(r"==|=>|=<|><", where_clause):
            return False, "Operador inválido encontrado na cláusula WHERE"

        if re.search(r"(=\s*[\w.]+)\s+(?=[\w.]+\s*=)", where_clause):
            return False, "Falta operador lógico (AND/OR) entre condições no WHERE"

        if re.search(r"\b(AND|OR)\s*$", where_clause, re.IGNORECASE):
            return False, "Cláusula WHERE termina incorretamente com operador lógico"

        conditions = re.split(r"\bAND\b|\bOR\b", where_clause, flags=re.IGNORECASE)
        conditions = [c.strip() for c in conditions if c.strip()]

        for cond in conditions:
            # Ignorar parênteses ou expressões compostas
            cond_clean = cond.strip("() ")

            # Verifica se contém pelo menos um operador válido
            op_match = re.search(r"(=|<>|<=|>=|<|>)", cond_clean)
            if not op_match:
                return (
                    False,
                    f"Falta operador de comparação em parte da cláusula WHERE: '{
                        cond_clean
                    }'",
                )

            # Operador presente, mas expressão incompleta (ex: coluna = )
            parts = re.split(r"(=|<>|<=|>=|<|>)", cond_clean)
            if len(parts) < 3 or not parts[0].strip() or not parts[2].strip():
                return (
                    False,
                    f"Expressão incompleta na cláusula WHERE: '{cond_clean}'",
                )

        return True, "Operadores e estrutura WHERE válidos"
