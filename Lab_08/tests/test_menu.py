from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from evaluator import find_action_by_command, format_breadcrumb, get_available_actions
from model import Action, Separator, Submenu
from pretty import render_menu


@pytest.fixture
def sample_menu() -> Submenu:
    return Submenu(
        title="Root",
        items=(
            Action("Home", "nav.home"),
            Separator(),
            Submenu(
                title="Account",
                allowed_roles=("user", "admin"),
                items=(
                    Action("Edit Profile", "acc.edit", allowed_roles=("user", "admin")),
                    Submenu(
                        title="Security",
                        allowed_roles=("admin",),
                        items=(Action("Audit Log", "sec.audit", allowed_roles=("admin",)),),
                    ),
                ),
            ),
        ),
    )


def test_single_action_access() -> None:
    act = Action("Delete DB", "db.drop", allowed_roles=("admin",))
    assert get_available_actions(act, "admin") == (act,)
    assert get_available_actions(act, "user") == ()
    assert get_available_actions(act, "guest") == ()


def test_separator_returns_no_actions() -> None:
    sep = Separator()
    assert get_available_actions(sep, "admin") == ()
    assert render_menu(sep) == "---"


def test_nested_menu_filtering(sample_menu: Submenu) -> None:
    guest_actions = get_available_actions(sample_menu, "guest")
    assert [a.command for a in guest_actions] == ["nav.home"]

    user_actions = get_available_actions(sample_menu, "user")
    assert [a.command for a in user_actions] == ["nav.home", "acc.edit"]

    admin_actions = get_available_actions(sample_menu, "admin")
    assert [a.command for a in admin_actions] == ["nav.home", "acc.edit", "sec.audit"]


def test_find_action_by_command(sample_menu: Submenu) -> None:
    assert find_action_by_command(sample_menu, "sec.audit", "user") is None
    found = find_action_by_command(sample_menu, "sec.audit", "admin")
    assert found is not None
    assert found.title == "Audit Log"


def test_render_menu_full_and_filtered(sample_menu: Submenu) -> None:
    guest_view = render_menu(sample_menu, role="guest")
    expected_guest = (
        "+ Root\n"
        "  - Home [nav.home]\n"
        "  ---"
    )
    assert guest_view == expected_guest


def test_render_empty_submenu() -> None:
    empty = Submenu(title="Empty", items=())
    assert render_menu(empty) == "+ Empty\n  (порожньо)"


def test_immutability() -> None:
    act = Action("Test", "test.run")
    with pytest.raises(FrozenInstanceError):
        act.title = "Changed"  # type: ignore[misc]


def test_protocol_has_title() -> None:
    sub = Submenu("File", items=())
    act = Action("Open", "file.open")
    assert format_breadcrumb((sub, act)) == "File > Open"