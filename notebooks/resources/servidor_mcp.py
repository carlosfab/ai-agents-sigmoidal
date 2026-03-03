from dotenv import load_dotenv

load_dotenv()

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("servidor_financeiro")


@mcp.tool()
def calcular_juros_compostos(capital: float, taxa_anual: float, meses: int) -> str:
    """Calcula o montante final usando juros compostos.

    Args:
        capital: valor inicial em reais
        taxa_anual: taxa de juros anual em porcentagem (ex: 12.5 para 12.5%)
        meses: quantidade de meses
    """
    taxa_mensal = taxa_anual / 100 / 12
    montante = capital * (1 + taxa_mensal) ** meses
    juros = montante - capital
    return (
        f"Capital: R$ {capital:,.2f} | "
        f"Taxa: {taxa_anual}% a.a. | "
        f"Prazo: {meses} meses | "
        f"Montante: R$ {montante:,.2f} | "
        f"Juros: R$ {juros:,.2f}"
    )


@mcp.tool()
def converter_moeda(valor: float, de: str, para: str) -> str:
    """Converte valores entre BRL, USD e EUR usando taxas fixas.

    Args:
        valor: quantidade a converter
        de: moeda de origem (BRL, USD ou EUR)
        para: moeda de destino (BRL, USD ou EUR)
    """
    taxas_para_brl = {"BRL": 1.0, "USD": 5.80, "EUR": 6.30}

    if de not in taxas_para_brl or para not in taxas_para_brl:
        return "Moedas suportadas: BRL, USD, EUR"

    valor_brl = valor * taxas_para_brl[de]
    resultado = valor_brl / taxas_para_brl[para]
    return f"{valor:.2f} {de} = {resultado:.2f} {para}"


@mcp.resource("info://servidor/sobre")
def sobre_o_servidor():
    """Informacoes sobre o servidor MCP financeiro."""
    return (
        "Servidor MCP Financeiro v1.0. "
        "Ferramentas disponiveis: calculo de juros compostos e conversao de moeda (BRL/USD/EUR). "
        "Desenvolvido para o curso de Agentes de IA - Sigmoidal."
    )


@mcp.prompt()
def prompt():
    """Prompt padrao para o assistente financeiro."""
    return (
        "Voce e um assistente financeiro especializado em calculos de investimento "
        "e conversao de moedas. Use as ferramentas disponiveis para responder com "
        "precisao. Sempre apresente os resultados de forma clara e organizada."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
