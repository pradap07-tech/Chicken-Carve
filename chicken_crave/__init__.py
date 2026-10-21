"""Chicken Crave package."""


def run():
    from .app import run as app_run

    app_run()


__all__ = ["run"]
