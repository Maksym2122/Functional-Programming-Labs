from __future__ import annotations

from evaluator import find_action_by_command, format_breadcrumb, get_available_actions
from model import Action, Separator, Submenu
from pretty import render_menu


def build_sample_menu() -> Submenu:
    """Створює демонстраційне багаторівневе дерево меню застосунку."""
    return Submenu(
        title="Головне меню",
        items=(
            Action(title="Переглянути профіль", command="profile.view"),
            Separator(),
            Submenu(
                title="Налаштування",
                allowed_roles=("user", "admin"),
                items=(
                    Action(
                        title="Змінити пароль",
                        command="settings.password",
                        allowed_roles=("user", "admin"),
                    ),
                    Action(
                        title="API ключі",
                        command="settings.api_keys",
                        allowed_roles=("admin",),
                    ),
                ),
            ),
            Separator("==="),
            Submenu(
                title="Адміністрування",
                allowed_roles=("admin",),
                items=(
                    Action(
                        title="Керування користувачами",
                        command="admin.users",
                        allowed_roles=("admin",),
                    ),
                    Action(
                        title="Системні логи",
                        command="admin.logs",
                        allowed_roles=("admin",),
                    ),
                ),
            ),
            Action(title="Вихід", command="app.exit"),
        ),
    )


def main() -> None:
    menu = build_sample_menu()

    print("=== ПОВНЕ ДЕРЕВО МЕНЮ ===")
    print(render_menu(menu))

    print("\n=== МЕНЮ ДЛЯ РОЛІ 'user' ===")
    print(render_menu(menu, role="user"))

    print("\n=== ДОСТУПНІ ДІЇ ДЛЯ 'guest' ===")
    for act in get_available_actions(menu, role="guest"):
        print(f"• {act.title} -> {act.command}")

    print("\n=== ДОСТУПНІ ДІЇ ДЛЯ 'admin' ===")
    admin_actions = get_available_actions(menu, role="admin")
    for act in admin_actions:
        print(f"• {act.title} -> {act.command}")

    found = find_action_by_command(menu, "admin.logs", role="admin")
    print(f"\nПошук 'admin.logs' для admin: {found}")

    crumb = format_breadcrumb((menu, Action("Профіль", "profile.view")))
    print(f"Шлях навігації: {crumb}")


if __name__ == "__main__":
    main()