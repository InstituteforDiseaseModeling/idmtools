class EntityMetaData:
    def __init__(self, **kwargs):
        for k,v in kwargs:
            setattr(self, k, v)