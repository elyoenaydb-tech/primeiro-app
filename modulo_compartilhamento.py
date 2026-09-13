"""
modulo_compartilhamento.py
Gera o texto/link de compartilhamento do perfil de um profissional,
para o cliente indicar via WhatsApp ou copiar para outro app.
"""

from urllib.parse import quote


def gerar_texto_compartilhamento(prof_nome: str, categoria: str, avaliacao: str) -> str:
    return (
        f"Olha esse profissional que encontrei no Service Clean! 🧹\n"
        f"👤 {prof_nome}\n"
        f"🛠️ {categoria}\n"
        f"⭐ {avaliacao}\n"
        f"Baixe o app Service Clean para agendar também!"
    )


def gerar_link_whatsapp(texto: str) -> str:
    """Retorna um link wa.me pronto para abrir o WhatsApp com o texto preenchido."""
    return f"https://wa.me/?text={quote(texto)}"
