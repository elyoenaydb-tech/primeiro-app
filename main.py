"""
main.py
Service Clean - App completo e funcional (ponto de entrada).

Uma única janela (CTk) que alterna entre todas as telas do fluxo:
  Login / Cadastro -> Catálogo -> Lista de Profissionais -> Perfil
  -> Checkout (Pagamento Pix com split automático) -> Pós-checkout
  -> Meus Agendamentos

Executar:
    pip install customtkinter bcrypt requests
    python main.py
"""

import re
import webbrowser
import customtkinter as ctk
from tkinter import messagebox

import config
from database import Database
import pagamento
import seguranca
import modulo_compartilhamento as compartilhamento

ctk.set_appearance_mode("light")

EMAIL_REGEX = re.compile(r'^[\w.\-]+@[\w.\-]+\.\w+$')


class ServiceCleanApp(ctk.CTk):
    """Janela única que gerencia a navegação entre todas as telas do app."""

    def __init__(self):
        super().__init__()

        self.title("Service Clean")
        self.geometry("480x720")
        self.resizable(False, False)
        self.configure(fg_color=config.COR_FUNDO)

        self.db = Database()
        self.usuario_logado = None       # (nome, email)
        self.agendamento_atual = None    # id do agendamento em andamento no checkout

        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.exibir_login()

    # ------------------------------------------------------------------ #
    # Utilidades de navegação
    # ------------------------------------------------------------------ #
    def limpar_tela(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def _ao_fechar(self):
        self.db.fechar()
        self.destroy()

    # ================= TELA: LOGIN ================= #
    def exibir_login(self):
        self.limpar_tela()
        self.geometry("400x640")

        ctk.CTkLabel(self.container, text="Service Clean",
                     font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
                     text_color=config.COR_MARROM).pack(pady=(50, 5))
        ctk.CTkLabel(self.container, text="Escolha profissionais e agende serviços",
                     font=ctk.CTkFont(size=13), text_color="#777777").pack(pady=(0, 25))

        self.lbl_status_login = ctk.CTkLabel(self.container, text="",
                                              font=ctk.CTkFont(size=12, weight="bold"),
                                              text_color=config.COR_ERRO)
        self.lbl_status_login.pack(pady=(0, 10))

        self.txt_email = ctk.CTkEntry(self.container, placeholder_text="Digite seu e-mail",
                                       width=300, height=45, border_color=config.COR_BORDA,
                                       fg_color=config.COR_CARD)
        self.txt_email.pack(pady=10)

        self.txt_senha = ctk.CTkEntry(self.container, placeholder_text="Digite sua senha", show="*",
                                       width=300, height=45, border_color=config.COR_BORDA,
                                       fg_color=config.COR_CARD)
        self.txt_senha.pack(pady=10)
        self.txt_senha.bind("<Return>", lambda e: self.executar_login())

        self.chk_lembrar = ctk.CTkCheckBox(self.container, text="Lembrar de mim",
                                            font=ctk.CTkFont(size=12), text_color="#555555",
                                            border_color=config.COR_BORDA,
                                            hover_color=config.COR_HOVER_CLARO,
                                            fg_color=config.COR_MARROM)
        self.chk_lembrar.pack(pady=(5, 20), padx=50, anchor="w")

        ctk.CTkButton(self.container, text="Entrar", command=self.executar_login,
                      width=300, height=48, font=ctk.CTkFont(size=16, weight="bold"),
                      fg_color=config.COR_MARROM, hover_color=config.COR_MARROM_HOVER,
                      text_color="#FFFFFF").pack(pady=10)

        ctk.CTkButton(self.container, text="Não tem uma conta? Cadastre-se",
                      font=ctk.CTkFont(size=13), text_color="#555555", fg_color="transparent",
                      hover_color=config.COR_HOVER_CLARO, command=self.exibir_cadastro).pack(pady=(15, 0))

        self._preencher_usuario_lembrado()

    def _preencher_usuario_lembrado(self):
        email_lembrado = self.db.obter_usuario_lembrado()
        if email_lembrado:
            self.txt_email.insert(0, email_lembrado)
            self.chk_lembrar.select()

    def executar_login(self):
        email = seguranca.sanitizar_entrada(self.txt_email.get()).lower()
        senha = self.txt_senha.get()

        if not email or not senha:
            self._erro_login("Por favor, preencha todos os campos.")
            return
        if not EMAIL_REGEX.match(email):
            self._erro_login("Formato de e-mail inválido (ex: nome@email.com).")
            return

        autenticado, nome = self.db.autenticar(email, senha)
        if not autenticado:
            self._erro_login("E-mail ou senha incorretos.")
            return

        if self.chk_lembrar.get() == 1:
            self.db.salvar_sessao(email)
        else:
            self.db.limpar_sessao()

        self.usuario_logado = (nome, email)
        self.exibir_catalogo_profissoes()

    def _erro_login(self, mensagem):
        self.lbl_status_login.configure(text_color=config.COR_ERRO, text=mensagem)

    # ================= TELA: CADASTRO ================= #
    def exibir_cadastro(self):
        self.limpar_tela()
        self.geometry("400x680")

        ctk.CTkButton(self.container, text="← Voltar", width=70, fg_color="transparent",
                      text_color=config.COR_MARROM, font=ctk.CTkFont(weight="bold"),
                      command=self.exibir_login).pack(anchor="w", padx=15, pady=(15, 0))

        ctk.CTkLabel(self.container, text="Criar Conta",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=config.COR_MARROM).pack(pady=(15, 20))

        self.lbl_status_cadastro = ctk.CTkLabel(self.container, text="",
                                                 font=ctk.CTkFont(size=12, weight="bold"),
                                                 text_color=config.COR_ERRO, wraplength=320)
        self.lbl_status_cadastro.pack(pady=(0, 10))

        self.txt_nome = ctk.CTkEntry(self.container, placeholder_text="Nome completo",
                                      width=300, height=45, border_color=config.COR_BORDA,
                                      fg_color=config.COR_CARD)
        self.txt_nome.pack(pady=8)

        self.txt_cad_email = ctk.CTkEntry(self.container, placeholder_text="E-mail",
                                           width=300, height=45, border_color=config.COR_BORDA,
                                           fg_color=config.COR_CARD)
        self.txt_cad_email.pack(pady=8)

        self.txt_cad_senha = ctk.CTkEntry(self.container, placeholder_text="Senha (letras e números)",
                                           show="*", width=300, height=45, border_color=config.COR_BORDA,
                                           fg_color=config.COR_CARD)
        self.txt_cad_senha.pack(pady=8)

        self.txt_cad_senha2 = ctk.CTkEntry(self.container, placeholder_text="Confirme a senha",
                                            show="*", width=300, height=45, border_color=config.COR_BORDA,
                                            fg_color=config.COR_CARD)
        self.txt_cad_senha2.pack(pady=8)
        self.txt_cad_senha2.bind("<Return>", lambda e: self.executar_cadastro())

        ctk.CTkLabel(self.container,
                     text="Seus dados são protegidos: a senha nunca é salva em texto puro.",
                     font=ctk.CTkFont(size=10), text_color="#999999",
                     wraplength=300).pack(pady=(4, 0))

        ctk.CTkButton(self.container, text="Cadastrar", command=self.executar_cadastro,
                      width=300, height=48, font=ctk.CTkFont(size=16, weight="bold"),
                      fg_color=config.COR_MARROM, hover_color=config.COR_MARROM_HOVER,
                      text_color="#FFFFFF").pack(pady=20)

    def executar_cadastro(self):
        nome = seguranca.sanitizar_entrada(self.txt_nome.get())
        email = seguranca.sanitizar_entrada(self.txt_cad_email.get()).lower()
        senha = self.txt_cad_senha.get()
        senha2 = self.txt_cad_senha2.get()

        if not nome or not email or not senha or not senha2:
            self._erro_cadastro("Preencha todos os campos.")
            return
        if not EMAIL_REGEX.match(email):
            self._erro_cadastro("Formato de e-mail inválido.")
            return

        senha_ok, motivo = seguranca.validar_forca_senha(senha)
        if not senha_ok:
            self._erro_cadastro(motivo)
            return
        if senha != senha2:
            self._erro_cadastro("As senhas não coincidem.")
            return

        sucesso, mensagem = self.db.criar_usuario(nome, email, senha)
        if not sucesso:
            self._erro_cadastro(mensagem)
            return

        messagebox.showinfo("Sucesso", "Conta criada com sucesso! Faça login para continuar.")
        self.exibir_login()

    def _erro_cadastro(self, mensagem):
        self.lbl_status_cadastro.configure(text_color=config.COR_ERRO, text=mensagem)

    # ================= TELA: CATÁLOGO DE PROFISSÕES ================= #
    def exibir_catalogo_profissoes(self):
        self.limpar_tela()
        self.geometry("480x700")

        barra_topo = ctk.CTkFrame(self.container, fg_color="transparent")
        barra_topo.pack(fill="x", padx=15, pady=(15, 0))

        nome_usuario = self.usuario_logado[0] if self.usuario_logado else ""
        ctk.CTkLabel(barra_topo, text=f"Olá, {nome_usuario.split(' ')[0]} 👋",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=config.COR_TEXTO).pack(side="left")

        ctk.CTkButton(barra_topo, text="Sair", width=55, height=28, fg_color="transparent",
                      text_color=config.COR_ERRO, hover_color=config.COR_HOVER_CLARO,
                      command=self.executar_logout).pack(side="right")
        ctk.CTkButton(barra_topo, text="📅 Agendamentos", width=130, height=28, fg_color="transparent",
                      text_color=config.COR_MARROM, hover_color=config.COR_HOVER_CLARO,
                      command=self.exibir_meus_agendamentos).pack(side="right", padx=6)

        ctk.CTkLabel(self.container, text="Service Clean",
                     font=ctk.CTkFont(family="Arial", size=26, weight="bold"),
                     text_color=config.COR_MARROM).pack(pady=(15, 5))
        ctk.CTkLabel(self.container, text="Selecione a categoria de serviço desejada",
                     font=ctk.CTkFont(size=12), text_color="#777777").pack(pady=(0, 15))

        scroll_frame = ctk.CTkScrollableFrame(self.container, width=420, height=480,
                                               fg_color="transparent")
        scroll_frame.pack(pady=5, fill="both", expand=True, padx=10)

        from dados_profissionais import PROFISSOES
        profissoes_com_prof = set(self.db.listar_profissoes())

        for profissao in PROFISSOES:
            tem_profissional = profissao in profissoes_com_prof
            btn = ctk.CTkButton(
                scroll_frame,
                text=profissao if tem_profissional else f"{profissao} (em breve)",
                font=ctk.CTkFont(size=15, weight="bold"),
                fg_color=config.COR_CARD if tem_profissional else "#EFEFEF",
                text_color=config.COR_TEXTO if tem_profissional else "#AAAAAA",
                hover_color=config.COR_HOVER_CLARO, border_color=config.COR_BORDA,
                border_width=1, height=55, anchor="w",
                state="normal" if tem_profissional else "disabled",
                command=lambda p=profissao: self.exibir_profissionais_perto(p),
            )
            btn.pack(pady=6, fill="x", padx=10)

    def executar_logout(self):
        self.usuario_logado = None
        self.exibir_login()

    # ================= TELA: LISTA DE PROFISSIONAIS ================= #
    def exibir_profissionais_perto(self, profissao):
        self.limpar_tela()

        barra_topo = ctk.CTkFrame(self.container, fg_color="transparent", height=40)
        barra_topo.pack(fill="x", pady=(15, 5), padx=10)

        ctk.CTkButton(barra_topo, text="← Voltar", width=70, fg_color="transparent",
                      text_color=config.COR_MARROM, font=ctk.CTkFont(weight="bold"),
                      command=self.exibir_catalogo_profissoes).pack(side="left")
        ctk.CTkLabel(barra_topo, text=profissao, font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=config.COR_TEXTO).pack(side="right", padx=15)

        lista_prestadores = self.db.listar_profissionais_por_categoria(profissao)

        if not lista_prestadores:
            ctk.CTkLabel(self.container,
                         text=f"Nenhum profissional de '{profissao}'\nencontrado perto de você no momento.",
                         font=ctk.CTkFont(size=14), text_color="#777777").pack(pady=100)
            return

        scroll_profissionais = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        scroll_profissionais.pack(fill="both", expand=True, padx=10, pady=10)

        for prof in lista_prestadores:
            card = ctk.CTkFrame(scroll_profissionais, fg_color=config.COR_CARD,
                                border_color=config.COR_BORDA, border_width=1, height=100)
            card.pack(fill="x", pady=8, padx=5)
            card.pack_propagate(False)

            foto_perfil = ctk.CTkFrame(card, width=50, height=50, fg_color=config.COR_HOVER_CLARO,
                                       corner_radius=25)
            foto_perfil.place(x=15, y=15)
            ctk.CTkLabel(foto_perfil, text=prof["nome"][:2].upper(),
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color="#777777").place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(card, text=prof["nome"], font=ctk.CTkFont(size=15, weight="bold"),
                        text_color=config.COR_TEXTO).place(x=80, y=12)
            ctk.CTkLabel(card, text=f"📍 {prof['bairro']}", font=ctk.CTkFont(size=11),
                        text_color="#777777").place(x=80, y=35)
            ctk.CTkLabel(card, text=f"{prof['avaliacao']} • {prof['preco_texto']}",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=config.COR_MARROM).place(x=80, y=55)

            ctk.CTkButton(card, text="Ver Perfil", width=80, height=30, fg_color=config.COR_MARROM,
                         hover_color=config.COR_MARROM_HOVER,
                         command=lambda p=prof: self.exibir_perfil_detalhado(p, profissao)
                         ).place(x=320, y=30)

    # ================= TELA: PERFIL DETALHADO ================= #
    def exibir_perfil_detalhado(self, prof, profissao_origem):
        self.limpar_tela()

        barra_topo = ctk.CTkFrame(self.container, fg_color="transparent")
        barra_topo.pack(fill="x", padx=10, pady=(15, 0))

        ctk.CTkButton(barra_topo, text="← Ver outros profissionais", fg_color="transparent",
                      text_color=config.COR_MARROM, font=ctk.CTkFont(weight="bold"),
                      command=lambda: self.exibir_profissionais_perto(profissao_origem)
                      ).pack(side="left", padx=5)
        ctk.CTkButton(barra_topo, text="🔗 Indicar", width=90, fg_color="transparent",
                      text_color=config.COR_MARROM, font=ctk.CTkFont(weight="bold"),
                      command=lambda: self.compartilhar_profissional(prof, profissao_origem)
                      ).pack(side="right", padx=5)

        foto_grande = ctk.CTkFrame(self.container, width=90, height=90, fg_color=config.COR_HOVER_CLARO,
                                   corner_radius=45)
        foto_grande.pack(pady=10)
        ctk.CTkLabel(foto_grande, text=prof["nome"][:2].upper(),
                    font=ctk.CTkFont(size=24, weight="bold"),
                    text_color="#777777").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.container, text=prof["nome"], font=ctk.CTkFont(size=22, weight="bold"),
                    text_color=config.COR_TEXTO).pack()
        ctk.CTkLabel(self.container,
                    text=f"{prof['avaliacao']} | Preço de referência: {prof['preco_texto']}",
                    font=ctk.CTkFont(size=13, weight="bold"), text_color=config.COR_MARROM).pack(pady=5)

        ctk.CTkLabel(self.container, text="📅 Horários Disponíveis",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=config.COR_TEXTO).pack(anchor="w", padx=25, pady=(15, 5))

        frame_horarios = ctk.CTkFrame(self.container, fg_color=config.COR_CARD,
                                      border_color=config.COR_BORDA, border_width=1)
        frame_horarios.pack(fill="x", padx=20, pady=5)

        disponibilidades = self.db.obter_disponibilidade(prof["id"])
        self.disponibilidade_selecionada = ctk.IntVar(
            value=disponibilidades[0]["id"] if disponibilidades else -1
        )

        if not disponibilidades:
            ctk.CTkLabel(frame_horarios, text="Sem horários livres no momento.",
                        font=ctk.CTkFont(size=12), text_color="#999999").pack(padx=15, pady=10)
        for disp in disponibilidades:
            ctk.CTkRadioButton(frame_horarios, text=disp["horario"],
                               variable=self.disponibilidade_selecionada, value=disp["id"],
                               fg_color=config.COR_MARROM, text_color=config.COR_TEXTO
                               ).pack(anchor="w", padx=15, pady=6)

        ctk.CTkLabel(self.container, text="💬 Comentários Recentes",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=config.COR_TEXTO).pack(anchor="w", padx=25, pady=(15, 5))

        scroll_comentarios = ctk.CTkScrollableFrame(self.container, height=100, fg_color="transparent")
        scroll_comentarios.pack(fill="x", padx=20)

        for coment in self.db.obter_comentarios(prof["id"]):
            box_coment = ctk.CTkFrame(scroll_comentarios, fg_color=config.COR_CARD,
                                      border_color=config.COR_BORDA, border_width=1)
            box_coment.pack(fill="x", pady=4)
            ctk.CTkLabel(box_coment, text=f'"{coment}"', font=ctk.CTkFont(size=12, slant="italic"),
                        text_color="#555555", wraplength=360, justify="left").pack(padx=10, pady=8)

        ctk.CTkButton(
            self.container, text=f"Ir para Pagamento  •  {prof['preco_texto']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=config.COR_MARROM, hover_color=config.COR_MARROM_HOVER, height=48,
            state="normal" if disponibilidades else "disabled",
            command=lambda: self.exibir_checkout(prof, profissao_origem),
        ).pack(fill="x", padx=20, pady=20)

    def compartilhar_profissional(self, prof, profissao_origem):
        texto = compartilhamento.gerar_texto_compartilhamento(
            prof["nome"], profissao_origem, prof["avaliacao"]
        )
        link = compartilhamento.gerar_link_whatsapp(texto)
        try:
            webbrowser.open(link)
        except Exception:
            pass
        self.clipboard_clear()
        self.clipboard_append(texto)
        messagebox.showinfo("Indicar profissional",
                             "Texto copiado e WhatsApp aberto para você enviar a indicação!")

    # ================= TELA: CHECKOUT / PAGAMENTO ================= #
    def exibir_checkout(self, prof, profissao_origem):
        if not self.usuario_logado:
            messagebox.showerror("Erro", "Você precisa estar logado para agendar.")
            return

        disp_id = self.disponibilidade_selecionada.get()
        if disp_id == -1:
            messagebox.showerror("Erro", "Selecione um horário disponível.")
            return

        self.limpar_tela()

        _, email_cliente = self.usuario_logado
        agendamento_id = self.db.criar_agendamento(email_cliente, prof["id"], disp_id)
        self.agendamento_atual = agendamento_id

        valor_comissao, valor_profissional = pagamento.calcular_split(prof["preco_valor"])

        ctk.CTkButton(self.container, text="← Cancelar", fg_color="transparent",
                      text_color=config.COR_ERRO, font=ctk.CTkFont(weight="bold"),
                      command=lambda: self.exibir_profissionais_perto(profissao_origem)
                      ).pack(anchor="w", padx=15, pady=(15, 0))

        ctk.CTkLabel(self.container, text="Confirmar Pagamento",
                    font=ctk.CTkFont(size=24, weight="bold"),
                    text_color=config.COR_MARROM).pack(pady=(15, 20))

        resumo = ctk.CTkFrame(self.container, fg_color=config.COR_CARD,
                              border_color=config.COR_BORDA, border_width=1)
        resumo.pack(fill="x", padx=25, pady=5)

        def linha(label, valor, destaque=False):
            f = ctk.CTkFrame(resumo, fg_color="transparent")
            f.pack(fill="x", padx=15, pady=6)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=13,
                        weight="bold" if destaque else "normal"),
                        text_color=config.COR_TEXTO).pack(side="left")
            ctk.CTkLabel(f, text=valor, font=ctk.CTkFont(size=13, weight="bold"),
                        text_color=config.COR_MARROM if destaque else "#777777").pack(side="right")

        linha("Profissional", prof["nome"])
        linha("Serviço", profissao_origem)
        linha("Valor do serviço (recebe o profissional)", f"R$ {valor_profissional:.2f}")
        linha("Taxa de serviço do app (10%)", f"R$ {valor_comissao:.2f}")
        linha("Total a pagar", f"R$ {prof['preco_valor']:.2f}", destaque=True)

        nota = "modo simulado — nenhuma cobrança real" if config.MODO_SIMULADO else "via Pix"
        ctk.CTkLabel(self.container, text=f"Pagamento {nota}. O valor é dividido automaticamente:\n"
                                          f"90% para o profissional, 10% para manutenção do app.",
                    font=ctk.CTkFont(size=11), text_color="#999999", wraplength=340,
                    justify="center").pack(pady=15)

        ctk.CTkButton(
            self.container, text=f"Pagar R$ {prof['preco_valor']:.2f} via Pix",
            font=ctk.CTkFont(size=16, weight="bold"), fg_color=config.COR_MARROM,
            hover_color=config.COR_MARROM_HOVER, height=48,
            command=lambda: self.confirmar_pagamento(prof, profissao_origem, disp_id),
        ).pack(fill="x", padx=25, pady=20)

    def confirmar_pagamento(self, prof, profissao_origem, disp_id):
        _, email_cliente = self.usuario_logado

        resultado = pagamento.processar_pagamento_pix(
            valor_total=prof["preco_valor"],
            pix_key_profissional=prof["pix_key"],
            nome_cliente=self.usuario_logado[0],
        )

        if not resultado.sucesso:
            messagebox.showerror("Pagamento não concluído", resultado.mensagem)
            return

        self.db.registrar_pagamento(
            agendamento_id=self.agendamento_atual,
            valor_total=resultado.valor_total,
            valor_comissao_app=resultado.valor_comissao_app,
            valor_profissional=resultado.valor_profissional,
            pix_txid=resultado.txid,
            status="confirmado",
        )
        self.db.marcar_horario_ocupado(disp_id)
        self.db.atualizar_status_agendamento(self.agendamento_atual, "Confirmado")

        self.exibir_pos_checkout(prof, profissao_origem, resultado)

    # ================= TELA: PÓS-CHECKOUT ================= #
    def exibir_pos_checkout(self, prof, profissao_origem, resultado: "pagamento.ResultadoPagamento"):
        self.limpar_tela()

        ctk.CTkLabel(self.container, text="✅", font=ctk.CTkFont(size=60)).pack(pady=(60, 10))
        ctk.CTkLabel(self.container, text="Agendamento Confirmado!",
                    font=ctk.CTkFont(size=22, weight="bold"),
                    text_color=config.COR_SUCESSO).pack(pady=(0, 10))
        ctk.CTkLabel(self.container,
                    text=f"{prof['nome']} ({profissao_origem}) foi notificado(a)\n"
                         f"e vai atender no horário combinado.",
                    font=ctk.CTkFont(size=13), text_color="#555555",
                    justify="center").pack(pady=(0, 20))

        info = ctk.CTkFrame(self.container, fg_color=config.COR_CARD,
                            border_color=config.COR_BORDA, border_width=1)
        info.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(info, text=f"ID da transação: {resultado.txid}",
                    font=ctk.CTkFont(size=11), text_color="#999999").pack(padx=15, pady=(10, 2))
        ctk.CTkLabel(info, text=f"Valor pago: R$ {resultado.valor_total:.2f}",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=config.COR_TEXTO).pack(padx=15, pady=2)
        ctk.CTkLabel(info,
                    text=f"Repasse ao profissional: R$ {resultado.valor_profissional:.2f}\n"
                         f"Taxa do app (10%): R$ {resultado.valor_comissao_app:.2f}",
                    font=ctk.CTkFont(size=11), text_color="#777777",
                    justify="left").pack(padx=15, pady=(2, 10))

        ctk.CTkButton(self.container, text="Ver Meus Agendamentos", height=45,
                      fg_color=config.COR_MARROM, hover_color=config.COR_MARROM_HOVER,
                      command=self.exibir_meus_agendamentos).pack(fill="x", padx=30, pady=(25, 8))
        ctk.CTkButton(self.container, text="Voltar ao Catálogo", height=40, fg_color="transparent",
                      text_color=config.COR_MARROM, hover_color=config.COR_HOVER_CLARO,
                      command=self.exibir_catalogo_profissoes).pack(fill="x", padx=30)

    # ================= TELA: MEUS AGENDAMENTOS ================= #
    def exibir_meus_agendamentos(self):
        self.limpar_tela()

        ctk.CTkButton(self.container, text="← Voltar", fg_color="transparent",
                      text_color=config.COR_MARROM, font=ctk.CTkFont(weight="bold"),
                      command=self.exibir_catalogo_profissoes).pack(anchor="w", padx=15, pady=(15, 0))

        ctk.CTkLabel(self.container, text="Meus Agendamentos",
                    font=ctk.CTkFont(size=22, weight="bold"),
                    text_color=config.COR_MARROM).pack(pady=(10, 15))

        _, email_cliente = self.usuario_logado
        agendamentos = self.db.listar_agendamentos(email_cliente)

        if not agendamentos:
            ctk.CTkLabel(self.container, text="Você ainda não tem agendamentos.",
                        font=ctk.CTkFont(size=13), text_color="#777777").pack(pady=60)
            return

        scroll = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=5)

        for ag in agendamentos:
            card = ctk.CTkFrame(scroll, fg_color=config.COR_CARD, border_color=config.COR_BORDA,
                                border_width=1)
            card.pack(fill="x", pady=6)
            ctk.CTkLabel(card, text=ag["profissional"], font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=config.COR_TEXTO).pack(anchor="w", padx=15, pady=(10, 0))
            ctk.CTkLabel(card, text=f"{ag['categoria']} • {ag['horario'] or '-'}",
                        font=ctk.CTkFont(size=12), text_color="#777777").pack(anchor="w", padx=15)
            cor_status = config.COR_SUCESSO if ag["status"] == "Confirmado" else config.COR_MARROM
            ctk.CTkLabel(card, text=f"Status: {ag['status']}",
                        font=ctk.CTkFont(size=12, weight="bold"), text_color=cor_status
                        ).pack(anchor="w", padx=15, pady=(0, 10))


if __name__ == "__main__":
    app = ServiceCleanApp()
    app.mainloop()
