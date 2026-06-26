"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """Faz pull do prompt do LangSmith Hub e retorna os dados extraídos."""
    prompt_name = "leonanluppi/bug_to_user_story_v1"
    print(f"   Puxando prompt: {prompt_name}")

    prompt = hub.pull(prompt_name)
    print(f"   ✓ Prompt carregado com sucesso")

    # Extrair dados do prompt
    messages = prompt.messages if hasattr(prompt, 'messages') else []

    system_prompt = ""
    user_prompt = ""

    for msg in messages:
        if hasattr(msg, 'prompt') and hasattr(msg.prompt, 'template'):
            template = msg.prompt.template
        elif hasattr(msg, 'content'):
            template = msg.content
        else:
            continue

        msg_type = type(msg).__name__.lower()
        if 'system' in msg_type:
            system_prompt = template
        elif 'human' in msg_type:
            user_prompt = template

    # Se não encontrou via messages, tentar template direto
    if not system_prompt and hasattr(prompt, 'template'):
        system_prompt = prompt.template

    prompt_data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt or "Prompt não encontrado",
            "user_prompt": user_prompt or "{bug_report}",
            "version": "v1",
            "created_at": "2025-01-15",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    return prompt_data


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    try:
        prompt_data = pull_prompts_from_langsmith()

        output_path = "prompts/bug_to_user_story_v1.yml"
        if save_yaml(prompt_data, output_path):
            print(f"\n   ✓ Prompt salvo em: {output_path}")
            print("\nPróximos passos:")
            print("1. Analise o prompt em prompts/bug_to_user_story_v1.yml")
            print("2. Crie sua versão otimizada em prompts/bug_to_user_story_v2.yml")
            return 0
        else:
            print("   ❌ Erro ao salvar prompt")
            return 1

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
