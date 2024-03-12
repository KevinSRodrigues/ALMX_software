# Importações
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image
from customtkinter import CTkImage, CTkButton
import threading
import sys
import os
import sqlite3
import logging
import json
import requests

from Config import CONSTANTS, VERSION, Monitor, NAME_APP
###

# Config de caminhos
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Config log
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(r'log\logs.log')
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(log_format)
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)

class Main:

    def __init__(self):

        Scr_home()

class Api_sefaz:

    def Consulta_cnpj(self, widget, label, tela):

        cnpj = widget.get()

        try:

            if cnpj.isdigit():

                try:

                    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
                    querystring = {"token":"XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX","cnpj":"06990590000123","plugin":"RF"}
                    response = requests.request("GET", url, params=querystring)

                    resp = json.loads(response.text)

                    label.configure(text=resp["nome"], anchor="w")

                except:
                    messagebox.showerror("Erro", "CNPJ inválido")
                    tela.lift()

            else:
                messagebox.showerror("Erro", "CNPJ inválido")
                tela.lift()

        except:
            messagebox.showerror("Falha inesperada", "Houve uma falha inesperada, entre em contato com o suporte.")
            logger.error("Falha com a api sefaz", exc_info=True)

class Database:

    def Verify_preenchimento(self, table, listaArgs_obr, listaArgs_none, widgetText, widgetLabel, tela):

        tabela = table
        listArgs_dict = {}

        for widget, value in listaArgs_obr.items():

            res_value = value.get()
            if res_value == "":
                
                messagebox.showwarning("Campo vazio", "Preencha os campos obrigatórios.")
                tela.lift()
            
            else:

                listArgs_dict[widget] = res_value

                for widget, value in listaArgs_none.items():

                    res_value = value.get()
                    if res_value == "":

                        res_value = None
                        listArgs_dict[widget] = res_value

                    else:
                        listArgs_dict[widget] = res_value

                for widget, value in widgetText.items():

                    if value.get(1.0, index2=tk.END) == "" or value.get(1.0, index2=tk.END) == "\n":
                        listArgs_dict[widget] = None

                    else:
                        listArgs_dict[widget] = value.get(1.0, index2=tk.END)

                for widget, value in widgetLabel.items():

                    if value.cget("text") == "":
                        
                        messagebox.showwarning("Campo vazio", "Preencha os campos obrigatórios.")
                        tela.lift()

                    else:
                        listArgs_dict[widget] = value.cget("text")

        Database.Inserção_default(self, table=tabela, listArgs=listArgs_dict)

    def Consulta_default(self, arg):

        try:

            conn = sqlite3.connect(CONSTANTS.CONN_DB)
            cursor = conn.cursor()

            field = arg + "Name"

            cursor.execute(f"""SELECT {field} FROM {arg}""")
            data = cursor.fetchall()

        except:
            messagebox.showerror("Falha inesperada", "Houve uma falha inesperada, entre em contato com o suporte.")
            logger.error("Falha com a consulta default", exc_info=True)

        return data

    def Inserção_default(self, table, listArgs):

        try:

            conn = sqlite3.connect(CONSTANTS.CONN_DB)
            cursor = conn.cursor()

            stringFields = ""
            for field in listArgs.keys():
                stringFields += f"{field}, "

            stringFields = stringFields.rstrip(", ")

            stringValues = ""
            for value in listArgs.values():
                stringValues += f"{value}, "

            stringValues = stringValues.rstrip(", ")

            cursor.execute(f"""INSERT INTO {table} ({stringFields}) VALUES ({stringValues})""")
            conn.commit()
            messagebox.showinfo("Sucesso", f"{listArgs["ProductName"]} cadastrado com sucesso!")

        except:
            messagebox.showerror("Falha inesperada", "Houve uma falha inesperada, entre em contato com o suporte.")
            logger.error("Falha com a inserção default", exc_info=True)

