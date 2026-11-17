from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol, TypeAlias, Union

# Обмежений набір ролей користувача
Role: TypeAlias = Literal["guest", "user", "admin"]


# Структурний контракт (Protocol) для об'єктів, що мають заголовок
class HasTitle(Protocol):
    @property
    def title(self) -> str: ...


@dataclass(frozen=True)
class Action:
    """Кінцевий пункт меню, що виконує певну дію."""

    title: str
    command: str
    allowed_roles: tuple[Role, ...] = ("guest", "user", "admin")


@dataclass(frozen=True)
class Separator:
    """Візуальний розділювач пунктів меню."""

    label: str = "---"


@dataclass(frozen=True)
class Submenu:
    """Вкладене підменю, що містить дочірні вузли."""

    title: str
    items: tuple[MenuNode, ...]
    allowed_roles: tuple[Role, ...] = ("guest", "user", "admin")


# Алгебраїчний тип даних (Sum Type) для дерева меню
MenuNode: TypeAlias = Union[Action, Submenu, Separator]