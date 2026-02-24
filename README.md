# Agentes de IA

Repositório da disciplina de **Agentes de IA** do MBA em Inteligência Artificial — [Sigmoidal](https://sigmoidal.ai) com [STAR Research Institute](https://starresearch.institute).

## Configuração do Ambiente

### 1. Clonar o repositório

```bash
git clone https://github.com/carlosfab/ai-agents-sigmoidal.git
cd ai-agents-sigmoidal
```

### 2. Instalar as dependências

É necessário ter o [uv](https://docs.astral.sh/uv/getting-started/installation/) instalado.

```bash
uv sync
```

### 3. Configurar as API Keys

Crie um arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
```

Preencha com suas chaves:

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

#### Onde obter as chaves

| Serviço | Cadastro | Observação |
|---------|----------|------------|
| **OpenAI** | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | Requer créditos (plano pago) |
| **Tavily** | [app.tavily.com](https://app.tavily.com) | Free tier com 1.000 buscas/mês |

> Você pode usar outro provedor de LLM (ex: Anthropic, Google) no lugar da OpenAI. Nesse caso, adicione a chave correspondente ao `.env` (ex: `ANTHROPIC_API_KEY`).
