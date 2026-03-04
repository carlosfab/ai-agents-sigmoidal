from dotenv import load_dotenv

load_dotenv()

from mcp.server.fastmcp import FastMCP

# ─────────────────────────────────────────────
# Servidor MCP — Simulação didática da API ASAAS
# ─────────────────────────────────────────────
mcp = FastMCP("asaas_financeiro")

# Banco de dados em memória para simulação
_clientes = {}
_cobrancas = {}
_id_counter = {"cliente": 1, "cobranca": 1}


# ══════════════════════════════════════════════
# TOOLS — Ações que o agente pode executar
# ══════════════════════════════════════════════

@mcp.tool()
def criar_cliente(nome: str, cpf_cnpj: str, email: str = "", telefone: str = "") -> str:
    """Cria um novo cliente na base do ASAAS.

    Args:
        nome: Nome completo ou razão social do cliente
        cpf_cnpj: CPF (000.000.000-00) ou CNPJ (00.000.000/0000-00)
        email: E-mail do cliente (opcional)
        telefone: Telefone do cliente (opcional)
    """
    cliente_id = f"cus_{_id_counter['cliente']:04d}"
    _id_counter["cliente"] += 1

    _clientes[cliente_id] = {
        "id": cliente_id,
        "nome": nome,
        "cpf_cnpj": cpf_cnpj,
        "email": email,
        "telefone": telefone,
    }
    return (
        f"✅ Cliente criado com sucesso!\n"
        f"  ID: {cliente_id}\n"
        f"  Nome: {nome}\n"
        f"  CPF/CNPJ: {cpf_cnpj}"
    )


@mcp.tool()
def criar_cobranca(
    cliente_id: str,
    valor: float,
    vencimento: str,
    tipo: str = "PIX",
    descricao: str = "",
) -> str:
    """Cria uma cobrança para um cliente existente.

    Args:
        cliente_id: ID do cliente (ex: cus_0001)
        valor: Valor em reais (ex: 150.00)
        vencimento: Data de vencimento no formato YYYY-MM-DD
        tipo: Forma de pagamento — PIX, BOLETO ou CREDIT_CARD (padrão: PIX)
        descricao: Descrição da cobrança (opcional)
    """
    if cliente_id not in _clientes:
        return f"❌ Cliente '{cliente_id}' não encontrado."

    tipos_validos = {"PIX", "BOLETO", "CREDIT_CARD"}
    if tipo not in tipos_validos:
        return f"❌ Tipo inválido. Use: {', '.join(tipos_validos)}"

    cobranca_id = f"pay_{_id_counter['cobranca']:04d}"
    _id_counter["cobranca"] += 1

    _cobrancas[cobranca_id] = {
        "id": cobranca_id,
        "cliente_id": cliente_id,
        "valor": valor,
        "vencimento": vencimento,
        "tipo": tipo,
        "status": "PENDING",
        "descricao": descricao,
    }

    link_fake = f"https://sandbox.asaas.com/i/{cobranca_id}"
    return (
        f"✅ Cobrança criada!\n"
        f"  ID: {cobranca_id}\n"
        f"  Cliente: {_clientes[cliente_id]['nome']}\n"
        f"  Valor: R$ {valor:,.2f}\n"
        f"  Vencimento: {vencimento}\n"
        f"  Tipo: {tipo}\n"
        f"  Status: PENDING\n"
        f"  Link: {link_fake}"
    )


@mcp.tool()
def consultar_cobranca(cobranca_id: str) -> str:
    """Consulta o status e detalhes de uma cobrança existente.

    Args:
        cobranca_id: ID da cobrança (ex: pay_0001)
    """
    if cobranca_id not in _cobrancas:
        return f"❌ Cobrança '{cobranca_id}' não encontrada."

    c = _cobrancas[cobranca_id]
    cliente = _clientes.get(c["cliente_id"], {})
    return (
        f"📋 Detalhes da Cobrança\n"
        f"  ID: {c['id']}\n"
        f"  Cliente: {cliente.get('nome', 'N/A')}\n"
        f"  Valor: R$ {c['valor']:,.2f}\n"
        f"  Vencimento: {c['vencimento']}\n"
        f"  Tipo: {c['tipo']}\n"
        f"  Status: {c['status']}\n"
        f"  Descrição: {c.get('descricao', '-')}"
    )


