# mini-ERP-simples

## 📦 Mini ERP – Estoque Simples

Este é um sistema **Mini ERP (Enterprise Resource Planning)** simples focado no **gerenciamento de estoque**. Foi desenvolvido em **Python** usando a biblioteca gráfica **Tkinter** para a interface de usuário (GUI) e **SQLite** para o banco de dados. Ele oferece funcionalidades básicas de cadastro, movimentação de estoque (entrada/saída) e ferramentas de análise de dados.

-----

🚀 Funcionalidades

  * **Cadastro de Produtos:** Insere novos itens com ID único, nome, categoria, preço e quantidade inicial.
  * **Movimentação de Estoque:** Realiza entradas ("E") e saídas ("S") de produtos, atualizando a quantidade em tempo real.
  * **Alertas de Estoque Baixo:** Exibe uma notificação se a quantidade de um produto cair para $\le 5$ unidades.
  * **Exclusão de Produtos:** Remove produtos e todo o seu histórico de movimentação.
  * **Exportação de Dados:** Gera um arquivo `estoque.xlsx` com o cadastro de produtos usando a biblioteca `pandas`.
  * **Análise Gráfica:** Utiliza `matplotlib` para gerar visualizações de dados:
      * **Gráfico Produto:** Quantidade em estoque por produto (gráfico de barras).
      * **Evolução Estoque:** Curva de estoque total ao longo do tempo.
      * **Curva ABC:** Análise da participação de cada produto no valor total do estoque, auxiliando na priorização de itens.

-----

## ⚙️ Pré-requisitos

Para executar o código, você precisa ter o **Python 3** instalado e as seguintes bibliotecas:

  * `tkinter` (Geralmente incluída na instalação padrão do Python)
  * `sqlite3` (Módulo padrão do Python)
  * `pandas`
  * `matplotlib`

Você pode instalar as bibliotecas necessárias usando `pip`:

```bash
pip install pandas matplotlib
```

-----

Estrutura do Banco de Dados (SQLite)

O sistema cria automaticamente um arquivo de banco de dados chamado `estoque.db` com duas tabelas principais:

### 1\. `produtos`

Armazena o cadastro e o estoque atual de cada item.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `TEXT` | **Chave Primária**, identificador único do produto. |
| `nome` | `TEXT` | Nome do produto. |
| `categoria` | `TEXT` | Categoria do produto. |
| `preco` | `REAL` | Preço unitário. |
| `quantidade` | `INTEGER` | Estoque atual. |

### 2\. `movimentacoes`

Registra todas as transações de entrada e saída.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `INTEGER` | Chave Primária, auto-incrementável. |
| `produto_id` | `TEXT` | ID do produto movimentado (Chave Estrangeira lógica para `produtos.id`). |
| `tipo` | `TEXT` | Tipo de movimento: **"E"** (Entrada) ou **"S"** (Saída). |
| `quantidade` | `INTEGER` | Quantidade movimentada. |
| `data` | `TEXT` | Data e hora da movimentação. |

-----

## 💻 Como Usar

1.  **Salve o código:** Salve o código Python como um arquivo, por exemplo, `ERP_simples.py`.
2.  **Execute o script:**
    ```bash
    python ERP_simples.py
    ```
3.  **Interface (GUI):**
      * **Cadastro:** Preencha os campos (ID, Nome, Categoria, Preço e Quantidade) no quadro **Cadastro** e clique em **Cadastrar**.
      * **Movimentação:** Selecione um produto na tabela, digite a quantidade no quadro **Movimentação** e clique em **Entrada** ou **Saída**.
      * **Relatórios:** Use os botões no rodapé para gerar a planilha Excel ou abrir os gráficos de análise.

-----

## 🧠 Análise de Código e Melhorias

### Ponto Forte: Estrutura Modular

O código está bem estruturado em funções separadas (`cadastrar`, `movimentar`, `exportar_excel`, etc.), o que facilita a leitura e manutenção.

### Sugestões de Melhoria

1.  **Validação de Dados:**

      * **Preço:** Adicionar validação mais robusta para garantir que o campo de preço seja um número real válido antes de tentar converter para `float(e_preco.get())`.
      * **Campos Vazios:** Impedir o cadastro ou movimentação se campos essenciais estiverem vazios.

2.  **Segurança e Concorrência:**

      * Para um uso mais profissional ou multiusuário, o `sqlite3` pode ser substituído por um banco de dados mais robusto (como PostgreSQL ou MySQL) e o acesso aos dados em funções como `movimentar` deve ser feito com **transações** mais seguras, especialmente em ambientes concorrentes.

3.  **Interface de Usuário:**

      * O uso de `float(qtd_raw)` seguido pela checagem `not qtd_float.is_integer()` na função `movimentar` é um pouco redundante. Poderia ser simplificado para uma única conversão para `int` após a substituição da vírgula.
      * Implementar **scrolbars** na `Treeview` para melhor visualização em listas longas.

4.  **Chave Estrangeira no DB:**

      * A tabela `movimentacoes` não define uma **Chave Estrangeira** (Foreign Key) formal para `produto_id`. Embora o `sqlite3` permita isso, adicionar a restrição `FOREIGN KEY(produto_id) REFERENCES produtos(id)` na criação da tabela aumentaria a integridade referencial do banco.
