"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def prompt_data():
    """Fixture que carrega o prompt v2."""
    data = load_prompts(PROMPT_FILE)
    return data["bug_to_user_story_v2"]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' não encontrado"
        system_prompt = prompt_data["system_prompt"].strip()
        assert len(system_prompt) > 0, "system_prompt está vazio"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        system_prompt = prompt_data["system_prompt"].lower()
        role_keywords = ["você é um", "você é uma", "atue como", "seu papel é", "sua missão"]
        has_role = any(keyword in system_prompt for keyword in role_keywords)
        assert has_role, "Prompt não define uma persona/role (ex: 'Você é um Product Manager')"

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data["system_prompt"].lower()
        format_keywords = ["markdown", "user story", "como um", "eu quero", "para que", "given-when-then", "dado que", "quando", "então"]
        matches = [kw for kw in format_keywords if kw in system_prompt]
        assert len(matches) >= 2, f"Prompt não menciona formato adequado. Encontrado: {matches}"

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data["system_prompt"].lower()
        example_keywords = ["exemplo", "entrada", "saída", "bug report", "user story gerada", "bug:", "resposta:"]
        matches = [kw for kw in example_keywords if kw in system_prompt]
        assert len(matches) >= 2, f"Prompt não contém exemplos de entrada/saída (Few-shot). Encontrado: {matches}"

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "")
        full_text = system_prompt + user_prompt
        assert "[TODO]" not in full_text, "Ainda existem marcadores [TODO] no prompt"
        assert "TODO:" not in full_text, "Ainda existem marcadores TODO: no prompt"

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques_applied", [])
        assert len(techniques) >= 2, f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}: {techniques}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
