import flet as ft

# 1. BANCO DE DADOS SIMULADO (Mock Data)
PROFISSIONAIS = [
    {
        "id": 1,
        "nome": "Carlos Silva",
        "area": "Encanador",
        "preco": 100.0,
        "localizacao": "São Paulo",
        "foto": "https://unsplash.com",
        "habilidades": "Vazamentos, Reparos hidráulicos urgentes, Desentupimento residencial.",
        "avaliacao": 4.8,
        "comentarios": [
            {"usuario": "Marcos A.",
             "texto": "Excelente profissional! Chegou no horário e resolveu o vazamento rápido."},
            {"usuario": "Julia F.", "texto": "Muito limpo e educado. Preço justo."}
        ]
    },
    {
        "id": 2,
        "nome": "Ana Oliveira",
        "area": "Eletricista",
        "preco": 150.0,
        "localizacao": "Campinas",
        "foto": "https://unsplash.com",
        "habilidades": "Instalações elétricas internas, Padrão de energia, Manutenção de quadros.",
        "avaliacao": 4.9,
        "comentarios": [
            {"usuario": "Roberto C.", "texto": "Instalou o chuveiro e refez a fiação com muita técnica. Recomendo!"}
        ]
    },
    {
        "id": 3,
        "nome": "Marcos Souza",
        "area": "Pintor",
        "preco": 80.0,
        "localizacao": "Santos",
        "foto": "https://unsplash.com",
        "habilidades": "Pintura residencial interna, Grafiato, Texturas e Verniz.",
        "avaliacao": 4.5,
        "comentarios": [
            {"usuario": "Fernanda M.", "texto": "Pintou minha sala perfeitamente, muito caprichoso."}
        ]
    }
]


