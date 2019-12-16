from deidentify.surrogates.generators import RandomData

class RandomDataMock(RandomData):

    def digit(self, digits='1'):
        return digits

    def ascii_lowercase(self):
        return 'c'

    def ascii_uppercase(self):
        return 'C'

    def choice(self, seq):
        return seq[0]
