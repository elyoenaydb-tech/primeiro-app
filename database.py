"""
database.py
Camada de acesso a dados do Service Clean.
Centraliza toda a interação com o SQLite para evitar conexões duplicadas
e manter as regras de persistência em um único lugar.
"""

import sqlite3
import bcrypt
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "service_clean.db")


class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._criar_tabelas()
        self._seed_usuario_teste()
        self._seed_profissionais()

    # ------------------------------------------------------------------ #
    # Estrutura
    # ------------------------------------------------------------------ #
    def _criar_tabelas(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                consentimento_lgpd INTEGER DEFAULT 1,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessao (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                email TEXT NOT NULL,
                lembrar INTEGER DEFAULT 0
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS profissionais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                avaliacao TEXT,
                preco_texto TEXT,
                preco_valor REAL NOT NULL,
                bairro TEXT,
                pix_key TEXT NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS disponibilidade (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profissional_id INTEGER NOT NULL,
                horario TEXT NOT NULL,
                ocupado INTEGER DEFAULT 0,
                FOREIGN KEY (profissional_id) REFERENCES profissionais(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS comentarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profissional_id INTEGER NOT NULL,
                texto TEXT NOT NULL,
                FOREIGN KEY (profissional_id) REFERENCES profissionais(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS agendamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_cliente TEXT NOT NULL,
                profissional_id INTEGER NOT NULL,
                disponibilidade_id INTEGER,
                status TEXT DEFAULT 'Aguardando pagamento',
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profissional_id) REFERENCES profissionais(id),
                FOREIGN KEY (disponibilidade_id) REFERENCES disponibilidade(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pagamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agendamento_id INTEGER NOT NULL,
                valor_total REAL NOT NULL,
                valor_comissao_app REAL NOT NULL,
                valor_profissional REAL NOT NULL,
                pix_txid TEXT,
                status TEXT DEFAULT 'pendente',
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agendamento_id) REFERENCES agendamentos(id)
            )
        """)
        self.conn.commit()

    def _seed_usuario_teste(self):
        """Garante que sempre exista um usuário de demonstração para testes rápidos."""
        try:
            senha_hash = bcrypt.hashpw("Senha123!".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            self.cursor.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                ("Usuário Teste", "teste@gmail.com", senha_hash),
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass  # já existe

    def _seed_profissionais(self):
        """Popula a tabela de profissionais na primeira execução (dados de exemplo)."""
        self.cursor.execute("SELECT COUNT(*) FROM profissionais")
        if self.cursor.fetchone()[0] > 0:
            return

        from dados_profissionais import PROFISSIONAIS_POR_CATEGORIA

        for categoria, lista in PROFISSIONAIS_POR_CATEGORIA.items():
            for prof in lista:
                self.cursor.execute(
                    """INSERT INTO profissionais
                       (nome, categoria, avaliacao, preco_texto, preco_valor, bairro, pix_key)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (prof["nome"], categoria, prof["avaliacao"], prof["preco"],
                     prof["preco_valor"], prof["bairro"], prof["pix_key"]),
                )
                profissional_id = self.cursor.lastrowid

                for horario in prof["horarios"]:
                    self.cursor.execute(
                        "INSERT INTO disponibilidade (profissional_id, horario) VALUES (?, ?)",
                        (profissional_id, horario),
                    )
                for comentario in prof["comentarios"]:
                    self.cursor.execute(
                        "INSERT INTO comentarios (profissional_id, texto) VALUES (?, ?)",
                        (profissional_id, comentario),
                    )
        self.conn.commit()

    # ------------------------------------------------------------------ #
    # Usuários
    # ------------------------------------------------------------------ #
    def criar_usuario(self, nome: str, email: str, senha: str) -> tuple[bool, str]:
        try:
            senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            self.cursor.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                (nome, email, senha_hash),
            )
            self.conn.commit()
            return True, "Conta criada com sucesso!"
        except sqlite3.IntegrityError:
            return False, "Já existe uma conta com este e-mail."

    def autenticar(self, email: str, senha: str) -> tuple[bool, str]:
        self.cursor.execute("SELECT nome, senha FROM usuarios WHERE email = ?", (email,))
        resultado = self.cursor.fetchone()
        if not resultado:
            return False, ""
        if bcrypt.checkpw(senha.encode("utf-8"), resultado["senha"].encode("utf-8")):
            return True, resultado["nome"]
        return False, ""

    # ------------------------------------------------------------------ #
    # Sessão ("Lembrar de mim")
    # ------------------------------------------------------------------ #
    def salvar_sessao(self, email: str):
        self.cursor.execute(
            "INSERT OR REPLACE INTO sessao (id, email, lembrar) VALUES (1, ?, 1)", (email,)
        )
        self.conn.commit()

    def limpar_sessao(self):
        self.cursor.execute("DELETE FROM sessao WHERE id = 1")
        self.conn.commit()

    def obter_usuario_lembrado(self):
        self.cursor.execute("SELECT email FROM sessao WHERE id = 1 AND lembrar = 1")
        resultado = self.cursor.fetchone()
        return resultado["email"] if resultado else None

    # ------------------------------------------------------------------ #
    # Profissionais / Disponibilidade / Comentários
    # ------------------------------------------------------------------ #
    def listar_profissoes(self):
        self.cursor.execute("SELECT DISTINCT categoria FROM profissionais ORDER BY categoria")
        return [row["categoria"] for row in self.cursor.fetchall()]

    def listar_profissionais_por_categoria(self, categoria: str):
        self.cursor.execute("SELECT * FROM profissionais WHERE categoria = ?", (categoria,))
        return self.cursor.fetchall()

    def obter_disponibilidade(self, profissional_id: int):
        self.cursor.execute(
            "SELECT * FROM disponibilidade WHERE profissional_id = ? AND ocupado = 0",
            (profissional_id,),
        )
        return self.cursor.fetchall()

    def obter_comentarios(self, profissional_id: int):
        self.cursor.execute(
            "SELECT texto FROM comentarios WHERE profissional_id = ?", (profissional_id,)
        )
        return [row["texto"] for row in self.cursor.fetchall()]

    def marcar_horario_ocupado(self, disponibilidade_id: int):
        self.cursor.execute(
            "UPDATE disponibilidade SET ocupado = 1 WHERE id = ?", (disponibilidade_id,)
        )
        self.conn.commit()

    # ------------------------------------------------------------------ #
    # Agendamentos
    # ------------------------------------------------------------------ #
    def criar_agendamento(self, email_cliente: str, profissional_id: int, disponibilidade_id: int) -> int:
        self.cursor.execute(
            """INSERT INTO agendamentos (email_cliente, profissional_id, disponibilidade_id)
               VALUES (?, ?, ?)""",
            (email_cliente, profissional_id, disponibilidade_id),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def atualizar_status_agendamento(self, agendamento_id: int, status: str):
        self.cursor.execute(
            "UPDATE agendamentos SET status = ? WHERE id = ?", (status, agendamento_id)
        )
        self.conn.commit()

    def listar_agendamentos(self, email_cliente: str):
        self.cursor.execute(
            """SELECT a.id, p.nome AS profissional, p.categoria, d.horario, a.status
               FROM agendamentos a
               JOIN profissionais p ON p.id = a.profissional_id
               LEFT JOIN disponibilidade d ON d.id = a.disponibilidade_id
               WHERE a.email_cliente = ?
               ORDER BY a.id DESC""",
            (email_cliente,),
        )
        return self.cursor.fetchall()

    # ------------------------------------------------------------------ #
    # Pagamentos
    # ------------------------------------------------------------------ #
    def registrar_pagamento(self, agendamento_id: int, valor_total: float,
                             valor_comissao_app: float, valor_profissional: float,
                             pix_txid: str, status: str):
        self.cursor.execute(
            """INSERT INTO pagamentos
               (agendamento_id, valor_total, valor_comissao_app, valor_profissional, pix_txid, status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (agendamento_id, valor_total, valor_comissao_app, valor_profissional, pix_txid, status),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def obter_pagamento_por_agendamento(self, agendamento_id: int):
        self.cursor.execute(
            "SELECT * FROM pagamentos WHERE agendamento_id = ? ORDER BY id DESC LIMIT 1",
            (agendamento_id,),
        )
        return self.cursor.fetchone()

    def fechar(self):
        try:
            self.conn.close()
        except Exception:
            pass
