import os
from dataclasses import dataclass
from pathlib import Path

import yaml

ENV_DIR = Path(__file__).parent / "environments"


@dataclass(frozen=True)
class Settings:
    env: str
    base_url: str
    api_url: str
    timeout_ms: int

    @property
    def host(self) -> str:
        return self.base_url.split("://", 1)[-1].rstrip("/")


def load_settings(env: str) -> Settings:
    path = ENV_DIR / f"{env}.yaml"
    if not path.exists():
        available = ", ".join(p.stem for p in ENV_DIR.glob("*.yaml"))
        raise ValueError(f"Unknown env '{env}'. Available: {available}")

    values = yaml.safe_load(path.read_text())

    # env vars win over the yaml file, handy in CI
    return Settings(
        env=env,
        base_url=os.getenv("BASE_URL", values["base_url"]).rstrip("/"),
        api_url=os.getenv("API_URL", values["api_url"]).rstrip("/"),
        timeout_ms=int(os.getenv("TIMEOUT_MS", values.get("timeout_ms", 15000))),
    )
