import datetime
import locale
import re
from datetime import datetime

import pydateinfer as dateinfer
from dateutil.relativedelta import relativedelta
from loguru import logger

from .base import SurrogateGenerator

# A date format can consist of all possible formatting directives and punctuation
DATE_FORMAT = re.compile(
    r'('
    r'%[aAwdbBmyYHIpMSfzZjUWcxX%]|'  # formatting directives
    r'[.,\/#!$\^&\*;:{}=\-_`~() ]|'  # punctuation
    r'T'                             # date time separator e.g., in %Y-%m-%dT%H:%M:%S
    r')*'
)


def fully_parsed(date_format):
    return len(DATE_FORMAT.sub('', date_format)) == 0


class Date:

    def __init__(self, date_string, date_format, date_locale='en_US.UTF-8'):
        self.date_string = date_string
        self.format = date_format
        self.locale = date_locale
        locale.setlocale(locale.LC_ALL, self.locale)
        self.datetime = datetime.strptime(date_string, self.format)

        if not self.day_anchored():
            self.datetime = self.datetime.replace(day=15)

    def year_anchored(self):
        return '%y' in self.format.lower()

    def day_anchored(self):
        return '%d' in self.format

    def season_offsets(self):
        from datetime import date
        current_date = self.datetime.date()
        year = current_date.year

        seasons = [
            (date(year, 3, 21), date(year, 6, 20)),  # spring
            (date(year, 6, 21), date(year, 9, 22)),  # summer
            (date(year, 9, 23), date(year, 12, 20)),  # autumn
        ]

        if date(year, 1, 1) <= current_date <= date(year, 3, 20):
            winter = (date(year - 1, 12, 21), date(year, 3, 20))
            seasons.append(winter)
        elif date(year, 12, 21) <= current_date <= date(year, 12, 31):
            winter = (date(year, 12, 21), date(year + 1, 3, 20))
            seasons.append(winter)

        return next(((current_date - start).days, (end - current_date).days)
                    for (start, end) in seasons
                    if start <= current_date <= end)

    def __str__(self):
        return u"Date(date_string={}, format={}, locale={}, datetime={})".format(
            self.date_string, self.format, self.locale, self.datetime)

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class NullDate(Date):

    def __init__(self, date_string='01-01-1001', date_format='%d-%m-%Y', date_locale='en_US.UTF-8'):
        super(NullDate, self).__init__(date_string, date_format, date_locale)

    def year_anchored(self):
        return False

    def day_anchored(self):
        return False

    def season_offsets(self):
        return (300, 300)


def infer_format(date_string, locales=('nl_NL.UTF-8', 'en_US.UTF-8', 'de_DE.UTF-8')):
    for locale_name in locales:
        locale.setlocale(locale.LC_ALL, locale_name)
        date_format = dateinfer.infer([date_string])

        if fully_parsed(date_format):
            return Date(date_string, date_format, locale_name)

    raise ValueError('Could parse date "{}" with given locales "{}"'.format(date_string, locales))


def max_date(dates):
    dates_filtered = [date for date in dates if date.year_anchored()]
    if not dates_filtered:
        raise ValueError('max_date() arg does not contain any year-anchored date')

    return max(dates_filtered, key=lambda date: date.datetime)


def year_span(date_a, date_b):
    return abs(relativedelta(date_a.datetime, date_b.datetime).years)


def shift_date(date, delta):
    new_datetime = date.datetime + delta
    locale.setlocale(locale.LC_ALL, date.locale)
    date_string = new_datetime.strftime(date.format)
    shifted_date = Date(date_string, date_format=date.format, date_locale=date.locale)
    return shifted_date


def adjust_long_date_span(date, most_recent, max_delta):
    if relativedelta(most_recent.datetime, date.datetime).years > max_delta:
        span = year_span(date, most_recent)
        delta = relativedelta(years=span - max_delta)
        return shift_date(date, delta)

    return date


def minimum_season_offsets(dates):
    # values longer than any season
    min_days_past = 300
    min_days_left = 300

    for date in dates:
        (days_past, days_left) = date.season_offsets()
        if days_past < min_days_past:
            min_days_past = days_past
        elif days_left < min_days_left:
            min_days_left = days_left

    return (min_days_past, min_days_left)


class DateSurrogates(SurrogateGenerator):

    def __init__(self, annotations, year_shift_base=65, year_shift_fuzz=20, random_data=None):
        super(DateSurrogates, self).__init__(annotations=annotations, random_data=random_data)

        self.dates = self._parse_dates(self.annotations)
        self.year_shift = year_shift_base + self.random_data.randint(
            -year_shift_fuzz, year_shift_fuzz)

        season_offsets = minimum_season_offsets(self.dates)
        max_offset = max(season_offsets)
        max_idx = season_offsets.index(max_offset)
        # if max_offset is 0, we still shift by 1 day
        day_shift = self.random_data.randint(1, max(max_offset, 1))
        self.day_shift = -day_shift if max_idx == 0 else day_shift

    @staticmethod
    def _parse_dates(dates):
        parsed = []
        dates_failed = []

        for date in dates:
            try:
                parsed.append(infer_format(date))
            except (ValueError, re.error):
                dates_failed.append(date)
                parsed.append(NullDate())

        if dates_failed:
            logger.debug('Could not parse {} of {} dates in this document. Failed dates:'
                         '{}'.format(len(dates_failed), len(dates), dates_failed))

        return parsed

    def replace_all(self):
        replaced = []

        try:
            most_recent = max_date(self.dates)
        except ValueError:
            # No year-anchored dates: any date can be used here
            most_recent = self.dates[0]

        for date in self.dates:
            # TODO: Add an annotation object that encapsules automatic replacement errors
            if isinstance(date, NullDate):
                replaced.append(None)
                continue

            adjusted = adjust_long_date_span(date, most_recent=most_recent, max_delta=89)
            delta = relativedelta(days=self.day_shift, years=self.year_shift)
            shifted_date = shift_date(adjusted, delta)
            replaced.append(shifted_date.date_string)

        return replaced
