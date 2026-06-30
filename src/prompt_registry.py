"""
Registro central de prompts do projeto.

Carrega o registry.yaml e fornece acesso tipado a cada prompt cadastrado.
Usado nos processos de push e validação para garantir consistência.
"""

import yaml
from pathlib import Path
from typing import NamedTuple, Optional


class PromptInfo(NamedTuple):
    id: str
    version: str
    path: Path
    description: str
    model: Optional[str] = None


class PromptRegistry:
    def __init__(self, prompts_dir: str = "prompts", registry_filename: str = "registry.yaml"):
        self.prompts_dir = Path(__file__).parent.parent / prompts_dir
        self.registry_path = self.prompts_dir / registry_filename
        self._load_registry()

    def _load_registry(self) -> None:
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Registry não encontrado: {self.registry_path}")

        with open(self.registry_path, "r", encoding="utf-8") as f:
            self.registry = yaml.safe_load(f)

        if "agents" not in self.registry:
            raise ValueError("O registry.yaml deve conter a chave 'agents'")

    def get_prompt(self, prompt_id: str) -> PromptInfo:
        """
        Retorna as informações de um prompt pelo seu ID.

        Args:
            prompt_id: Identificador do prompt (ex: 'bug_to_user_story_v2')

        Returns:
            PromptInfo com id, version, path, description e model

        Raises:
            ValueError: Se o prompt não existir no registry ou faltar campos obrigatórios
            FileNotFoundError: Se o arquivo .yml do prompt não existir em disco
        """
        agents = self.registry.get("agents", {})

        if prompt_id not in agents:
            available = list(agents.keys())
            raise ValueError(f"Prompt '{prompt_id}' não encontrado. Disponíveis: {available}")

        agent_config = agents[prompt_id]

        required_fields = ["current_version", "path", "description"]
        missing_fields = [f for f in required_fields if f not in agent_config]
        if missing_fields:
            raise ValueError(
                f"Campos obrigatórios ausentes para '{prompt_id}': {missing_fields}"
            )

        prompt_path = self.prompts_dir / agent_config["path"]

        if not prompt_path.exists():
            raise FileNotFoundError(f"Arquivo do prompt não encontrado: {prompt_path}")

        return PromptInfo(
            id=prompt_id,
            version=agent_config["current_version"],
            path=prompt_path,
            description=agent_config["description"],
            model=agent_config.get("model"),
        )

    def list_prompts(self) -> list[str]:
        """Retorna a lista de IDs de todos os prompts cadastrados no registry."""
        return list(self.registry.get("agents", {}).keys())


registry = PromptRegistry()
