def gravity(distination_population, distance, G=1e-3, a=1, b=2):
    """
    Gravity model of migration between population centers.
    (1e-3) : 1/day to pop=1,000 village @ 1km
    """
    return G * distination_population**a / distance**b
