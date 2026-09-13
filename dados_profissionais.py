"""
dados_profissionais.py
Dados simulados de profissionais (seed inicial do banco), separados do
código de interface para facilitar a futura substituição por uma API real
de cadastro de prestadores.

Cada profissional tem sua PRÓPRIA chave Pix (pix_key) — é para ELA que vai
os 90% do pagamento. Os 10% de comissão do app vão para a chave definida
em config.PIX_KEY_DONO_APP, automaticamente, a cada pagamento confirmado.
"""

PROFISSIONAIS_POR_CATEGORIA = {
    "Diarista": [
        {"nome": "Maria Silva", "avaliacao": "4.9 ⭐", "preco": "R$ 150/dia", "preco_valor": 150.00,
         "bairro": "Centro (0.5 km)", "pix_key": "maria.silva.diarista@exemplo.com",
         "horarios": ["Seg 08:00", "Qua 14:00"],
         "comentarios": ["Excelente limpeza!", "Muito pontual e caprichosa."]},
        {"nome": "Ana Souza", "avaliacao": "4.7 ⭐", "preco": "R$ 140/dia", "preco_valor": 140.00,
         "bairro": "Vila Nova (1.2 km)", "pix_key": "ana.souza.diarista@exemplo.com",
         "horarios": ["Ter 09:00", "Sexta 13:00"],
         "comentarios": ["Recomendo fortemente.", "Deixou tudo brilhando."]},
    ],
    "Eletricista": [
        {"nome": "Carlos Roberto", "avaliacao": "4.8 ⭐", "preco": "R$ 120/visita", "preco_valor": 120.00,
         "bairro": "Jardins (0.8 km)", "pix_key": "carlos.roberto.eletricista@exemplo.com",
         "horarios": ["Ter 10:00", "Qui 16:00"],
         "comentarios": ["Resolveu o curto rápido.", "Preço justo."]},
    ],
    "Encanador": [
        {"nome": "Marcos Lima", "avaliacao": "5.0 ⭐", "preco": "R$ 100/hora", "preco_valor": 100.00,
         "bairro": "Centro (0.2 km)", "pix_key": "marcos.lima.encanador@exemplo.com",
         "horarios": ["Hoje 15:00", "Amanhã 09:00"],
         "comentarios": ["Trocou a tubulação perfeitamente."]},
    ],
}

# Lista completa de profissões suportadas pelo catálogo (mesmo sem prestador cadastrado ainda)
PROFISSOES = [
    "Diarista", "Eletricista", "Encanador", "Pintor",
    "Pedreiro", "Marceneiro", "Mecânico", "Chaveiro",
    "Montador de Móveis", "Técnico de TI", "Jardineiro", "Lavador de Sofá",
]