def main(page: ft.Page):
    # Configurações globais da página (Cores Neutras)
    page.title = "ServiceClean Pro"
    page.bgcolor = "#F8F9FA"
    page.padding = 20
    page.scroll = "adaptive"

    # Estado global do aplicativo
    profissional_selecionado = None

    # --- TELA: CENTRAL DE SUPORTE ---
    def show_suporte_screen():
        page.clean()
        page.horizontal_alignment = "start"
        page.vertical_alignment = "start"
        page.floating_action_button = None

        chat_historico = ft.Column(scroll="always", height=300, spacing=10)
        chat_historico.controls.append(
            ft.Container(
                content=ft.Text("🤖 Suporte: Olá! Como posso ajudar você hoje?", color="#212529"),
                padding=10, bgcolor="#E9ECEF", border_radius=8
            )
        )
        input_msg = ft.TextField(hint_text="Digite sua dúvida aqui...", expand=True, bgcolor="#FFFFFF")

        def enviar_mensagem_suporte(e):
            if input_msg.value:
                chat_historico.controls.append(
                    ft.Container(
                        content=ft.Text(f"👤 Você: {input_msg.value}", color="#FFFFFF"),
                        padding=10, bgcolor="#212529", border_radius=8, alignment=ft.alignment.center_right
                    )
                )
                chat_historico.controls.append(
                    ft.Container(
                        content=ft.Text(
                            "🤖 Suporte: Entendido! Nossa equipe de segurança monitora as transações do Mercado Pago para garantir seu split de 10% e 90%.",
                            color="#212529"),
                        padding=10, bgcolor="#E9ECEF", border_radius=8
                    )
                )
                input_msg.value = ""
                page.update()

        page.add(
            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_welcome_screen()),
            ft.Text("Central de Suporte", size=24, weight=ft.FontWeight.BOLD, color="#212529"),
            ft.Container(content=chat_historico, padding=15, bgcolor="#FFFFFF", border_radius=12, expand=True),
            ft.Row([input_msg, ft.IconButton(ft.Icons.SEND, icon_color="#212529", on_click=enviar_mensagem_suporte)])
        )
        page.update()

    # --- TELA: TRABALHE CONOSCO ---
    def show_trabalhe_conosco_screen():
        page.clean()
        page.horizontal_alignment = "start"
        page.vertical_alignment = "start"
        page.floating_action_button = None

        nome_f = ft.TextField(label="Nome Completo", bgcolor="#FFFFFF")
        area_f = ft.TextField(label="Área de Atuação", bgcolor="#FFFFFF")
        preco_f = ft.TextField(label="Preço por Hora / Consulta (R$)", bgcolor="#FFFFFF")
        local_f = ft.TextField(label="Sua Cidade / Localização", bgcolor="#FFFFFF")
        hab_f = ft.TextField(label="Suas Habilidades", multiline=True, min_lines=2, bgcolor="#FFFFFF")

        def salvar_profissional(e):
            if nome_f.value and area_f.value and preco_f.value:
                PROFISSIONAIS.append({
                    "id": len(PROFISSIONAIS) + 1,
                    "nome": nome_f.value,
                    "area": area_f.value,
                    "preco": float(preco_f.value),
                    "localizacao": local_f.value,
                    "foto": "https://unsplash.com",
                    "habilidades": hab_f.value,
                    "avaliacao": 5.0,
                    "comentarios": []
                })
                page.snack_bar = ft.SnackBar(ft.Text("Perfil publicado com sucesso!"), bgcolor="#198754")
                page.snack_bar.open = True
                show_welcome_screen()

        page.add(
            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_welcome_screen()),
            ft.Text("Trabalhe Conosco", size=24, weight=ft.FontWeight.BOLD, color="#212529"),
            ft.Text("Cadastre seu perfil profissional:", size=14, color="#6C757D"),
            nome_f, area_f, preco_f, local_f, hab_f,
            ft.ElevatedButton("Cadastrar Meu Perfil", width=float("inf"),
                              style=ft.ButtonStyle(bgcolor="#212529", color="#FFFFFF"), on_click=salvar_profissional)
        )
        page.update()

    # --- TELA: LISTAGEM ---
    def show_home_screen():
        page.clean()
        page.floating_action_button = None
        lista_layout = ft.Column(spacing=15)
        lista_ordenada = sorted(PROFISSIONAIS, key=lambda x: x["preco"])

        for pro in lista_ordenada:
            lista_layout.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Image(src=pro["foto"], width=60, height=60, border_radius=30, fit="cover"),
                        ft.Column([
                            ft.Text(pro["nome"], weight=ft.FontWeight.BOLD, color="#212529", size=16),
                            ft.Text(pro["area"], color="#6C757D", size=14),
                            ft.Text(f"R$ {pro['preco']:.2f}", weight=ft.FontWeight.W_500, color="#212529")
                        ], expand=True),
                        ft.ElevatedButton(
                            "Ver Perfil",
                            style=ft.ButtonStyle(bgcolor="#212529", color="#FFFFFF"),
                            on_click=lambda e, p=pro: show_perfil_screen(p)
                        )
                    ]),
                    padding=15, bgcolor="#FFFFFF", border_radius=10,
                    border=ft.Border(top=ft.BorderSide(1, "#E9ECEF"), bottom=ft.BorderSide(1, "#E9ECEF"),
                                     left=ft.BorderSide(1, "#E9ECEF"), right=ft.BorderSide(1, "#E9ECEF"))
                )
            )

        page.add(
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_welcome_screen()),
                ft.Text("Profissionais Disponíveis", size=22, weight=ft.FontWeight.BOLD, color="#212529")
            ]),
            ft.Text("Exibindo os menores preços primeiro:", size=13, color="#6C757D"),
            ft.Divider(height=10, color="transparent"),
            lista_layout
        )
        page.update()

    # --- TELA: PERFIL ---
    def show_perfil_screen(pro):
        nonlocal profissional_selecionado
        profissional_selecionado = pro
        page.clean()
        comentarios_layout = ft.Column(spacing=10)
        for c in pro["comentarios"]:
            comentarios_layout.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(c["usuario"], weight=ft.FontWeight.BOLD, size=13, color="#495057"),
                        ft.Text(f'"{c["texto"]}"', italic=True, size=13, color="#212529")
                    ]),
                    padding=10, bgcolor="#F8F9FA", border_radius=6
                )
            )

        input_usuario = ft.TextField(label="Seu Nome", dense=True, bgcolor="#FFFFFF")
        input_comentario = ft.TextField(label="Escreva uma avaliação...", multiline=True, min_lines=2,
                                        bgcolor="#FFFFFF")

        def enviar_comentario(e):
            if input_usuario.value and input_comentario.value:
                pro["comentarios"].append({"usuario": input_usuario.value, "texto": input_comentario.value})
                show_perfil_screen(pro)

        page.add(
            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_home_screen()),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Image(src=pro["foto"], width=80, height=80, border_radius=40, fit="cover"),
                        ft.Column([
                            ft.Text(pro["nome"], size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(pro["area"], size=15, color="#6C757D"),
                            ft.Row([ft.Icon(ft.Icons.STAR, color="amber", size=16),
                                    ft.Text(f"{pro['avaliacao']} (Média)", size=13)])
                        ])
                    ]),
                    ft.Divider(),
                    ft.Text("Sobre o Profissional / Habilidades", weight=ft.FontWeight.BOLD, size=14),
                    ft.Text(pro["habilidades"], color="#495057", size=14),
                    ft.Text(f"Localização: {pro['localizacao']}", size=13, color="#6C757D"),

                    ft.Divider(),
                    ft.Text(f"Avaliações dos Clientes ({len(pro['comentarios'])})", weight=ft.FontWeight.BOLD, size=14),
                    comentarios_layout,
                    ft.Divider(height=10, color="transparent"),

                    # Formulário de novo comentário
                    ft.Text("Deixe sua avaliação:", weight=ft.FontWeight.BOLD, size=13),
                    input_usuario,
                    input_comentario,
                    ft.TextButton("Postar Comentário", icon=ft.Icons.SEND, on_click=enviar_comentario),
                    ft.Divider(),

                    # Botão para ir ao Checkout
                    ft.ElevatedButton(
                        f"Contratar Consulta por R$ {pro['preco']:.2f}",
                        icon=ft.Icons.CREDIT_CARD,
                        width=float("inf"),
                        style=ft.ButtonStyle(bgcolor="#198754", color="#FFFFFF"),
                        on_click=lambda e: show_checkout_screen()
                    )
                ]),
                padding=15,
                bgcolor="#FFFFFF",
                border_radius=12
            )
        )
        page.update()

        # --- TELA 4: CHECKOUT (Split de Taxas + Dados do Cartão) ---

    def show_checkout_screen():
        page.clean()
        pro = profissional_selecionado
        valor_total = pro["preco"]
        taxa_app = valor_total * 0.10
        valor_profissional = valor_total - taxa_app

        num_cartao = ft.TextField(label="Número do Cartão", hint_text="0000 0000 0000 0000", max_length=19,
                                  bgcolor="#FFFFFF")
        nome_titular = ft.TextField(label="Nome Impresso no Cartão", bgcolor="#FFFFFF")
        validade_cartao = ft.TextField(label="Validade (MM/AA)", hint_text="MM/AA", max_length=5, expand=True,
                                       bgcolor="#FFFFFF")
        cvv_cartao = ft.TextField(label="CVV", hint_text="123", max_length=3, password=True, expand=True,
                                  bgcolor="#FFFFFF")

        page.add(
            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_perfil_screen(pro)),
            ft.Text("Checkout de Pagamento Seguro", size=22, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([
                    ft.Text(f"Resumo da transação para: {pro['nome']}", size=14, color="#6C757D"),
                    ft.Row([ft.Text("Valor Total do Serviço:"),
                            ft.Text(f"R$ {valor_total:.2f}", weight=ft.FontWeight.BOLD)],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row(
                        [ft.Text("Taxa Retida pela Plataforma (10%):"), ft.Text(f"R$ {taxa_app:.2f}", color="#DC3545")],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([ft.Text("Destinado ao Profissional (90%):"),
                            ft.Text(f"R$ {valor_profissional:.2f}", color="#198754")],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    ft.Text("Dados do Cartão de Crédito", weight=ft.FontWeight.BOLD, size=15), num_cartao, nome_titular,
                    ft.Row([validade_cartao, cvv_cartao], spacing=10), ft.Divider(height=10, color="transparent"),
                    ft.ElevatedButton("Efetuar Pagamento via Mercado Pago", icon=ft.Icons.LOCK_CLOCK,
                                      width=float("inf"), style=ft.ButtonStyle(bgcolor="#009EE3", color="#FFFFFF"),
                                      on_click=lambda e: processar_pagamento())
                ]), padding=20, bgcolor="#FFFFFF", border_radius=12
            )
        )
        page.update()

    def processar_pagamento():
        page.snack_bar = ft.SnackBar(
            ft.Text("Sucesso! Pagamento aprovado. 10% retido na sua conta e 90% enviado ao profissional."),
            bgcolor="#198754")
        page.snack_bar.open = True
        show_welcome_screen()

        # --- TELA 5: TRABALHE CONOSCO ---

    def show_trabalhe_conosco_screen():
        page.clean()
        page.horizontal_alignment = "start"
        page.vertical_alignment = "start"
        page.floating_action_button = None
        nome_f = ft.TextField(label="Nome Completo", bgcolor="#FFFFFF")
        area_f = ft.TextField(label="Área de Atuação", bgcolor="#FFFFFF")
        preco_f = ft.TextField(label="Preço por Hora / Consulta (R$)", bgcolor="#FFFFFF")
        local_f = ft.TextField(label="Sua Cidade / Localização", bgcolor="#FFFFFF")
        hab_f = ft.TextField(label="Suas Habilidades", multiline=True, min_lines=2, bgcolor="#FFFFFF")

        def salvar_profissional(e):
            if nome_f.value and area_f.value and preco_f.value:
                PROFISSIONAIS.append({"id": len(PROFISSIONAIS) + 1, "nome": nome_f.value, "area": area_f.value,
                                      "preco": float(preco_f.value), "localizacao": local_f.value,
                                      "foto": "https://unsplash.com", "habilidades": hab_f.value, "avaliacao": 5.0,
                                      "comentarios": []})
                page.snack_bar = ft.SnackBar(ft.Text("Perfil publicado com sucesso!"), bgcolor="#198754")
                page.snack_bar.open = True
                show_welcome_screen()

        page.add(
            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_welcome_screen()),
            ft.Text("Trabalhe Conosco", size=24, weight=ft.FontWeight.BOLD, color="#212529"),
            ft.Text("Cadastre seu perfil profissional:", size=14, color="#6C757D"),
            nome_f, area_f, preco_f, local_f, hab_f,
            ft.ElevatedButton("Cadastrar Meu Perfil", width=float("inf"),
                              style=ft.ButtonStyle(bgcolor="#212529", color="#FFFFFF"), on_click=salvar_profissional)
        )
        page.update()

        # --- TELA 6: CENTRAL DE SUPORTE ---

    def show_suporte_screen():
        page.clean()
        page.horizontal_alignment = "start"
        page.vertical_alignment = "start"
        page.floating_action_button = None
        chat_historico = ft.Column(scroll="always", height=300, spacing=10)
        chat_historico.controls.append(
            ft.Container(content=ft.Text("🤖 Suporte: Olá! Como posso ajudar você hoje?", color="#212529"), padding=10,
                         bgcolor="#E9ECEF", border_radius=8))
        input_msg = ft.TextField(hint_text="Digite sua dúvida aqui...", expand=True, bgcolor="#FFFFFF")

        def enviar_mensagem_suporte(e):
            if input_msg.value:
                chat_historico.controls.append(
                    ft.Container(content=ft.Text(f"👤 Você: {input_msg.value}", color="#FFFFFF"), padding=10,
                                 bgcolor="#212529", border_radius=8, alignment=ft.alignment.center_right))
                chat_historico.controls.append(ft.Container(content=ft.Text(
                    "🤖 Suporte: Entendido! Nossa equipe de segurança monitora as transações do Mercado Pago para garantir seu split de 10% e 90%.",
                    color="#212529"), padding=10, bgcolor="#E9ECEF", border_radius=8))
                input_msg.value = ""
                page.update()

        page.add(
            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_welcome_screen()),
            ft.Text("Central de Suporte", size=24, weight=ft.FontWeight.BOLD, color="#212529"),
            ft.Container(content=chat_historico, padding=15, bgcolor="#FFFFFF", border_radius=12, expand=True),
            ft.Row([input_msg, ft.IconButton(ft.Icons.SEND, icon_color="#212529", on_click=enviar_mensagem_suporte)])
        )
        page.update()

        # --- TELA 1: INICIAL (BOAS-VINDAS) ---

    def show_welcome_screen():
        page.clean()
        page.horizontal_alignment = "center"
        page.vertical_alignment = "center"

        page.floating_action_button = ft.FloatingActionButton(
            content=ft.Row(
                [ft.Icon(ft.Icons.SUPPORT_AGENT, color="#FFFFFF"), ft.Text("Suporte", color="#FFFFFF")],
                alignment=ft.MainAxisAlignment.CENTER, spacing=5
            ),
            bgcolor="#212529", width=110, on_click=lambda e: show_suporte_screen()
        )

        page.add(
            ft.Column([
                ft.Text("ServiceClean Pro", size=28, weight=ft.FontWeight.BOLD, color="#212529"),
                ft.Text("Sua vida mais fácil com profissionais qualificados", size=14, color="#6C757D"),
                ft.Divider(height=15, color="transparent"),
                ft.Image(src="https://unsplash.com", width=350, height=220, fit="cover", border_radius=12),
                ft.Divider(height=25, color="transparent"),
                ft.ElevatedButton("Buscar Profissionais", icon=ft.Icons.ARROW_FORWARD, width=350,
                                  style=ft.ButtonStyle(bgcolor="#212529", color="#FFFFFF", padding=15),
                                  on_click=lambda e: preparar_e_ir_para_home()),
                ft.Divider(height=5, color="transparent"),
                ft.TextButton("Quero ser um profissional (Trabalhe Conosco)", icon=ft.Icons.WORK_OUTLINE,
                              style=ft.ButtonStyle(color="#495057"), on_click=lambda e: show_trabalhe_conosco_screen())
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

    def preparar_e_ir_para_home():
        page.horizontal_alignment = "start"
        page.vertical_alignment = "start"
        show_home_screen()

        # Inicia o app abrindo a tela de boas-vindas

    show_welcome_screen()

if __name__ == "__main__":
    ft.app(target=main)