# ══════════════════════════════════════════════
# RESOURCES (estáticos) — Contexto somente-leitura
# ══════════════════════════════════════════════

@mcp.resource("asaas://info/sobre")
def sobre_o_servidor() -> str:
    """Informações gerais sobre o servidor MCP do ASAAS."""
    return (
        "Servidor MCP ASAAS (modo sandbox/didático).\n"
        "Permite criar clientes, emitir cobranças via PIX, Boleto e Cartão,\n"
        "e consultar status de pagamentos.\n"
        "Ambiente: SANDBOX — nenhuma operação real é realizada."
    )


@mcp.resource("asaas://info/formas-de-pagamento")
def formas_de_pagamento() -> str:
    """Lista as formas de pagamento suportadas pelo ASAAS."""
    return (
        "Formas de pagamento suportadas:\n"
        "  • PIX         — Instantâneo, QR Code dinâmico gerado automaticamente\n"
        "  • BOLETO      — Vencimento configurável, juros e multa opcionais\n"
        "  • CREDIT_CARD — Parcelamento em até 12x, pré-autorização disponível\n\n"
        "Para cobranças recorrentes (assinaturas), os ciclos disponíveis são:\n"
        "  WEEKLY | BIWEEKLY | MONTHLY | QUARTERLY | SEMIANNUALLY | YEARLY"
    )


@mcp.resource("asaas://info/status-cobranca")
def status_cobranca() -> str:
    """Explica os possíveis status de uma cobrança no ASAAS."""
    return (
        "Status possíveis de uma cobrança:\n"
        "  PENDING      — Aguardando pagamento\n"
        "  RECEIVED     — Pago (confirmado)\n"
        "  CONFIRMED    — Pago e confirmado pelo banco\n"
        "  OVERDUE      — Vencida e não paga\n"
        "  REFUNDED     — Estornada ao pagador\n"
        "  REFUND_REQUESTED — Estorno solicitado\n"
        "  CHARGEBACK_REQUESTED — Chargeback em análise\n"
        "  CANCELLED    — Cancelada pelo emissor"
    )


# ══════════════════════════════════════════════
# PROMPTS — Instruções de papel para o agente
# ══════════════════════════════════════════════

@mcp.prompt()
def assistente_cobrancas() -> str:
    """Prompt padrão para o assistente de cobranças ASAAS."""
    return (
        "Você é um assistente especializado na plataforma ASAAS.\n"
        "Seu papel é ajudar a criar clientes, emitir cobranças e consultar pagamentos.\n\n"
        "Regras importantes:\n"
        "- Sempre confirme o CPF/CNPJ antes de criar um cliente\n"
        "- Para cobranças, prefira PIX quando o vencimento for no dia\n"
        "- Informe sempre o status e o link de pagamento ao criar uma cobrança\n"
        "- Nunca invente IDs; use apenas os retornados pelas ferramentas"
    )


@mcp.prompt()
def assistente_inadimplencia() -> str:
    """Prompt para o agente de recuperação de cobranças vencidas."""
    return (
        "Você é um assistente de recuperação de crédito integrado ao ASAAS.\n"
        "Sua missão é identificar cobranças com status OVERDUE e sugerir ações:\n\n"
        "1. Consulte as cobranças vencidas usando 'consultar_cobranca'\n"
        "2. Proponha reenvio do link de pagamento atualizado\n"
        "3. Sugira renegociação com nova data de vencimento se necessário\n"
        "4. Mantenha um tom profissional e empático com o cliente"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
