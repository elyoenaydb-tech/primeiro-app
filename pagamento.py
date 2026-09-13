"""
pagamento.py
Integração com gateway de pagamento (Pix) e regra de split automático.

REGRA DE NEGÓCIO:
  - Valor total pago pelo cliente é dividido automaticamente:
      90% -> chave Pix do profissional que prestou o serviço
      10% -> chave Pix do dono do app (config.PIX_KEY_DONO_APP)
  - O split acontece no lado do GATEWAY de pagamento (Asaas, Efí, Mercado
    Pago etc.), não manualmente — é assim que esse tipo de "marketplace"
    funciona na prática: você cria os dois recebedores no gateway e ele
    distribui o valor no momento da confirmação do Pix.

MODO SIMULADO:
  Se nenhuma API key for configurada (ver config.py), este módulo NÃO
  faz nenhuma chamada de rede: ele apenas calcula os valores e devolve
  um resultado simulado, para que o app funcione de ponta a ponta sem
  precisar de uma conta de gateway ainda.

PARA LIGAR PAGAMENTOS DE VERDADE:
  1. Crie uma conta em um gateway com Pix + split via API (ex.: Asaas).
  2. Cadastre o profissional como "subconta"/"recebedor" no gateway e
     guarde o walletId/ID retornado (troque o uso de pix_key por esse ID
     nas chamadas reais — cada gateway tem seu próprio formato).
  3. Configure as variáveis de ambiente SERVICE_CLEAN_GATEWAY_API_KEY e
     SERVICE_CLEAN_GATEWAY_BASE_URL.
  4. Implemente a assinatura/validação do webhook de confirmação de
     pagamento do gateway escolhido (necessário para segurança).
"""

import uuid
import requests

import config


class ResultadoPagamento:
    def __init__(self, sucesso: bool, txid: str, valor_total: float,
                 valor_comissao_app: float, valor_profissional: float,
                 mensagem: str, simulado: bool):
        self.sucesso = sucesso
        self.txid = txid
        self.valor_total = valor_total
        self.valor_comissao_app = valor_comissao_app
        self.valor_profissional = valor_profissional
        self.mensagem = mensagem
        self.simulado = simulado


def calcular_split(valor_total: float) -> tuple[float, float]:
    """Retorna (valor_comissao_app, valor_profissional) a partir do valor total."""
    valor_comissao_app = round(valor_total * config.COMISSAO_APP_PERCENTUAL, 2)
    valor_profissional = round(valor_total - valor_comissao_app, 2)
    return valor_comissao_app, valor_profissional


def processar_pagamento_pix(valor_total: float, pix_key_profissional: str,
                             nome_cliente: str, cpf_cliente: str = "00000000000") -> ResultadoPagamento:
    """
    Cria uma cobrança Pix com split automático entre o profissional e o app.

    Em modo simulado (sem API key configurada), retorna um resultado de
    sucesso fictício para permitir testar o fluxo completo do app.
    """
    valor_comissao_app, valor_profissional = calcular_split(valor_total)

    if config.MODO_SIMULADO:
        txid_simulado = f"SIMULADO-{uuid.uuid4().hex[:12].upper()}"
        return ResultadoPagamento(
            sucesso=True,
            txid=txid_simulado,
            valor_total=valor_total,
            valor_comissao_app=valor_comissao_app,
            valor_profissional=valor_profissional,
            mensagem=(
                f"[MODO SIMULADO] Pagamento de R$ {valor_total:.2f} processado. "
                f"R$ {valor_profissional:.2f} iriam para {pix_key_profissional} e "
                f"R$ {valor_comissao_app:.2f} iriam para {config.PIX_KEY_DONO_APP} "
                f"({config.BANCO_DONO_APP})."
            ),
            simulado=True,
        )

    # ---------------------------------------------------------------- #
    # Chamada real ao gateway (exemplo no formato Asaas).
    # Ajuste os campos conforme a documentação do gateway escolhido.
    # ---------------------------------------------------------------- #
    headers = {
        "access_token": config.GATEWAY_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "billingType": "PIX",
        "value": valor_total,
        "description": "Pagamento de serviço - Service Clean",
        "customer": {"name": nome_cliente, "cpfCnpj": cpf_cliente},
        # 'split' é o array que define quem recebe cada parte do valor.
        # No Asaas isso é feito por walletId de subconta, não pela chave
        # Pix diretamente — troque pelo walletId real do profissional.
        "split": [
            {
                "walletId": pix_key_profissional,
                "fixedValue": valor_profissional,
            },
            {
                "walletId": config.PIX_KEY_DONO_APP,
                "fixedValue": valor_comissao_app,
            },
        ],
    }

    try:
        resposta = requests.post(
            f"{config.GATEWAY_BASE_URL}/payments",
            json=payload,
            headers=headers,
            timeout=15,
        )
        resposta.raise_for_status()
        dados = resposta.json()

        return ResultadoPagamento(
            sucesso=True,
            txid=dados.get("id", ""),
            valor_total=valor_total,
            valor_comissao_app=valor_comissao_app,
            valor_profissional=valor_profissional,
            mensagem="Cobrança Pix gerada com sucesso. Aguardando confirmação do pagamento.",
            simulado=False,
        )
    except requests.exceptions.RequestException as erro:
        return ResultadoPagamento(
            sucesso=False,
            txid="",
            valor_total=valor_total,
            valor_comissao_app=valor_comissao_app,
            valor_profissional=valor_profissional,
            mensagem=f"Falha ao processar pagamento: {erro}",
            simulado=False,
        )
