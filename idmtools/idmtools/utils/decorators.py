class abstractstatic(staticmethod):
    """
    Decorator for defining a method both as static and abstract
    """
    __slots__ = ()

    def __init__(self, function):
        super(abstractstatic, self).__init__(function)
        function.__isabstractmethod__ = True

    __isabstractmethod__ = True
