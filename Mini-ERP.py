import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

con = sqlite3.connect("estoque.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    categoria TEXT,
    preco REAL,
    quantidade INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id TEXT,
    tipo TEXT,
    quantidade INTEGER,
    data TEXT
)
""")
con.commit()


def atualizar():
    tree.delete(*tree.get_children())
    for row in cur.execute("SELECT * FROM produtos"):
        tree.insert("", tk.END, values=row)

def cadastrar():
    try:
        cur.execute("INSERT INTO produtos VALUES (?, ?, ?, ?, ?)", (
            e_id.get(), e_nome.get(), e_cat.get(),
            float(e_preco.get()), int(e_qtd.get())
        ))
        con.commit()
        atualizar()
        messagebox.showinfo("OK", "Produto cadastrado!")
        checar_alertas()
    except:
        messagebox.showerror("Erro", "ID já existe ou dados inválidos.")


def movimentar(tipo):
    sel = tree.selection()
    if not sel:
        return messagebox.showwarning("Atenção", "Selecione um produto!")

    item = tree.item(sel)
    valores = item.get("values", [])

    if not valores:
        return messagebox.showwarning("Erro", "Falha ao obter dados do produto!")

    pid = valores[0]

    try:
        estoque = int(valores[4])
    except:
        try:
            estoque = int(float(valores[4]))
        except:
            estoque = 0

    qtd_raw = e_mov.get().strip()
    if qtd_raw == "":
        return messagebox.showwarning("Erro", "Digite a quantidade!")

    qtd_raw = qtd_raw.replace(",", ".")

    try:
        qtd_float = float(qtd_raw)
    except:
        return messagebox.showwarning("Erro", "Digite apenas números!")

    if not qtd_float.is_integer():
        return messagebox.showwarning("Erro", "A quantidade deve ser um número inteiro!")

    qtd = int(qtd_float)

    if qtd <= 0:
        return messagebox.showwarning("Erro", "A quantidade deve ser maior que zero!")

    if tipo == "S" and estoque < qtd:
        return messagebox.showerror("Erro", "Estoque insuficiente!")

    novo_estoque = estoque + qtd if tipo == "E" else estoque - qtd

    cur.execute("UPDATE produtos SET quantidade=? WHERE id=?", (novo_estoque, pid))
    cur.execute("""
        INSERT INTO movimentacoes (produto_id, tipo, quantidade, data)
        VALUES (?, ?, ?, ?)
    """, (pid, tipo, qtd, datetime.now().strftime("%Y-%m-%d %H:%M")))
    con.commit()

    e_mov.delete(0, tk.END)
    atualizar()
    checar_alertas()


def excluir_produto():
    selecionados = tree.selection()
    if not selecionados:
        messagebox.showwarning("Erro", "Selecione um produto!")
        return
    for selecionado in selecionados:
        item = tree.item(selecionado)
        id_prod = item['values'][0]
        try:
            cur.execute("DELETE FROM produtos WHERE id = ?", (id_prod,))
            cur.execute("DELETE FROM movimentacoes WHERE produto_id = ?", (id_prod,))
            con.commit()
            tree.delete(selecionado)
        except Exception as e:
            messagebox.showerror("Erro ao excluir produto: ", str(e))
    
    messagebox.showinfo("OK", "Produto(s) removido(s)!")


def exportar_excel():
    dados = list(cur.execute("SELECT * FROM produtos"))
    df = pd.DataFrame(dados, columns=["ID", "Nome", "Categoria", "Preço", "Quantidade"])
    df.to_excel("estoque.xlsx", index=False)
    messagebox.showinfo("OK", "Planilha gerada!")


def grafico_produto():
    dados = list(cur.execute("SELECT nome, quantidade FROM produtos"))
    if not dados:
        return messagebox.showwarning("Aviso", "Nada a mostrar")

    nomes = [d[0] for d in dados]
    qtds = [d[1] for d in dados]

    plt.bar(nomes, qtds)
    plt.xticks(rotation=45)
    plt.title("Estoque por Produto")
    plt.tight_layout()
    plt.show()


def evolucao_estoque():
    dados = list(cur.execute("SELECT tipo, quantidade, data FROM movimentacoes"))
    if not dados:
        return messagebox.showwarning("Aviso", "Nenhuma movimentação!")

    df = pd.DataFrame(dados, columns=["Tipo", "Qtd", "Data"])
    df["Data"] = pd.to_datetime(df["Data"])
    df["Qtd"] = df.apply(lambda x: x["Qtd"] if x["Tipo"] == "E" else -x["Qtd"], axis=1)

    curva = df.groupby("Data")["Qtd"].sum().cumsum()

    plt.plot(curva.index, curva.values)
    plt.title("Evolução do Estoque Total")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def curva_abc():
    dados = list(cur.execute("SELECT nome, preco, quantidade FROM produtos"))
    if not dados:
        return messagebox.showwarning("Aviso", "Nenhum produto!")

    df = pd.DataFrame(dados, columns=["Produto", "Preço", "Qtd"])
    df["Valor"] = df["Preço"] * df["Qtd"]
    df = df.sort_values("Valor", ascending=False)
    df["Acumulado"] = df["Valor"].cumsum() / df["Valor"].sum()

    plt.plot(df["Produto"], df["Acumulado"])
    plt.title("Curva ABC (Valor)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def checar_alertas():
    produtos = cur.execute("SELECT nome, quantidade FROM produtos").fetchall()
    for nome, qtd in produtos:
        if qtd <= 5:
            messagebox.showwarning(
                "Estoque Baixo",
                f"O produto '{nome}' está com estoque baixo ({qtd} unidades)!"
            )


app = tk.Tk()
app.title("Mini ERP – Estoque Simples")
app.geometry("950x550")
app.state("zoomed")


app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)
app.grid_columnconfigure(2, weight=3)
app.grid_rowconfigure(1, weight=1)


cad = tk.LabelFrame(app, text="Cadastro", padx=10, pady=10)
cad.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

tk.Label(cad, text="ID:").grid(row=0, column=0, sticky="w"); e_id = tk.Entry(cad); e_id.grid(row=0, column=1)
tk.Label(cad, text="Nome:").grid(row=1, column=0, sticky="w"); e_nome = tk.Entry(cad); e_nome.grid(row=1, column=1)
tk.Label(cad, text="Categoria:").grid(row=2, column=0, sticky="w"); e_cat = tk.Entry(cad); e_cat.grid(row=2, column=1)
tk.Label(cad, text="Preço:").grid(row=3, column=0, sticky="w"); e_preco = tk.Entry(cad); e_preco.grid(row=3, column=1)
tk.Label(cad, text="Quantidade:").grid(row=4, column=0, sticky="w"); e_qtd = tk.Entry(cad); e_qtd.grid(row=4, column=1)

tk.Button(cad, text="Cadastrar", command=cadastrar).grid(row=5, column=1, pady=10, sticky="e")


mov = tk.LabelFrame(app, text="Movimentação", padx=10, pady=10)
mov.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

tk.Label(mov, text="Quantidade:").grid(row=0, column=0)
e_mov = tk.Entry(mov)
e_mov.grid(row=0, column=1)

tk.Button(mov, text="Entrada", command=lambda: movimentar("E")).grid(row=1, column=0, pady=10)
tk.Button(mov, text="Saída", command=lambda: movimentar("S")).grid(row=1, column=1, pady=10)

colunas = ("ID", "Nome", "Categoria", "Preço", "Quantidade")
tree = ttk.Treeview(app, columns=colunas, show="headings")
for col in colunas:
    tree.heading(col, text=col)
tree.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)
atualizar()

footer = tk.Frame(app)
footer.grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")

for i in range(6):
    footer.grid_columnconfigure(i, weight=1)

tk.Button(footer, text="Planilha Excel", command=exportar_excel).grid(row=0, column=0, sticky="ew", padx=5)
tk.Button(footer, text="Gráfico Produto", command=grafico_produto).grid(row=0, column=1, sticky="ew", padx=5)
tk.Button(footer, text="Evolução Estoque", command=evolucao_estoque).grid(row=0, column=2, sticky="ew", padx=5)
tk.Button(footer, text="Curva ABC", command=curva_abc).grid(row=0, column=3, sticky="ew", padx=5)
tk.Button(footer, text="Excluir Selecionado", bg="red", fg="white",
          command=excluir_produto).grid(row=0, column=4, sticky="ew", padx=5)

checar_alertas()
app.mainloop()



