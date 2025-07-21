"""Database repositories."""

from .base_repository import BaseRepository
from .{{ prefix_name }}_repository import {{ PrefixName }}Repository

__all__ = [
    "BaseRepository",
    "{{ PrefixName }}Repository",
] 