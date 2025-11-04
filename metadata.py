SCHEMA = {
    "Categoria": {
        "columns": ["idCategoria", "Descricao"],
        "primary_key": "idCategoria",
    },
    "Produto": {
        "columns": [
            "idProduto",
            "Nome",
            "Descricao",
            "Preco",
            "QuantEstoque",
            "Categoria_idCategoria",
        ],
        "primary_key": "idProduto",
        "foreign_keys": {"Categoria_idCategoria": ("Categoria", "idCategoria")},
    },
    "TipoCliente": {
        "columns": ["idTipoCliente", "Descricao"],
        "primary_key": "idTipoCliente",
    },
    "Cliente": {
        "columns": [
            "idCliente",
            "Nome",
            "Email",
            "Nascimento",
            "Senha",
            "TipoCliente_idTipoCliente",
            "DataRegistro",
        ],
        "primary_key": "idCliente",
        "foreign_keys": {"TipoCliente_idTipoCliente": ("TipoCliente", "idTipoCliente")},
    },
    "TipoEndereco": {
        "columns": ["idTipoEndereco", "Descricao"],
        "primary_key": "idTipoEndereco",
    },
    "Endereco": {
        "columns": [
            "idEndereco",
            "EnderecoPadrao",
            "Logradouro",
            "Numero",
            "Complemento",
            "Bairro",
            "Cidade",
            "UF",
            "CEP",
            "TipoEndereco_idTipoEndereco",
            "Cliente_idCliente",
        ],
        "primary_key": "idEndereco",
        "foreign_keys": {
            "TipoEndereco_idTipoEndereco": ("TipoEndereco", "idTipoEndereco"),
            "Cliente_idCliente": ("Cliente", "idCliente"),
        },
    },
    "Telefone": {
        "columns": ["Numero", "Cliente_idCliente"],
        "primary_key": "Numero",
        "foreign_keys": {"Cliente_idCliente": ("Cliente", "idCliente")},
    },
    "Status": {"columns": ["idStatus", "Descricao"], "primary_key": "idStatus"},
    "Pedido": {
        "columns": [
            "idPedido",
            "Status_idStatus",
            "DataPedido",
            "ValorTotalPedido",
            "Cliente_idCliente",
        ],
        "primary_key": "idPedido",
        "foreign_keys": {
            "Status_idStatus": ("Status", "idStatus"),
            "Cliente_idCliente": ("Cliente", "idCliente"),
        },
    },
    "Pedido_has_Produto": {
        "columns": [
            "idPedidoProduto",
            "Pedido_idPedido",
            "Produto_idProduto",
            "Quantidade",
            "PrecoUnitario",
        ],
        "primary_key": "idPedidoProduto",
        "foreign_keys": {
            "Pedido_idPedido": ("Pedido", "idPedido"),
            "Produto_idProduto": ("Produto", "idProduto"),
        },
    },
}

# SCHEMA = {
#     "Tb1": {"columns": ["pk", "Nome", "id"], "primary_key": "pk"},
#     "Tb2": {
#         "columns": ["pk", "fk"],
#         "primary_key": "pk",
#         "foreign_keys": {"fk": ("Tb1", "pk")},
#     },
#     "Tb3": {
#         "columns": ["pk", "sal", "fk"],
#         "primary_key": "pk",
#         "foreign_keys": {"fk": ("Tb2", "pk")},
#     },
# }


def get_table_columns(table_name):
    table_name_normalized = normalize_table_name(table_name)
    if table_name_normalized in SCHEMA:
        return SCHEMA[table_name_normalized]["columns"]
    return None


def table_exists(table_name):
    return normalize_table_name(table_name) in SCHEMA


def column_exists_in_table(table_name, column_name):
    columns = get_table_columns(table_name)
    if columns:
        column_name_lower = column_name.lower()
        return any(col.lower() == column_name_lower for col in columns)
    return False


def normalize_table_name(table_name):
    table_name_lower = table_name.lower()
    for schema_table in SCHEMA.keys():
        if schema_table.lower() == table_name_lower:
            return schema_table
    return table_name


def get_foreign_keys(table_name):
    table_name_normalized = normalize_table_name(table_name)
    if table_name_normalized in SCHEMA:
        return SCHEMA[table_name_normalized].get("foreign_keys", {})
    return {}


def find_join_path(table1, table2):
    table1_norm = normalize_table_name(table1)
    table2_norm = normalize_table_name(table2)

    # Verifica se há relação direta
    fks1 = get_foreign_keys(table1_norm)
    for fk_col, (ref_table, ref_col) in fks1.items():
        if ref_table == table2_norm:
            return (table1_norm, fk_col, table2_norm, ref_col)

    # Verifica relação inversa
    fks2 = get_foreign_keys(table2_norm)
    for fk_col, (ref_table, ref_col) in fks2.items():
        if ref_table == table1_norm:
            return (table2_norm, fk_col, table1_norm, ref_col)

    return None
