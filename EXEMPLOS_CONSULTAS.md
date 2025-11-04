# Exemplos de Consultas SQL para Teste

## ✅ Consultas Válidas

### 1. Consulta Simples sem JOIN

```sql
SELECT Cliente.Nome, Cliente.Email
FROM Cliente
WHERE Cliente.idCliente > 100
```

**Descrição**: Busca nome e email de clientes com ID maior que 100.

---

### 2. Consulta com 1 JOIN

```sql
SELECT Cliente.Nome, Pedido.DataPedido, Pedido.ValorTotalPedido
FROM Cliente
JOIN Pedido ON Cliente.idCliente = Pedido.Cliente_idCliente
WHERE Cliente.idCliente > 50
```

**Descrição**: Busca clientes e seus pedidos.

---

### 3. Consulta com 2 JOINs

```sql
SELECT Produto.Nome, Categoria.Descricao, Pedido_has_Produto.Quantidade
FROM Produto
JOIN Categoria ON Produto.Categoria_idCategoria = Categoria.idCategoria
JOIN Pedido_has_Produto ON Produto.idProduto = Pedido_has_Produto.Produto_idProduto
WHERE Produto.Preco > 50
```

**Descrição**: Busca produtos com suas categorias e quantidades em pedidos.

---

### 4. Consulta com 3 JOINs

```sql
SELECT Cliente.Nome, Pedido.ValorTotalPedido, Status.Descricao, Produto.Nome
FROM Cliente
JOIN Pedido ON Cliente.idCliente = Pedido.Cliente_idCliente
JOIN Status ON Pedido.Status_idStatus = Status.idStatus
JOIN Pedido_has_Produto ON Pedido.idPedido = Pedido_has_Produto.Pedido_idPedido
WHERE Pedido.ValorTotalPedido > 100
```

**Descrição**: Busca informações completas de pedidos.

---

### 5. Consulta com Múltiplas Condições WHERE

```sql
SELECT Produto.Nome, Produto.Preco, Produto.QuantEstoque
FROM Produto
WHERE Produto.Preco > 10 AND Produto.QuantEstoque > 0
```

**Descrição**: Busca produtos disponíveis com preço acima de 10.

---

### 6. Consulta com JOIN e Múltiplas Condições

```sql
SELECT Cliente.Nome, Pedido.DataPedido
FROM Cliente
JOIN Pedido ON Cliente.idCliente = Pedido.Cliente_idCliente
WHERE Cliente.idCliente > 100 AND Pedido.ValorTotalPedido > 200
```

**Descrição**: Busca clientes e pedidos que atendem múltiplas condições.

---

### 7. Consulta com Endereço

```sql
SELECT Cliente.Nome, Endereco.Cidade, Endereco.UF
FROM Cliente
JOIN Endereco ON Cliente.idCliente = Endereco.Cliente_idCliente
WHERE Endereco.UF = CE
```

**Descrição**: Busca clientes do Ceará.

---

### 8. Consulta com Telefone

```sql
SELECT Cliente.Nome, Telefone.Numero
FROM Cliente
JOIN Telefone ON Cliente.idCliente = Telefone.Cliente_idCliente
WHERE Cliente.idCliente > 0
```

**Descrição**: Busca clientes e seus telefones.

---

### 9. Consulta com TipoCliente

```sql
SELECT Cliente.Nome, TipoCliente.Descricao
FROM Cliente
JOIN TipoCliente ON Cliente.TipoCliente_idTipoCliente = TipoCliente.idTipoCliente
WHERE TipoCliente.idTipoCliente > 0
```

**Descrição**: Busca clientes e seus tipos.

---

### 10. Consulta Complexa - Produtos em Pedidos com Status

```sql
SELECT Produto.Nome, Pedido_has_Produto.Quantidade, Pedido_has_Produto.PrecoUnitario, Status.Descricao
FROM Produto
JOIN Pedido_has_Produto ON Produto.idProduto = Pedido_has_Produto.Produto_idProduto
JOIN Pedido ON Pedido_has_Produto.Pedido_idPedido = Pedido.idPedido
JOIN Status ON Pedido.Status_idStatus = Status.idStatus
WHERE Pedido_has_Produto.Quantidade > 1 AND Status.idStatus <> 5
```

**Descrição**: Busca produtos em pedidos com quantidade maior que 1 e status diferente de 5.

---

## ❌ Consultas Inválidas (para teste de validação)

### 11. Tabela Inexistente

```sql
SELECT Nome FROM TabelaInexistente WHERE id > 100
```

**Erro Esperado**: "Tabela 'TabelaInexistente' não existe no esquema"

---

### 12. Coluna Inexistente

```sql
SELECT Cliente.ColunaInvalida FROM Cliente
```

**Erro Esperado**: "Coluna 'ColunaInvalida' não existe na tabela 'Cliente'"

---

### 13. Sintaxe Incorreta - Sem FROM

```sql
SELECT Cliente.Nome WHERE Cliente.idCliente > 100
```

**Erro Esperado**: "Sintaxe SQL inválida"

---

### 14. JOIN sem ON

```sql
SELECT Cliente.Nome, Pedido.DataPedido
FROM Cliente
JOIN Pedido
WHERE Cliente.idCliente > 100
```

**Erro Esperado**: Parsing incorreto

---

### 15. Operador Inválido (se implementado)

```sql
SELECT Cliente.Nome FROM Cliente WHERE Cliente.idCliente LIKE teste
```

**Nota**: LIKE não está na lista de operadores válidos do trabalho

---

## 🎯 Casos de Teste Especiais

### 16. Case Insensitive

```sql
select cliente.nome from cliente where cliente.idcliente > 100
```

**Deve funcionar**: Sistema deve ignorar diferença entre maiúsculas e minúsculas.

---

### 17. Múltiplos Espaços

```sql
SELECT    Cliente.Nome    FROM    Cliente    WHERE    Cliente.idCliente   >   100
```

**Deve funcionar**: Sistema deve ignorar espaços extras.

---

### 18. Comparação com Igualdade

```sql
SELECT Produto.Nome FROM Produto WHERE Produto.idProduto = 10
```

---

### 19. Comparação com Diferente

```sql
SELECT Status.Descricao FROM Status WHERE Status.idStatus <> 5
```

---

### 20. Comparação com Menor ou Igual

```sql
SELECT Produto.Nome, Produto.Preco FROM Produto WHERE Produto.Preco <= 100
```

---