class Módulo_estoque:

    class Visao_Geral:
    
        # Adiciona tabela à tela
        def Visao_geral(self, tela):

            tela.title(f"{NAME_APP} - Saldos estoque")

            try:

                headers = ["ID", "ProductName", "Descrição", "Medida", "Category", "Quantidade", "Fornecedor"]
                treeview = ttk.Treeview(
                    master=tela,
                    columns=headers,
                    show="headings"
                )

                treeview.place(relx=0.5, rely=0.95, relheight=0.8, relwidth=1, anchor=tk.S)

                style = ttk.Style()
                style.configure("Treeview", borderwidth=0)
                style.configure("Treeview.Heading", borderwidth=0)

                # Config cols
                for col in headers:
                    treeview.heading(col, text=col, anchor="w")
                    treeview.heading(headers[0], anchor="center")
                    treeview.heading(headers[3], anchor="center")
                    treeview.heading(headers[4], anchor="center")
                    treeview.heading(headers[5], anchor="center")
                    treeview.column(headers[0], width=3, anchor="center")
                    treeview.column(headers[3], width=4, anchor="center")
                    treeview.column(headers[4], width=6, anchor="center")
                    treeview.column(headers[5], width=10, anchor="center")

                var_filtro_key = tk.StringVar()

                # Filtro por palavras
                filtro_key_text = tk.Label(
                    master=tela,
                    text="Procurar por"
                )

                self.filtro_key = tk.Entry(
                    master=tela,
                    textvariable=var_filtro_key
                )

                icon_lupa_ = Image.open(os.path.join(script_dir, "..", "images", "lupa.png"))
                icon_lupa = CTkImage(dark_image=icon_lupa_, light_image=icon_lupa_, size=(15, 15))

                btn_procurar = CTkButton(
                    master=tela,
                    text="",
                    fg_color="transparent",
                    width=7.5,
                    height=7.5,
                    hover=False,
                    cursor="hand2",
                    image=icon_lupa,
                    command= lambda: Módulo_estoque.Visao_Geral.Infs_filtro(self, tree=treeview)
                )

                x = 0.075
                y = 0.14

                self.filtro_key.place(relx=x, rely=y, anchor=tk.SW)
                btn_procurar.place(relx=(x+0.105), rely=(y+0.002), anchor=tk.SW)
                filtro_key_text.place(relx=(x-0.035), rely=y, anchor=tk.S)
                ###

                Módulo_estoque.Visao_Geral.Infs_geral(self, tree=treeview)

            except:
                messagebox.showerror("Erro", "Houve uma falha inesperada, entre em contato com o suporte.")
                logger.error("Erro com a treeview", exc_info=True)

        def Infs_geral(self, tree):
            
            # Adicionar infs à tabela
            try:
                conn = sqlite3.connect(CONSTANTS.CONN_DB)
                cursor = conn.cursor()

                cursor.execute("""SELECT
                                        e.ProductID AS ID,
                                        e.ProductName AS Name,
                                        e.ProductDescription AS Description,
                                        un.UnitOfMeasureName AS UnitOfMeasureName,
                                        c.CategoryName AS CategoryName,
                                        e.StockQuantity,
                                        e.SupplierName
                                    FROM 
                                        Estoque e
                                    JOIN 
                                        Category c ON e.Category = c.CategoryID
                                    JOIN 
                                        UnitOfMeasure un ON e.UnitOfMeasure = un.UnitOfMeasureID
                            """)
                data = cursor.fetchall()

                tree.delete(*tree.get_children())
                for tupla in data:

                    tree.insert("", "end", values=tupla)

            except:
                messagebox.showerror("Falha", "Erro ao recuperar informações, entre em contato com o suporte.")
                logger.error("Erro ao recuperar informações do db", exc_info=True)

        def Infs_filtro(self, tree):

            tree_ = tree

            key = self.filtro_key.get()
            try:

                conn = sqlite3.connect(CONSTANTS.CONN_DB)
                cursor = conn.cursor()

                if len(key) != 0:

                    cursor.execute("""SELECT
                                            e.ProductID AS ID,
                                            e.ProductName AS Name,
                                            e.ProductDescription AS Description,
                                            un.UnitOfMeasureName AS UnitOfMeasureName,
                                            c.CategoryName AS CategoryName,
                                            e.StockQuantity,
                                            e.SupplierName
                                        FROM 
                                            Estoque e
                                        JOIN 
                                            Categorys c ON e.Category = c.CategoryID
                                        JOIN 
                                            UnitOfMeasure un ON e.UnitOfMeasure = un.UnitOfMeasureID
                                        WHERE e.ProductName LIKE ?
                                """, (f"{key}%",))
                    data = cursor.fetchall()

                    tree.delete(*tree.get_children())
                    for tupla in data:

                        tree.insert("", "end", values=tupla)

                else:
                    
                    Módulo_estoque.Visao_Geral.Infs_geral(self, tree=tree_)

            except:
                messagebox.showerror("Falha", "Houve um erro com o filtro, entre em contato com o suporte.")
                logger.error("Erro com os filtros", exc_info=True)

    class Cadastrar:

        def Scr_cadastrar(self):

            Tela_scr_cadastrar = tk.Tk()
            Tela_scr_cadastrar.title(f"{NAME_APP} - Cadastrar ProductName")
            Tela_scr_cadastrar.resizable(False, False)
            Tela_scr_cadastrar.geometry(f"600x500+{(self.width_screen-600)//2}+{(self.height_screen-(517+80))//2}") 

            # ProductName
            ProductName_txt = tk.Label(
                master=Tela_scr_cadastrar,
                text="ProductName*"
            )

            ProductName = tk.Entry(
                master=Tela_scr_cadastrar
            )

            ProductName_txt.place(x=28,  y=37, anchor=tk.SW)
            ProductName.place(x=30, y=57, relwidth=0.9, anchor=tk.SW)
            ###

            # Unidade medida
            UnitOfMeasure_txt = tk.Label(
                master=Tela_scr_cadastrar,
                text="Unidade de medida*"
            )

            UnitOfMeasure = ttk.Combobox(
                master=Tela_scr_cadastrar,
                values=Database.Consulta_default(self, arg="UnitOfMeasure")
            )

            UnitOfMeasure_txt.place(x=28, y=94, anchor=tk.SW)
            UnitOfMeasure.place(x=30, y=114, relwidth=0.434, anchor=tk.SW)
            ###

            ### Category
            Category_txt = tk.Label(
                master=Tela_scr_cadastrar,
                text="Catergoria*"
            )

            Category = ttk.Combobox(
                master=Tela_scr_cadastrar,
                values=Database.Consulta_default(self, arg="Category")
            )

            Category_txt.place(x=310, y=94, anchor=tk.SW)
            Category.place(x=310, y=114, relwidth=0.434, anchor=tk.SW)
            ###

            # Razão Social Fornecedor
            SupplierName_txt = tk.Label(
                master=Tela_scr_cadastrar,
                text="Razão social fornecedor"
            )

            SupplierName = tk.Label(
                master=Tela_scr_cadastrar,
                text=""
            )

            SupplierName_txt.place(x=310, y=151, anchor=tk.SW)
            SupplierName.place(x=310, y=171, relwidth=0.434, anchor=tk.SW)
            ###

            # CNPJ Fornecedor
            Cnpj_txt = tk.Label(
                master=Tela_scr_cadastrar,
                text="CNPJ Fornecedor*"
            )

            Cnpj = tk.Entry(
                master=Tela_scr_cadastrar
            )

            Cnpj_txt.place(x=28, y=151, anchor=tk.SW)
            Cnpj.place(x=30, y=171, relwidth=0.434, anchor=tk.SW)
            Cnpj.bind("<FocusOut>", lambda event=None: Api_sefaz.Consulta_cnpj(self, widget=Cnpj, label=SupplierName, tela=Tela_scr_cadastrar))
            ###

            # Obra
            Obra_txt = tk.Label(
                master=Tela_scr_cadastrar,
                text="Obra*"
            )

            Obra = ttk.Combobox(
                master=Tela_scr_cadastrar,
                values=Database.Consulta_default(self, arg="Obra")
            )

            Obra_txt.place(x=28, y=208, anchor=tk.SW)
            Obra.place(x=30, y=228, relwidth=0.255, anchor=tk.SW)
            ###

            # N° ordem de compra
            OrderNumber_txt = tk.Label(
                master=Tela_scr_cadastrar,
                text="N° ordem de compra*"
            )

            OrderNumber = tk.Entry(
                master=Tela_scr_cadastrar
            )

            OrderNumber_txt.place(x=222,  y=208, anchor=tk.SW)
            OrderNumber.place(x=224, y=228, relwidth=0.255, anchor=tk.SW)
            ###

            # N° NF-e
            NotaFiscal_txt = tk.Label(
                master=Tela_scr_cadastrar,
                text="N° NF-e*"
            )

            NotaFiscal = tk.Entry(
                master=Tela_scr_cadastrar
            )

            NotaFiscal_txt.place(x=415, y=208, anchor=tk.SW)
            NotaFiscal.place(x=417, y=228, relwidth=0.255, anchor=tk.SW)
            ###

            # Data validade
            ExpirationDate_txt = tk.Label(
                master=Tela_scr_cadastrar,
                text="Validade (dd-mm-yyyy)"
            )

            ExpirationDate = tk.Entry(
                master=Tela_scr_cadastrar
            )

            ExpirationDate_txt.place(x=28, y=265, anchor=tk.SW)
            ExpirationDate.place(x=30, y=285, relwidth=0.255, anchor=tk.SW)
            ###

            # Quantidade
            StockQuantity_txt = tk.Label(
                master=Tela_scr_cadastrar,
                text="Quantidade*"
            )

            StockQuantity = ttk.Entry(
                master=Tela_scr_cadastrar
            )

            StockQuantity_txt.place(x=222, y=265, anchor=tk.SW)
            StockQuantity.place(x=224, y=285, relwidth=0.255, anchor=tk.SW)
            ###

            # Código de barras
            Barcode_txt = tk.Label(
                master=Tela_scr_cadastrar,
                text="Código de barras"
            )

            Barcode = tk.Entry(
                master=Tela_scr_cadastrar
            )

            Barcode_txt.place(x=415, y=265, anchor=tk.SW)
            Barcode.place(x=417, y=285, relwidth=0.255, anchor=tk.SW)
            ###

            # Observações
            ProductDescription_txt = tk.Label(
                master=Tela_scr_cadastrar,
                text="Observações"
            )

            ProductDescription = tk.Text(
                master=Tela_scr_cadastrar,
                height=6
            )

            ProductDescription_txt.place(x=28, y=322, anchor=tk.SW)
            ProductDescription.place(x=30, y=324, relwidth=0.9, anchor=tk.NW)
            ###

            # Separator
            Separator = ttk.Separator(
                master=Tela_scr_cadastrar,
                orient="horizontal"
            )

            Separator.place(relx=0.5, rely=0.9, relwidth=1, anchor=tk.N)
            ###
            
            listaArgs_obr = {"ProductName": ProductName,
                             "UnitOfMeasure": UnitOfMeasure,
                             "Category": Category,
                             "Cnpj": Cnpj,
                             "Obra": Obra,
                             "StockQuantity": StockQuantity}
            
            listaArgs_none = {"OrderNumber": OrderNumber,
                              "NotaFiscal": NotaFiscal,
                              "ExpirationDate": ExpirationDate,
                              "Barcode": Barcode}

            # Botão gravar
            btnGravar = tk.Button(
                master=Tela_scr_cadastrar,
                text="Gravar",
                command= lambda event=None: Database.Verify_preenchimento(self, table="Estoque", listaArgs_obr=listaArgs_obr, listaArgs_none=listaArgs_none, widgetText={"ProductDescription": ProductDescription}, widgetLabel={"SupplierName": SupplierName}, tela=Tela_scr_cadastrar)
            )

            btnGravar.place(relx=0.95, rely=0.975, anchor=tk.SE)
            ###

            Tela_scr_cadastrar.mainloop()         

