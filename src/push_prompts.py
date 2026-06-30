"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê todos os prompts cadastrados no registry.yaml
2. Valida cada prompt
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header
from prompt_registry import registry

load_dotenv()

PROMPT_IDS = registry.list_prompts()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: ID do prompt no registry (ex: 'bug_to_user_story_v2')
        prompt_data: Dados do prompt carregados do YAML

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB")
    hub_name = f"{username}/{prompt_name}"

    try:
        prompt_info = registry.get_prompt(prompt_name)

        inner = prompt_data.get(prompt_name, {})
        system_prompt = inner.get("system_prompt", "")
        user_prompt = inner.get("user_prompt", "")

        template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt),
        ])

        tags = [f"version:{prompt_info.version}"]
        if prompt_info.model:
            tags.append(f"model:{prompt_info.model}")

        client = Client()
        url = client.push_prompt(
            hub_name,
            object=template,
            tags=tags,
            description=prompt_info.description,
            is_public=True,
        )

        print(f"✅ Prompt publicado com sucesso: {url}")
        return True

    except Exception as e:
        print(f"❌ Erro ao fazer push do prompt: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt carregados do YAML

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    inner = next(iter(prompt_data.values()), {}) if prompt_data else {}

    required_fields = ["description", "system_prompt", "user_prompt", "version"]
    for field in required_fields:
        if field not in inner:
            errors.append(f"Campo obrigatório faltando: {field}")

    system_prompt = inner.get("system_prompt", "").strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print("=" * 50)
    print("Push de Prompts para o LangSmith Hub")
    print("=" * 50 + "\n")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    print(f"Prompts encontrados no registry: {PROMPT_IDS}\n")

    results = []
    for prompt_id in PROMPT_IDS:
        print(f"{'─' * 40}")
        prompt_info = registry.get_prompt(prompt_id)
        prompt_data = load_yaml(str(prompt_info.path))

        if not prompt_data:
            print(f"❌ [{prompt_id}] Falha ao carregar {prompt_info.path}")
            results.append((prompt_id, False))
            continue

        print(f"Validando: {prompt_id}")
        is_valid, errors = validate_prompt(prompt_data)

        if not is_valid:
            print(f"❌ [{prompt_id}] Prompt inválido:")
            for err in errors:
                print(f"   - {err}")
            results.append((prompt_id, False))
            continue

        print(f"✅ Válido — fazendo push: {os.getenv('USERNAME_LANGSMITH_HUB')}/{prompt_id}")
        success = push_prompt_to_langsmith(prompt_id, prompt_data)
        results.append((prompt_id, success))

    print(f"\n{'=' * 50}")
    print("RESUMO")
    print("=" * 50)
    for prompt_id, ok in results:
        status = "✅" if ok else "❌"
        print(f"  {status} {prompt_id}")

    failed = [pid for pid, ok in results if not ok]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

