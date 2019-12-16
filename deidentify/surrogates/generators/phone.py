import re
from collections import defaultdict

from loguru import logger

from .base import ExactMatchGenerator

DIAL_CODES = ['6', '10', '111', '113', '114', '115', '117', '118', '13', '15', '161', '162', '164',
              '165', '166', '167', '168', '172', '174', '180', '181', '182', '183', '184', '186',
              '187', '20', '222', '223', '224', '226', '227', '228', '229', '23', '24', '251',
              '252', '255', '26', '294', '297', '299', '30', '313', '314', '315', '316', '317',
              '318', '320', '321', '33', '341', '342', '343', '344', '345', '346', '347', '348',
              '35', '36', '38', '40', '411', '412', '413', '416', '418', '43', '45', '46', '475',
              '478', '481', '485', '486', '487', '488', '492', '493', '495', '497', '499', '50',
              '511', '512', '513', '514', '515', '516', '517', '518', '519', '521', '522', '523',
              '524', '525', '527', '528', '529', '53', '541', '543', '544', '545', '546', '547',
              '548', '55', '561', '562', '566', '570', '571', '572', '573', '575', '577', '578',
              '58', '591', '592', '593', '594', '595', '596', '597', '598', '599', '70', '71',
              '72', '73', '74', '75', '76', '77', '78', '79']

DIAL_CODES_BY_LENGTH = defaultdict(list)

for code in DIAL_CODES:
    DIAL_CODES_BY_LENGTH[len(code)].append(code)


PHONE_PATTERN = r''.join((
    r"^(?:(?:\+|00)(31))?",  # group 1 = country code
    r"[ -]*[(0)]*[ \-\(]*",
    r"({})?".format('|'.join(DIAL_CODES)),  # group 2 = dial code
    r"[ \-\)]*",
    r"((?:\d[ -]*)+)",  # group 3 = phone number
))

SPLIT_PHONE = re.compile(PHONE_PATTERN, re.MULTILINE)


class PhoneFaxSurrogates(ExactMatchGenerator):

    def dial_code(self, length):
        return self.random_data.choice(DIAL_CODES_BY_LENGTH[length])

    @staticmethod
    def mask_phonenumber(annotation):
        match = SPLIT_PHONE.search(annotation)

        if not match or len(match.group(0)) < 7:
            # excluding dial code, the shortest dutch phone number can be 7 digits
            raise ValueError('Not a valid phone number')

        def sub_match(whole, match, group_id, pattern, replace):
            if not match.group(group_id):
                return whole

            start, end = match.span(group_id)

            return whole[:start] \
                + re.sub(pattern, replace, whole[start:end]) \
                + whole[end:]

        # country code
        annotation = sub_match(annotation, match, group_id=1, pattern=r'\d', replace='C')
        # dial code
        annotation = sub_match(annotation, match, group_id=2, pattern=r'\d', replace='D')
        # participant number
        annotation = sub_match(annotation, match, group_id=3, pattern=r'\d', replace='#')
        return annotation

    def replace_pattern(self, pattern):
        pattern = re.sub(r'C+', '31', pattern)

        dial_code = re.search(r'D+', pattern)
        if dial_code:
            random_code = self.dial_code(len(dial_code.group(0)))
            pattern = re.sub('D+', random_code, pattern)

        replaced = ''
        first_digit = True
        for char in pattern:
            replacement = char

            if char == '#':
                if first_digit:
                    replacement = self.random_data.digit(digits='123456789')
                    first_digit = False
                else:
                    replacement = self.random_data.digit()

            replaced += replacement

        return replaced

    def replace_one(self, annotation):
        # TODO: Add an annotation object that encapsules automatic replacement errors
        replacement = None

        try:
            pattern = self.mask_phonenumber(annotation)
            replacement = self.replace_pattern(pattern)
        except ValueError:
            logger.opt(exception=True).debug('Could not process phone {}'.format(annotation))

        return replacement
