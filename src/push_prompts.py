"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "{bug_report}")

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt),
        ])

        username = os.getenv("USERNAME_LANGSMITH_HUB", "mba")
        full_name = f"{username}/{prompt_name}"

        print(f"   Fazendo push: {full_name}")

        hub.push(
            full_name,
            prompt_template,
            new_repo_is_public=True,
            new_repo_description=prompt_data.get("description", "Prompt otimizado para Bug to User Story"),
            tags=prompt_data.get("tags", []),
        )

        print(f"   ✓ Push realizado com sucesso: {full_name}")
        print(f"   ✓ Prompt publicado como PÚBLICO")
        return True

    except Exception as e:
        print(f"   ❌ Erro ao fazer push: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    required_fields = ["description", "system_prompt", "version"]
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")

    system_prompt = prompt_data.get("system_prompt", "").strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")

    if "[TODO]" in system_prompt or "TODO:" in system_prompt:
        errors.append("system_prompt ainda contém TODOs")

    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 2:
        errors.append(f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS AO LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    yaml_path = "prompts/bug_to_user_story_v2.yml"
    data = load_yaml(yaml_path)

    if not data:
        print(f"❌ Não foi possível carregar: {yaml_path}")
        return 1

    prompt_key = "bug_to_user_story_v2"
    prompt_data = data.get(prompt_key)

    if not prompt_data:
        print(f"❌ Chave '{prompt_key}' não encontrada no YAML")
        return 1

    # Validar prompt
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for err in errors:
            print(f"   - {err}")
        return 1

    print("✓ Prompt validado com sucesso")

    techniques = prompt_data.get("techniques_applied", [])
    print(f"   Técnicas aplicadas: {', '.join(techniques)}")

    # Push para o LangSmith Hub
    if push_prompt_to_langsmith(prompt_key, prompt_data):
        print("\n✅ Push concluído com sucesso!")
        print("\nPróximos passos:")
        print("1. Verifique o prompt no LangSmith Hub: https://smith.langchain.com/hub")
        print("2. Execute a avaliação: python src/evaluate.py")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
