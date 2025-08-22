import sqlite3
import tkinter as tk
from tkinter import messagebox
from datetime import datetime,timedelta

conexao=sqlite3.connect("documentos.db")
cursor=conexao.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS documentos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    validade DATE NOT NULL,
    observacao TEXT)""")
conexao.commit()

def salvar_documento():
    nome=entry_nome.get()
    validade=entry_validade.get()
    obs=entry_obs.get()
    if not nome or not validade:
        messagebox.showwarning("Atenção","Preencha todos os campos obrigatórios!")
        return

    try:
        datetime.strptime(validade,"%d/%m/%Y")
    except ValueError:
            print (
                messagebox.showerror("Erro","Data invalida! Use o formato DD/MM/AAAA."))
            return
    cursor.execute("INSERT INTO documentos(nome,validade,observacao)VALUES(?,?,?)",
    (nome,validade,obs))
    conexao.commit()
    messagebox.showinfo("Sucesso","Documento cadastrado!")
    listar_documentos()

def listar_documentos():
    lista.delete(0, tk.END)
    hoje=datetime.now()
    aviso_dias=30

    cursor.execute("SELECT nome,validade,observacao FROM documentos")
    for nome,validade,obs in cursor.fetchall():
        data_val=datetime.strptime(validade,"%d/%m/%Y")
        dias_restantes=(data_val-hoje).days

        if dias_restantes <0:
            status:"VENCIDO"
        elif dias_restantes<=aviso_dias:
            status=f"Vence em {dias_restantes} dias"
        else:
            status=f"OK ({dias_restantes} dias restantes)"
        lista.insert(tk.END,f"{nome}-{validade}-{status}-{obs}") 

janela=tk.Tk()
janela.title("Remenber That")
janela.geometry("600x400")
tk.Label(janela,text="Nome do Documento:").pack()
entry_nome=tk.Entry(janela,width=40)
entry_nome.pack()

tk.Label(janela,text="Data de Validade(DD/MM/AAAA):").pack()
entry_validade=tk.Entry(janela,width=20)
entry_validade.pack()

tk.Label(janela,text="Observação(opcional):").pack()
entry_obs=tk.Entry(janela,width=40)
entry_obs.pack()

tk.Button(janela,text="Salvar Documento",command=salvar_documento).pack(pady=5)

lista=tk.Listbox(janela,width=80,height=15)
lista.pack(pady=10)
listar_documentos()

janela.mainloop()







            






