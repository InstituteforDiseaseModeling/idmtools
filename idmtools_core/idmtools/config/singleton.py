from abc import ABCMeta, abstractmethod


class Singleton(metaclass=ABCMeta):
    _instance = None
    inid = False  # working but may not need it and we can use method initialized() for checking!

    @abstractmethod
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
            cls.inid = True
        return cls._instance

    # working!
    @classmethod
    def get_instance(cls):
        return cls._instance

    # not working...
    @classmethod
    def initialized(cls):
        return cls._instance is not None

    @classmethod
    def un_init(cls):
        cls._instance = None
        cls.inid = False

    @property
    def initcheck(cls):

        return type(cls)._instance is not None

