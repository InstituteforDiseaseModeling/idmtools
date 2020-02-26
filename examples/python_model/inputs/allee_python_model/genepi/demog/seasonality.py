import math


def annual_cycle(year_max, year_min=0, coeff=2, cycle=365):
    """ Sinusoidal seasonal forcing function. """

    def f(t):

        if coeff == 0:
            return year_max

        if coeff % 2:
            raise Exception('Only supporting even sinusoid powers.')

        return year_min + (year_max - year_min) * pow(math.cos(3.1416 * t / cycle), coeff)

    return f