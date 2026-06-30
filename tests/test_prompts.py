"""
Testes estáticos de qualidade para os prompts do projeto.

Valida estrutura, técnicas aplicadas e boas práticas sem usar LLM.
Roda contra todos os prompts registrados no registry.yaml.
"""

import re
import yaml
import pytest
from pathlib import Path
from typing import Any, Dict, List, Tuple


# ── Helpers ─────────────────────────────────────────────────────────────────

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_registry() -> Dict[str, Any]:
    with open(_PROMPTS_DIR / "registry.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_all_prompts() -> List[Tuple[str, Dict[str, Any]]]:
    registry = _load_registry()
    result = []
    for prompt_id, agent_data in registry.get("agents", {}).items():
        path = _PROMPTS_DIR / agent_data["path"]
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            result.append((prompt_id, data.get(prompt_id, {})))
    return result


ALL_PROMPTS = _load_all_prompts()
PROMPT_IDS = [p[0] for p in ALL_PROMPTS]


# ── Testes ───────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("prompt_id,prompt_data", ALL_PROMPTS, ids=PROMPT_IDS)
def test_prompt_has_system_prompt(prompt_id: str, prompt_data: Dict[str, Any]):
    """Verifica se o campo system_prompt existe e não está vazio."""
    assert "system_prompt" in prompt_data, (
        f"[{prompt_id}] Campo 'system_prompt' ausente no YAML."
    )
    assert prompt_data["system_prompt"].strip(), (
        f"[{prompt_id}] Campo 'system_prompt' existe mas está vazio."
    )


@pytest.mark.parametrize("prompt_id,prompt_data", ALL_PROMPTS, ids=PROMPT_IDS)
def test_prompt_has_role_definition(prompt_id: str, prompt_data: Dict[str, Any]):
    """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
    system_prompt = prompt_data.get("system_prompt", "")
    role_patterns = [
        r"você é",
        r"you are",
        r"seu papel é",
        r"your role",
        r"atue como",
        r"act as",
    ]
    match = any(re.search(p, system_prompt, re.IGNORECASE) for p in role_patterns)
    assert match, (
        f"[{prompt_id}] Nenhuma definição de persona encontrada no system_prompt. "
        f"Use 'Você é...' ou similar para definir o papel do assistente."
    )


@pytest.mark.parametrize("prompt_id,prompt_data", ALL_PROMPTS, ids=PROMPT_IDS)
def test_prompt_mentions_format(prompt_id: str, prompt_data: Dict[str, Any]):
    """Verifica se o prompt exige formato Markdown ou User Story padrão."""
    system_prompt = prompt_data.get("system_prompt", "")
    format_patterns = [
        r"user story",
        r"markdown",
        r"##",
        r"formato",
        r"seções",
        r"estrutura",
    ]
    match = any(re.search(p, system_prompt, re.IGNORECASE) for p in format_patterns)
    assert match, (
        f"[{prompt_id}] O system_prompt não menciona nenhum formato de saída esperado "
        f"(User Story, Markdown, seções, etc.)."
    )


@pytest.mark.parametrize("prompt_id,prompt_data", ALL_PROMPTS, ids=PROMPT_IDS)
def test_prompt_has_few_shot_examples(prompt_id: str, prompt_data: Dict[str, Any]):
    """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot).

    Pulado para o v1 (prompt base intencional sem otimizações).
    """
    if prompt_id == "bug_to_user_story_v1":
        pytest.skip("v1 é o prompt base de baixa qualidade — few-shot não é exigido.")

    system_prompt = prompt_data.get("system_prompt", "")
    example_patterns = [
        r"exemplo",
        r"example",
        r"por exemplo",
        r"e\.g\.",
        r"como exemplo",
        r"input:",
        r"output:",
    ]
    match = any(re.search(p, system_prompt, re.IGNORECASE) for p in example_patterns)
    assert match, (
        f"[{prompt_id}] Nenhum exemplo (few-shot) encontrado no system_prompt. "
        f"Adicione ao menos um exemplo de entrada/saída para guiar o modelo."
    )


@pytest.mark.parametrize("prompt_id,prompt_data", ALL_PROMPTS, ids=PROMPT_IDS)
def test_prompt_no_todos(prompt_id: str, prompt_data: Dict[str, Any]):
    """Garante que nenhum [TODO] foi esquecido no texto do prompt."""
    system_prompt = prompt_data.get("system_prompt", "")
    user_prompt = prompt_data.get("user_prompt", "")
    todo_pattern = re.compile(r"\[TODO\]", re.IGNORECASE)

    assert not todo_pattern.search(system_prompt), (
        f"[{prompt_id}] system_prompt contém '[TODO]' não resolvido."
    )
    assert not todo_pattern.search(user_prompt), (
        f"[{prompt_id}] user_prompt contém '[TODO]' não resolvido."
    )


@pytest.mark.parametrize("prompt_id,prompt_data", ALL_PROMPTS, ids=PROMPT_IDS)
def test_minimum_techniques(prompt_id: str, prompt_data: Dict[str, Any]):
    """Verifica se pelo menos 2 técnicas de prompting foram declaradas nos metadados.

    Pulado para o v1 (prompt base intencional sem técnicas aplicadas).
    """
    if prompt_id == "bug_to_user_story_v1":
        pytest.skip("v1 é o prompt base de baixa qualidade — técnicas não são exigidas.")

    techniques = prompt_data.get("techniques_applied", [])
    assert isinstance(techniques, list), (
        f"[{prompt_id}] 'techniques_applied' deve ser uma lista."
    )
    assert len(techniques) >= 2, (
        f"[{prompt_id}] Esperado ao menos 2 técnicas em 'techniques_applied', "
        f"encontradas: {len(techniques)} → {techniques}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