class Scr_home(Módulo_estoque):

    def __init__(self):

        self.width_screen, self.height_screen = Monitor.Monitor(self)
        self.Scr()

    def Scr(self):

        Tela_scr = tk.Tk()
        Tela_scr.title(f"{NAME_APP} - Home")
        Tela_scr.resizable(False, False)
        Tela_scr.geometry(f"1200x600+{(self.width_screen-1200)//2}+{(self.height_screen-(600+80))//2}")

        # Cor bg
        cor_bg = tk.Label(
            master=Tela_scr,
            background="#F0F0F0"
        )

        cor_bg.place(relheight=1, relwidth=1)
        ###

        # Menu
        menu_bar = tk.Menu(
            master=Tela_scr
        )

        menu_estoque = tk.Menu(
            master=menu_bar,
            tearoff=0
        )
        menu_estoque.add_command(label="Visão geral", command= lambda: Módulo_estoque.Visao_Geral.Visao_geral(self, tela=Tela_scr))
        menu_estoque.add_command(label="Cadastrar", command= lambda: Módulo_estoque.Cadastrar.Scr_cadastrar(self))
        menu_estoque.add_command(label="Alterar")
        menu_estoque.add_command(label="Excluir")
        menu_estoque.add_command(label="Relatório")
        menu_bar.add_cascade(label="Estoque", menu=menu_estoque)

        menu_ferramentas = tk.Menu(
            master=menu_bar,
            tearoff=0
        )
        menu_ferramentas.add_command(label="Visão geral")
        menu_ferramentas.add_command(label="Cadastrar")
        menu_ferramentas.add_command(label="Alterar")
        menu_ferramentas.add_command(label="Excluir")
        menu_ferramentas.add_command(label="Relatório")
        menu_bar.add_cascade(label="Ferramentas", menu=menu_ferramentas)

        menu_fiscal = tk.Menu(
            master=menu_bar,
            tearoff=0
        )
        menu_fiscal.add_command(label="Registrar movimentação")
        menu_fiscal.add_command(label="Relatório")
        menu_bar.add_cascade(label="Fiscal", menu=menu_fiscal)
        ###

        # Separator
        separator = ttk.Separator(
            master=Tela_scr,
            orient="horizontal"
        )
        
        separator.place(relx=0.5, rely=0.95, relwidth=1, anchor=tk.S)
        ###

        # Infs rodapé
        version = tk.Label(
            master=Tela_scr,
            text=f"{NAME_APP} - {VERSION}",
            foreground="#828282"
        )

        version.place(relx=0.99, rely=0.992, anchor=tk.SE)
        ###

        # Name host
        name_host = tk.Label(
            master=Tela_scr,
            text=f"Host: {CONSTANTS.MAQUINA}",
            foreground="#828282"
        )

        name_host.place(relx=1-0.99, rely=0.992, anchor=tk.SW)
        ###

        Tela_scr.config(menu=menu_bar)

        Tela_scr.mainloop()
