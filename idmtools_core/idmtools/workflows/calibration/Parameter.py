class Parameter:
    def __init__(self, name: str, min: float, max: float, guess: float):
        self.name = name
        self.min = min
        self.max = max
        self.value = guess
