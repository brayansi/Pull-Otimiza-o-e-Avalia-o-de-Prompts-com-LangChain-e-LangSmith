# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

## Objetivo

Software para otimização de prompts de conversão de Bug Reports em User Stories, utilizando LangChain e LangSmith.

1. **Pull de prompts** do LangSmith Prompt Hub (prompt v1 de baixa qualidade)
2. **Otimização** usando técnicas avançadas de Prompt Engineering
3. **Push dos prompts otimizados** de volta ao LangSmith Hub (público)
4. **Avaliação automática** com 4 métricas customizadas (Tone, Acceptance Criteria, User Story Format, Completeness)
5. **Iteração** até atingir pontuação >= 0.9 em todas as métricas

---

## Técnicas Aplicadas (Fase 2)

### 1. Role Prompting
**Técnica escolhida:** Definir uma persona detalhada para o modelo.

**Justificativa:** Ao atribuir o papel de "Product Manager Sênior e Scrum Master certificado com mais de 10 anos de experiência", o modelo adota um comportamento mais profissional, empático e focado em valor de negócio, resultando em User Stories de maior qualidade.

**Exemplo prático:**
```
Você é um Product Manager Sênior e Scrum Master certificado com mais de 10 anos de experiência em metodologias ágeis.
Você é reconhecido pela sua capacidade de transformar relatos de bugs técnicos em User Stories claras, empáticas e completas...
```

### 2. Few-shot Learning
**Técnica escolhida:** Fornecer 4 exemplos concretos de entrada/saída dentro do prompt.

**Justificativa:** Exemplos claros de bugs simples e médios permitem que o modelo aprenda o formato exato esperado (Como um... eu quero... para que...) e o padrão de Critérios de Aceitação (Given-When-Then). Isso melhorou significativamente o User Story Format Score.

**Exemplo prático:** 4 exemplos incluídos no prompt:
- 2 bugs simples (carrinho de compras, validação de email)
- 1 bug simples com dados numéricos (dashboard)
- 1 bug médio com contexto técnico (relatório de vendas)

### 3. Chain of Thought (CoT)
**Técnica escolhida:** Instruir o modelo a "pensar passo a passo" antes de gerar a resposta.

**Justificativa:** O raciocínio estruturado em 6 passos (identificar persona, entender problema, articular valor, listar critérios, considerar edge cases, preservar contexto técnico) garante que o modelo não omita informações importantes, melhorando o Completeness Score.

**Exemplo prático:**
```
Antes de escrever, analise mentalmente:
1. Quem é a PERSONA específica afetada?
2. O que essa persona DESEJA FAZER?
3. Qual o VALOR DE NEGÓCIO real?
4. Quais CRITÉRIOS DE ACEITAÇÃO testáveis validam a correção?
5. Quais EDGE CASES relevantes?
6. Há INFORMAÇÕES TÉCNICAS no bug que devem ser preservadas?
```

---

## Resultados Finais

### Métricas de Avaliação (v2 otimizado)

| Métrica | Score |
|---------|-------|
| Tone Score | 0.87 |
| Acceptance Criteria Score | 0.89 |
| User Story Format Score | 0.88 |
| Completeness Score | 0.88 |
| **MÉDIA GERAL** | **0.88** |

### Comparação v1 vs v2

| Aspecto | v1 (Original) | v2 (Otimizado) |
|---------|---------------|----------------|
| Persona | Genérica ("assistente") | Específica ("PM Sênior") |
| Formato | Sem estrutura definida | "Como um... eu quero... para que..." |
| Critérios de Aceitação | Ausentes | Given-When-Then estruturado |
| Exemplos | Nenhum | 4 exemplos (Few-shot) |
| Raciocínio | Direto | Chain of Thought (6 passos) |
| Contexto Técnico | Não preservado | Seção obrigatória quando aplicável |
| Edge Cases | Não cobertos | Instruções explícitas |

### LangSmith Dashboard

- Prompt público: [mba/bug_to_user_story_v2](https://smith.langchain.com/hub/mba/bug_to_user_story_v2)
- Projeto de avaliação: `prompt-optimization-challenge-resolved`

---

## Como Executar

### Pré-requisitos

- Python 3.9+
- Conta no [LangSmith](https://smith.langchain.com/) com API Key
- API Key da [OpenAI](https://platform.openai.com/api-keys)

### Instalação

```bash
# Clonar o repositório
git clone https://github.com/diegonogueira/mba-fullcycle-desafio2.git
cd mba-fullcycle-desafio2

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### Configuração

```bash
# Copiar template de variáveis de ambiente
cp .env.example .env

# Editar .env com suas credenciais:
# - LANGSMITH_API_KEY
# - USERNAME_LANGSMITH_HUB (seu handle do LangSmith Hub)
# - OPENAI_API_KEY
# - LLM_PROVIDER=openai
# - LLM_MODEL=gpt-4o-mini
# - EVAL_MODEL=gpt-4o
```

### Execução

```bash
# 1. Pull dos prompts ruins do LangSmith
PYTHONPATH=src python src/pull_prompts.py

# 2. (Opcional) Editar prompts/bug_to_user_story_v2.yml com suas otimizações

# 3. Push dos prompts otimizados
PYTHONPATH=src python src/push_prompts.py

# 4. Executar avaliação
PYTHONPATH=src python src/evaluate.py

# 5. Executar testes de validação
pytest tests/test_prompts.py -v
```

---

## Estrutura do Projeto

```
desafio-prompt-engineer/
├── .env.example              # Template das variáveis de ambiente
├── requirements.txt          # Dependências Python
├── README.md                 # Documentação do processo
│
├── prompts/
│   ├── bug_to_user_story_v1.yml       # Prompt inicial (após pull)
│   └── bug_to_user_story_v2.yml       # Prompt otimizado
│
├── src/
│   ├── pull_prompts.py       # Pull do LangSmith
│   ├── push_prompts.py       # Push ao LangSmith
│   ├── evaluate.py           # Avaliação automática
│   ├── metrics.py            # 4 métricas implementadas
│   ├── dataset.py            # 15 exemplos de bugs
│   └── utils.py              # Funções auxiliares
│
├── datasets/
│   └── bug_to_user_story.jsonl  # Dataset de avaliação
│
├── tests/
│   └── test_prompts.py       # Testes de validação
```
