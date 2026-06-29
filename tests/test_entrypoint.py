from __future__ import annotations

from unittest.mock import Mock, patch

from mewcode.config import AppConfig, ProviderConfig
from mewcode.permissions import PermissionMode


def _config() -> AppConfig:
    return AppConfig(
        providers=[
            ProviderConfig(
                name="fake",
                protocol="openai",
                base_url="http://fake",
                model="fake",
                api_key="x",
            )
        ],
        permission_mode=PermissionMode.DEFAULT.value,
    )


def test_main_uses_default_textual_driver_by_default(monkeypatch):
    monkeypatch.delenv("MEWCODE_NO_ALT_SCREEN", raising=False)
    monkeypatch.setattr("sys.argv", ["mewcode"])

    with patch("mewcode.__main__.load_config", return_value=_config()), patch(
        "mewcode.__main__.load_hooks", return_value=[]
    ), patch("mewcode.app.MewCodeApp") as app_cls:
        app_cls.return_value.run = Mock()
        from mewcode.__main__ import main

        main()

    _, kwargs = app_cls.call_args
    assert "driver_class" not in kwargs
    app_cls.return_value.run.assert_called_once()


def test_main_can_enable_no_alt_screen_driver(monkeypatch):
    monkeypatch.setenv("MEWCODE_NO_ALT_SCREEN", "1")
    monkeypatch.setattr("sys.argv", ["mewcode"])

    with patch("mewcode.__main__.load_config", return_value=_config()), patch(
        "mewcode.__main__.load_hooks", return_value=[]
    ), patch("mewcode.app.MewCodeApp") as app_cls:
        app_cls.return_value.run = Mock()
        from mewcode.__main__ import main

        main()

    _, kwargs = app_cls.call_args
    assert kwargs["driver_class"].__name__ == "NoAltScreenDriver"
    app_cls.return_value.run.assert_called_once()
