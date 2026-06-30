"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_REF = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml"


def pull_prompts_from_langsmith() -> bool:
    """
    Conecta ao LangSmith, faz pull do prompt e salva localmente em YAML.

    Returns:
        True se sucesso, False caso contrário
    """
    print(f"Fazendo pull do prompt: {PROMPT_REF}")

    try:
        client = Client()
        prompt = client.pull_prompt(PROMPT_REF, dangerously_pull_public_prompt=True)

        system_prompt = ""
        user_prompt = ""

        for message in prompt.messages:
            if isinstance(message, SystemMessagePromptTemplate):
                system_prompt = message.prompt.template
            elif isinstance(message, HumanMessagePromptTemplate):
                user_prompt = message.prompt.template

        yaml_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
            }
        }

        if OUTPUT_PATH.exists():
            print(f"⚠️  Arquivo já existia — será sobrescrito: {OUTPUT_PATH}")

        print(f"Salvando em: {OUTPUT_PATH}")
        success = save_yaml(yaml_data, str(OUTPUT_PATH))

        if success:
            print(f"✅ Prompt salvo com sucesso em {OUTPUT_PATH}")
        else:
            print("❌ Falha ao salvar o prompt")

        return success

    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt: {e}")
        return False


def main():
    """Função principal"""
    print("=" * 50)
    print("Pull de Prompts do LangSmith Hub")
    print("=" * 50 + "\n")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
