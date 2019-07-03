class Transmission(object):
    """
    Characteristics of transmitted sporozoite and parent gametocytes
    """

    def __init__(self, parentGenomeIds=(None, None), genome=None,
                       parentInfection=None, infection=None,
                       populationId=None, day=None):

        # sporozoite properties
        self.genome = genome
        self.infection = infection

        # male + female gametocyte properties
        self.parentGenomeIds = parentGenomeIds
        self.parentInfection = parentInfection

        # other info
        self.populationId = populationId
        self.day = day

    def to_tuple(self):
        return (self.day, self.populationId,
                getattr(self.infection, 'id', None),
                getattr(self.parentInfection, 'id', None),
                self.parentGenomeIds[0], self.parentGenomeIds[1],
                self.genome.id)
