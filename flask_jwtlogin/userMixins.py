from abc import ABC, abstractmethod


class AbstractUser(ABC):

    @abstractmethod
    def is_authenticated(self) ->bool:
        pass

    @abstractmethod
    def is_anonymous(self) ->bool:
        pass


class KnownUser(AbstractUser):
    def is_anonymous(self) -> bool:
        return False

    def is_authenticated(self) -> bool:
        return True


class AnonymousUser(AbstractUser):
    def is_anonymous(self) -> bool:
        return True

    def __init__(self):
        pass

    def is_authenticated(self) -> bool:
        return False
