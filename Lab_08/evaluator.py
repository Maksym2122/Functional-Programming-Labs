from __future__ import annotations

from model import Action, HasTitle, MenuNode, Role, Separator, Submenu


def format_breadcrumb(items: tuple[HasTitle, ...]) -> str:
    """Демонстрація роботи зі структурним контрактом HasTitle (Protocol)."""
    return " > ".join(item.title for item in items)


def get_available_actions(node: MenuNode, role: Role) -> tuple[Action, ...]:
    """Чиста рекурсивна функція пошуку всіх доступних дій для заданої ролі."""
    match node:
        case Action(allowed_roles=roles) as action:
            return (action,) if role in roles else ()

        case Submenu(items=children, allowed_roles=roles):
            if role not in roles:
                return ()
            result: list[Action] = []
            for child in children:
                result.extend(get_available_actions(child, role))
            return tuple(result)

        case Separator():
            return ()


def find_action_by_command(node: MenuNode, command: str, role: Role) -> Action | None:
    """Пошук конкретної доступної дії за її кодом команди."""
    for action in get_available_actions(node, role):
        if action.command == command:
            return action
    return None