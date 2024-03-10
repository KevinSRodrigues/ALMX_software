# Importações
from tkinter import messagebox
import sys
import os
import socket
import sqlite3
import logging
import threading

from Config import CONSTANTS, OBRAS
from Setup import Main
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

# Host name
host = socket.gethostname()

class Verify:

    def __init__(self):

        CONSTANTS.MAQUINA = host
        
        thread_verify = threading.Thread(target=self.Verify)
        thread_verify.start()

    def Verify(self):
        
        try:
            if os.path.exists(os.path.join(script_dir, '..\\db', f'{host}_prod.db')):
                db = os.path.join(script_dir, '..\\db', f'{host}_prod.db')
                CONSTANTS.CONN_DB = db
                logger.info(f"Database encontrado {db}")
                Main()
            else:
                self.Create_database()

        except:
            messagebox.showerror("Erro", "Houve um erro inesperado, entre em contato com o suporte.")
            logger.critical("Erro crítico", exc_info=True)
            sys.exit()

    def Create_database(self):

        try:
            conn = sqlite3.connect(os.path.join(script_dir, '..\\db', f'{host}_prod.db'))
            db = os.path.join(script_dir, '..\\db', f'{host}_prod.db')
            CONSTANTS.CONN_DB = db
            cursor = conn.cursor()
        except:
            logger.error("Erro ao conectar ao db", exc_info=True)
            messagebox.showerror("Erro de conexão", "Erro ao conectar ao banco de dados, entre em contato com o suporte.")

        try:
            # Criar tabela Obra
            cursor.execute("""CREATE TABLE Obra (
                    ObraID INTEGER PRIMARY KEY,
                    ObraName VARCHAR(255) NOT NULL
            )""")

            # Inserir as Obra na tabela Obra
            for obra in OBRAS:
                cursor.execute("INSERT INTO Obra (ObraName) VALUES (?)", (obra,))

            # Criar tabela Status
            cursor.execute("""CREATE TABLE Status (
                        StatusID INTEGER PRIMARY KEY,
                        StatusName VARCHAR(50) NOT NULL
            )""")

            # Inserir Status na tabela Status
            values = ["Em Estoque",
                    "Em Trânsito",
                    "Em Manutenção/Reparo",
                    "Fora de estoque",
                    "Aguardando conferência",
                    "Alugado",
                    "Emprestado"]   
            for status in values:
                cursor.execute("INSERT INTO Status(StatusName) VALUES (?)", (status,))

            # Criar tabela Category
            cursor.execute("""CREATE TABLE Category (
                        CategoryID INTEGER PRIMARY KEY,
                        CategoryName VARCHAR(255) NOT NULL
            )""")

            # Inserir Category na tabela Category
            values = ["Hidráulica",
                    "Elétrica",
                    "Ferramental",
                    "Acabamento",
                    "Pintura",
                    "Epi",
                    "Uso-consumo",
                    "Informática",
                    "Escritório",
                    "Ar-condicionado",
                    "Não-provisionado",
                    "Terceirizado"]
            for categ in values:
                cursor.execute("INSERT INTO Category(CategoryName) VALUES (?)", (categ,))

            # Criar tabela UnMedida
            cursor.execute("""CREATE TABLE UnMedida (
                        UnMedidaID INTEGER PRIMARY KEY,
                        UnMedidaName CHAR(4) NOT NULL
            )""")

            # Inserir Unidades de medida na tabela UnMedida
            values = ["m",
                    "cm",
                    "mm",
                    "m2",
                    "m3",
                    "L",
                    "kg",
                    "gr",
                    "Ton",
                    "A",
                    "V",
                    "kW",
                    "W",
                    "Par",
                    "Kit",
                    "Sc",
                    "Kit"]
            for medida in values:
                cursor.execute("INSERT INTO UnMedida(UnMedidaName) VALUES (?)", (medida,))

            # Criar tabela Estoque
            cursor.execute("""CREATE TABLE Estoque (
                        ProductID INTEGER PRIMARY KEY,
                        OrderNumber INT,
                        NotaFiscal INT,
                        ProductName VARCHAR(255) NOT NULL,
                        ProductDescription TEXT,
                        UnitOfMeasure INT NOT NULL,
                        StockQuantity FLOAT NOT NULL,
                        Category INT NOT NULL, 
                        SupplierCNPJ INT(14) NOT NULL, 
                        SupplierName VARCHAR(255) NOT NULL, 
                        ExpirationDate DATE, 
                        ProductStatus INT NOT NULL, 
                        LastUpdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                        Barcode TEXT UNIQUE,
                        Obra INT NOT NULL, 
                        FOREIGN KEY (ProductStatus) REFERENCES Status(StatusID),
                        FOREIGN KEY (Category) REFERENCES Category(CategoryID),
                        FOREIGN KEY (UnitOfMeasure) REFERENCES UnMedida(UnMedidaID),
                        FOREIGN KEY (Obra) REFERENCES Obra(ObraID)
            )""")

            # Inserir Produtos teste na tabela Estoque
            sql = "INSERT INTO Estoque(ProductName, ProductDescription, UnitOfMeasure, StockQuantity, Category, SupplierCNPJ, SupplierName, ProductStatus, Obra) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            values = [("Tênis", "Vermelho", 1, 20, 1, 12345678912345, "Exemplo", 1, 1,),
                    ("Calça", "Jeans", 2, 53, 2, 12345678912345, "Exemplo", 2, 2,),
                    ("Tênis", "Vermelho", 1, 20, 1, 12345678912345, "Exemplo", 1, 3,),
                    ("Calça", "Jeans", 2, 53, 2, 12345678912345, "Exemplo", 2, 4,),
                    ("Calça", "Jeans", 2, 53, 2, 12345678912345, "Exemplo", 2, 5,)]
            cursor.executemany(sql, values)

            # Criar tabela Ferramentas
            cursor.execute("""CREATE TABLE Ferramentas (
                        ToolsID INTEGER PRIMARY KEY,
                        ToolsName VARCHAR(255) NOT NULL,
                        ToolsDescription TEXT,
                        UnitOfMeasure CHAR(3) NOT NULL,
                        StockQuantity FLOAT NOT NULL,
                        Patrimony INT NOT NULL,
                        Category VARCHAR(255) NOT NULL,
                        Supplier VARCHAR(255) NOT NULL,
                        ExpirationDate DATE,
                        ProductStatus INT NOT NULL,
                        LastUpdate TIMESTAMP NOT NULL,
                        FOREIGN KEY (ProductStatus) REFERENCES Status(StatusID)
            )""")

            # Criar tabela Fiscal
            cursor.execute("""CREATE TABLE Fiscal (
                        FiscalID INTEGER PRIMARY KEY,
                        nNotaFiscal INT NOT NULL,
                        dtEmissao DATE NOT NULL,
                        hrEmissao TIME NOT NULL,
                        SupplierCNPJ INT NOT NULL,
                        SupplierName VARCHAR(255) NOT NULL,
                        LastUpdate TIMESTAMP NOT NULL
            )""")

            # Salvando as alterações
            conn.commit()
            logger.info("Database e tabelas criados com sucesso!")
            Main()
        
        except:
            messagebox.showerror("Erro", "Houve uma falha inesperada, entre em contato com o suporte.")
            logger.error("Erro com a criação do database", exc_info=True)

if __name__ == "__main__":
    Verify()