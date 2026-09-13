"""
seguranca.py
Funções de apoio para proteção de dados pessoais (boas práticas alinhadas
à LGPD): mascaramento de dados sensíveis ao exibir na tela, e utilitários
de hashing (a senha em si já é tratada com bcrypt em database.py).
"""

import re


def mascarar_email(email: str) -> str:
    """joao.silva@gmail.com -> jo***@gmail.com"""
    if "@" not in email:
        return email
    usuario, dominio = email.split("@", 1)
    if len(usuario) <= 2:
        usuario_mascarado = usuario[0] + "*"
    else:
        usuario_mascarado = usuario[:2] + "*" * (len(usuario) - 2)
    return f"{usuario_mascarado}@{dominio}"


def mascarar_pix_key(pix_key: str) -> str:
    """Mascara qualquer tipo de chave Pix (e-mail, CPF, telefone ou aleatória)."""
    if "@" in pix_key:
        return mascarar_email(pix_key)
    if len(pix_key) <= 4:
        return "*" * len(pix_key)
    return pix_key[:2] + "*" * (len(pix_key) - 4) + pix_key[-2:]


def validar_forca_senha(senha: str) -> tuple[bool, str]:
    """Regra mínima de senha forte, além do tamanho mínimo já checado no cadastro."""
    if len(senha) < 6:
        return False, "A senha deve ter no mínimo 6 caracteres."
    if not re.search(r"[A-Za-z]", senha) or not re.search(r"\d", senha):
        return False, "Use letras e números na senha para maior segurança."
    return True, ""


def sanitizar_entrada(texto: str) -> str:
    """Remove espaços extras e caracteres de controle de campos de texto livre."""
    return re.sub(r"[\x00-\x1f\x7f]", "", texto).strip()
