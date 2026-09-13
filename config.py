"""
config.py
Configurações centrais do Service Clean.

IMPORTANTE SOBRE PAGAMENTOS:
Nenhuma chave de API real fica gravada no código. Tudo vem de variáveis
de ambiente (arquivo .env), que você configura com as credenciais da SUA
conta em um gateway de pagamento com suporte a PIX e split (divisão
automática de valores). Sem essas credenciais reais, o app roda em modo
SIMULADO (nenhuma cobrança real acontece).

Gateways brasileiros com PIX + split prontos via API (escolha um e crie
uma conta de pessoa física/jurídica para obter as chaves):
  - Asaas          -> https://www.asaas.com/api
  - Efí (Gerencianet) -> https://sejaefi.com.br
  - Mercado Pago   -> https://www.mercadopago.com.br/developers
  - PagBank        -> https://dev.pagbank.uol.com.br
"""

import os

# ------------------------------------------------------------------ #
# Comissão do app
# ------------------------------------------------------------------ #
COMISSAO_APP_PERCENTUAL = 0.10  # 10% de cada pagamento fica retido para o app

# Chave PIX (e-mail) da conta que RECEBE a comissão do app.
# Troque aqui se um dia mudar de conta/banco.
PIX_KEY_DONO_APP = os.getenv("SERVICE_CLEAN_PIX_DONO", "elyoenaydb@gmail.com")
BANCO_DONO_APP = "Sicredi"

# ------------------------------------------------------------------ #
# Credenciais do gateway de pagamento (defina no seu ambiente/.env)
#   export SERVICE_CLEAN_GATEWAY_API_KEY="sua_chave_aqui"
#   export SERVICE_CLEAN_GATEWAY_BASE_URL="https://api.asaas.com/v3"
# ------------------------------------------------------------------ #
GATEWAY_API_KEY = os.getenv("SERVICE_CLEAN_GATEWAY_API_KEY", "")
GATEWAY_BASE_URL = os.getenv("SERVICE_CLEAN_GATEWAY_BASE_URL", "https://api.asaas.com/v3")

# Se não houver chave configurada, o gateway roda em modo simulado
MODO_SIMULADO = GATEWAY_API_KEY == ""

# ------------------------------------------------------------------ #
# Paleta de cores (única fonte de verdade para toda a UI)
# ------------------------------------------------------------------ #
COR_MARROM = "#6F4E37"
COR_MARROM_HOVER = "#593E2B"
COR_TEXTO = "#333333"
COR_ERRO = "#D32F2F"
COR_SUCESSO = "#2E7D32"
COR_FUNDO = "#F5F5F7"
COR_BORDA = "#D1D1D6"
COR_CARD = "#FFFFFF"
COR_HOVER_CLARO = "#E5E5EA"
