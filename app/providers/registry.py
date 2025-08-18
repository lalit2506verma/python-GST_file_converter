from typing import Dict
from app.providers.base import SalesProvider
from app.providers.meesho import MeeshoProvider

_registry: Dict[str, SalesProvider] = {
    "meesho": MeeshoProvider(),
}

def get_provider(name: str) -> SalesProvider:
    if name not in _registry:
        raise ValueError(f"Unknown provider: {name}")
    return _registry[name]
