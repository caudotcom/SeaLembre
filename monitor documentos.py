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
'preciso logar em casa'