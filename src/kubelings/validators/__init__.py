"""Exercise validator registry and module loader."""

import importlib
import pkgutil
from typing import Any, Callable, Optional

ValidatorFunc = Callable[[Any, str], None]
_VALIDATORS: dict[str, ValidatorFunc] = {}
_LOADED: bool = False


def register_validator(name: str) -> Callable[[ValidatorFunc], ValidatorFunc]:
    """Register a validation function for a specific exercise name."""

    def decorator(fn: ValidatorFunc) -> ValidatorFunc:
        _VALIDATORS[name] = fn
        return fn

    return decorator


def get_validator(name: str) -> Optional[ValidatorFunc]:
    """Retrieve the registered validation function for an exercise."""
    if name not in _VALIDATORS and not _LOADED:
        load_all_validators()
    return _VALIDATORS.get(name)


def load_all_validators() -> None:
    """Import all chapter validator modules to populate registry."""
    global _LOADED
    import kubelings.validators as val_pkg

    for _, module_name, _ in pkgutil.iter_modules(val_pkg.__path__):
        if module_name != "__init__":
            importlib.import_module(f"kubelings.validators.{module_name}")
    _LOADED = True


__all__ = [
    "ValidatorFunc",
    "get_validator",
    "load_all_validators",
    "register_validator",
]
