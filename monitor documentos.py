import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime,timedelta
import openpyxl
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pywhatkit

conexao=sqlite3.connect("documentos.db")
cursor=conexao.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS documentos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    validade DATE NOT NULL,
    observacao TEXT,
    imagem TEXT,
    whatsapp TEXT)""")
conexao.commit()

def enviar_alerta_whatsapp(numero,mensagem):
    try:
        agora= datetime.now()
        hora = agora.hour
        minuto=agora.minute + 2

        pywhatkit.sendwhatmsg(numero, mensagem, hora, minuto)
        messagebox.showinfo("Whatsapp",f"Mensagem agendada para {numero}")
    except Exception as e:
        messagebox.showerror("Erro Whatsapp",f"Erro ao enviar:{e}")

def salvar_documento():
    nome=entry_nome.get()
    validade=entry_validade.get()
    obs=entry_obs.get()
    img= entry_imagem.get()
    numero=entry_whatsapp.get()

    if not nome or not validade:
        messagebox.showwarning("Atenção","Preencha todos os campos obrigatórios!")
        return

    try:
        datetime.strptime(validade,"%d/%m/%Y")
    except ValueError:
            print (
                messagebox.showerror("Erro","Data invalida! Use o formato DD/MM/AAAA."))
            return
    cursor.execute("INSERT INTO documentos(nome,validade,observacao,imagem, whatsapp)VALUES(?,?,?,?,?)",
    (nome,validade,obs,img,numero))
    conexao.commit()
    messagebox.showinfo("Sucesso","Documento cadastrado!")
    listar_documentos()

def listar_documentos():
    lista.delete(0, tk.END)
    hoje=datetime.now()
    aviso_dias=30

    cursor.execute("SELECT nome,validade,observacao,imagem,whatsapp FROM documentos")
    for nome,validade,obs,imagem,numero in cursor.fetchall():
        data_val=datetime.strptime(validade,"%d/%m/%Y")
        dias_restantes=(data_val-hoje).days

        if dias_restantes <0:
            status:f"VENCIDO"
            enviar_alerta_whatsapp(numero,f"O documento '{nome}' esta VENCIDO desde {validade}!")
        elif dias_restantes<=aviso_dias:
            status=f"Vence em {dias_restantes} dias"
            if dias_restantes <=5:
                enviar_alerta_whatsapp(numero,f"O documento '{nome}' vence em {dias_restantes} dias ({validade}).")
        else:
            status=f"OK ({dias_restantes} dias restantes)"
        lista.insert(tk.END,f"{nome}-{validade}-{status}-{obs}-{imagem}-WhatsApp:{numero}") 

def excluir_documento():
    try:
        selecionado=lista.get(lista.curselection())
        doc_id=selecionado.split(",")[0]
        cursor.execute("DELETE FROM documentos WHERE id=?",(doc_id,))
        conexao.commit()
        listar_documentos()
        messagebox.showinfo("Pronto","Documento excluido!")
    except:
        messagebox.showwarning("Aviso","Selecione um documento para excluir.")

def editar_documento():
    try:
        selecionado=lista.get(lista.curselection())
        doc_id=selecionado.split(",")[0]
        #obter dados atuais
        cursor.execute("SELECT nome,validade,observacao,imagem FROM documentos WHERE id=?",(doc_id,))
        nome,validade,obs,img=cursor.fetchone()

        edit_win=tk.Toplevel(janela)
        edit_win.title("Editar documento")

        tk.Label(edit_win, text="Nome:").pack()
        nome_entry = tk.Entry(edit_win,width=20)
        nome_entry.insert(0,nome)
        nome_entry.pack()

        tk.Label(edit_win,text="Validade(DD/MM/AAAA):").pack()
        validade_entry=tk.Entry(edit_win, width=20)
        validade_entry.insert(0,validade)
        validade_entry.pack()

        tk.Label(edit_win, text="Observação:").pack()
        obs_entry = tk.Entry(edit_win, width=40)
        obs_entry.insert(0, obs)
        obs_entry.pack()

        def salvar_edicao():
            novo_nome = nome_entry.get()
            nova_validade = validade_entry.get()
            nova_obs = obs_entry.get()
            cursor.execute("UPDATE documentos SET nome=?,validade=?,observacao=? WHERE id=?",
                           (novo_nome,nova_validade,nova_obs,doc_id))
            conexao.commit()
            listar_documentos()
            edit_win.destroy()
            messagebox.showinfo("Sucesso","Documentos atualizados!")

        tk.Button(edit_win, text="Salvar",
                  command=salvar_edicao).pack(pady=10)
    except:
        messagebox.showwarning("Aviso","Selecione um documento para editar.")

def exportar_excel():
    cursor.execute("SELECT nome, validade, observacao FROM documentos")
    docs = cursor.fetchall()

    if not docs:
        messagebox.showinfo("Info","Nenhum documento para exportar.")
        return

    wb=openpyxl.Workbook()
    ws=wb.active
    ws.title="Documentos"

    ws.append(["Nome", "Validade","Observação"])
    for doc in docs:
        ws.append(doc)

    wb.save("documentos_exportados.xlsx")
    messagebox.showinfo("Sucesso","Exportado para documentos_exportados.xlsx")

def selecionar_imagem():
    caminho=filedialog.askopenfilename(filetypes=[("imagens","*.jpg;*.png;*.jpeg")])
    if caminho:
        entry_imagem.delete(0,tk.END)
        entry_imagem.insert(0,caminho)


janela=tk.Tk()
janela.title("Remenber That")
janela.geometry("800x600")
tk.Label(janela,text="Nome do Documento:").pack()
entry_nome=tk.Entry(janela,width=40)
entry_nome.pack()

tk.Label(janela,text="Data de Validade(DD/MM/AAAA):").pack()
entry_validade=tk.Entry(janela,width=20)
entry_validade.pack()

tk.Label(janela,text="Observação(opcional):").pack()
entry_obs=tk.Entry(janela,width=40)
entry_obs.pack()

tk.Label(janela, text="Imagem do documento(opcional):").pack()
entry_imagem=tk.Entry(janela, width=40)
entry_imagem.pack()
tk.Button(janela, text="Selecionar Imagem",
          command=selecionar_imagem).pack(pady=5)

tk.Label(janela, text="Numero Whatsapp(+5511999999999)").pack()
entry_whatsapp=tk.Entry(janela, width=20)
entry_whatsapp.pack()

tk.Button(janela,text="Salvar Documento",command=salvar_documento).pack(pady=5)

frame=tk.Frame(janela)
frame.pack()

tk.Button(frame, text="Editar",
          command=editar_documento).grid(row=0, column=0,padx=5)
tk.Button(frame, text="Excluir",
          command=excluir_documento).grid(row=0,column=1, padx=5)
tk.Button(frame, text="Exportar Excel",
          command=exportar_excel).grid(row=0, column=2, padx=5)


lista=tk.Listbox(janela,width=100,height=15)
lista.pack(pady=10)
listar_documentos()

janela.mainloop()







            






