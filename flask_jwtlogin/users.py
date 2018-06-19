from flask import g
from werkzeug.local import LocalProxy


class KnownUser:
    def is_anonymous(self) -> bool:
        return False

    def is_authenticated(self) -> bool:
        return True


class AnonymousUser:
    def is_anonymous(self) -> bool:
        return True

    def is_authenticated(self) -> bool:
        return False

    def __init__(self):
        pass


def _safe_load_from_g():
    if hasattr(g, "_user"):
        return getattr(g, "_user")
    return AnonymousUser()


current_user = LocalProxy(lambda: _safe_load_from_g())