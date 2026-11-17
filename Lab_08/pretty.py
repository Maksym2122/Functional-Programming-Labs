from __future__ import annotations

from model import Action, MenuNode, Role, Separator, Submenu


def render_menu(node: MenuNode, role: Role | None = None, indent: int = 0) -> str:
    """
    Чиста рекурсивна функція для побудови текстового дерева меню.
    Якщо передано role, приховує недоступні для цієї ролі пункти.
    """
    prefix = "  " * indent

    match node:
        case Action(title=title, command=cmd, allowed_roles=roles):
            if role is not None and role not in roles:
                return ""
            return f"{prefix}- {title} [{cmd}]"

        case Separator(label=label):
            return f"{prefix}{label}"

        case Submenu(title=title, items=children, allowed_roles=roles):
            if role is not None and role not in roles:
                return ""

            rendered_children: list[str] = []
            for child in children:
                line = render_menu(child, role=role, indent=indent + 1)
                if line:
                    rendered_children.append(line)

            header = f"{prefix}+ {title}"
            if not rendered_children:
                return f"{header}\n{prefix}  (порожньо)"

            return "\n".join([header, *rendered_children])