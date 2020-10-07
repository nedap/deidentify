import pytest

from deidentify.surrogates.generators import Date, DateSurrogates, RandomData
from deidentify.surrogates.generators.date import (adjust_long_date_span, fully_parsed,
                                        infer_format, max_date,
                                        minimum_season_offsets, year_span)


def test_infer_format():
    assert infer_format('Tuesday 5 March 2019 08:59').format == '%A %d %B %Y %H:%M'
    assert infer_format('Friday (10 June)').format == '%A (%d %B)'
    assert infer_format('10 November').format == '%d %B'
    assert infer_format('August 3, 2009').format == '%B %d, %Y'
    assert infer_format('2 May 1980').format == '%d %b %Y'
    assert infer_format('20-08-2016').format == '%d-%m-%Y'
    assert infer_format('Friday').format == '%A'
    assert infer_format('23 feb.').format == '%d %b.'
    assert infer_format('01 01 2015').format == '%d %m %Y'
    assert infer_format('22/05/13').format == '%d/%m/%y'
    assert infer_format('0411').format == '%Y'
    # Odd edge case which results into a parsing including timezone information.
    # This should be handled gracefully.
    assert infer_format('15-34-2019').format == '%H-%M%z'


def test_infer_format_multiple_languages():
    date = infer_format('dinsdag 5 maart 2019 08:59')
    assert date.format == '%A %d %B %Y %H:%M'
    assert date.locale == 'nl_NL.UTF-8'

    date = infer_format('Tuesday 5 March 2019 08:59')
    assert date.format == '%A %d %B %Y %H:%M'
    assert date.locale == 'en_US.UTF-8'

    date = infer_format('Dienstag 5 März 2019 08:59')
    assert date.format == '%A %d %B %Y %H:%M'
    assert date.locale == 'de_DE.UTF-8'


def test_infer_format_unanchored_weekdays():
    date = infer_format('vrijdag')
    assert date.format == '%A'
    assert date.locale == 'nl_NL.UTF-8'
    assert date.datetime.year == 1900
    assert date.datetime.day == 15
    assert date.datetime.month == 1


def test_infer_format_invalid_date():
    date = infer_format('Tuesday 5 March 2019 08:59')
    assert date.format == '%A %d %B %Y %H:%M'
    assert date.locale == 'en_US.UTF-8'
    assert date.date_string == 'Tuesday 5 March 2019 08:59'

    with pytest.raises(ValueError):
        date = infer_format('Tuesday 5 Marc 2019 08:59')


def test_fully_parsed():
    assert fully_parsed('%d-%m-%Y')
    assert fully_parsed('%A %d %B %Y %H:%M')
    assert fully_parsed('%Y-%m-%dT%H:%M:%S%z')
    assert not fully_parsed('20082016')
    assert not fully_parsed('%d082016')
    assert not fully_parsed('%d/082016')
    assert not fully_parsed('%d-%m-2016')
    assert not fully_parsed('%d-%m-%Y January')
    assert not fully_parsed('January')


def test_year_anchored():
    assert Date('01-01-1905', '%d-%m-%Y').year_anchored()
    assert Date('01-01-18', '%d-%m-%y').year_anchored()
    assert not Date('01-01', '%d-%m').year_anchored()


def test_day_anchored():
    assert Date('01-01-1905', '%d-%m-%Y').day_anchored()
    assert not Date('01-1905', '%m-%Y').day_anchored()


def test_max_date():
    dates = [
        Date('01-01-1905', '%d-%m-%Y'),
        Date('01-02', '%d-%m'),
        Date('01-01-1989', '%d-%m-%Y'),
    ]
    most_recent = max_date(dates)
    assert most_recent == Date('01-01-1989', '%d-%m-%Y')

    dates = [
        Date('01-01-1905', '%d-%m-%Y'),
        Date('01-01-1905', '%d-%m-%Y')
    ]
    most_recent = max_date(dates)
    assert most_recent == Date('01-01-1905', '%d-%m-%Y')

    dates = [
        Date('01-01', '%d-%m'),
        Date('01-01-1905', '%d-%m-%Y'),
    ]
    most_recent = max_date(dates)
    assert most_recent == Date('01-01-1905', '%d-%m-%Y')


def test_max_dates_raises_unanchored():
    dates = [
        Date('01-01', '%d-%m'),
        Date('01-12', '%d-%m'),
    ]
    with pytest.raises(ValueError) as exec_info:
        _ = max_date(dates)

    expected_exc = 'max_date() arg does not contain any year-anchored date'
    assert expected_exc in str(exec_info.value).lower()


def test_year_span():
    date_a = Date('01-01-1905', '%d-%m-%Y')
    date_b = Date('01-01-1989', '%d-%m-%Y')

    assert year_span(date_a, date_b) == 84


def test_adjust_long_date_span():
    dates_given = [
        Date('03-11-1899', '%d-%m-%Y'),
        Date('04-05-1900', '%d-%m-%Y'),
        Date('01-01-1915', '%d-%m-%Y'),
        Date('01-01-1995', '%d-%m-%Y')
    ]

    dates_expected = [
        Date('03-11-1904', '%d-%m-%Y'),
        Date('04-05-1904', '%d-%m-%Y'),
        Date('01-01-1915', '%d-%m-%Y'),
        Date('01-01-1995', '%d-%m-%Y'),
    ]

    most_recent = Date('01-01-1995', '%d-%m-%Y')
    for given, expected in zip(dates_given, dates_expected):
        shifted = adjust_long_date_span(given, most_recent=most_recent, max_delta=90)
        assert shifted == expected


def test_adjust_long_date_span_disregard_timezones():
    dt_aware = Date('15-34-2019', '%H-%M%z')
    dt_unaware = Date('ma', '%a', date_locale='nl_NL.UTF-8')
    assert adjust_long_date_span(dt_unaware, most_recent=dt_aware, max_delta=90) == dt_unaware


def test_adjust_long_date_span_preserves_locale():
    dates_given = [
        Date('03 November 1899', '%d %B %Y', date_locale='de_DE.UTF-8'),
        Date('04 Mai 1900', '%d %B %Y', date_locale='de_DE.UTF-8'),
        Date('01 Januar 1915', '%d %B %Y', date_locale='de_DE.UTF-8'),
        Date('01 January 1995', '%d %B %Y', date_locale='en_US.UTF-8')
    ]

    dates_expected = [
        Date('03 November 1904', '%d %B %Y', date_locale='de_DE.UTF-8'),
        Date('04 Mai 1904', '%d %B %Y', date_locale='de_DE.UTF-8'),
        Date('01 Januar 1915', '%d %B %Y', date_locale='de_DE.UTF-8'),
        Date('01 January 1995', '%d %B %Y', date_locale='en_US.UTF-8')
    ]

    most_recent = Date('01-01-1995', '%d-%m-%Y')
    for given, expected in zip(dates_given, dates_expected):
        shifted = adjust_long_date_span(given, most_recent=most_recent, max_delta=90)
        assert shifted == expected


def test_season_offsets():
    fmt = '%Y-%m-%d'
    spring_date = Date('2018-04-24', fmt)
    summer_date = Date('2018-7-7', fmt)
    autumn_date = Date('2018-11-11', fmt)
    winter_date_end_of_year = Date('2018-12-22', fmt)
    winter_date_start_of_year = Date('2019-1-7', fmt)
    border_date = Date('2018-12-21', fmt)

    assert spring_date.season_offsets() == (34, 57)
    assert summer_date.season_offsets() == (16, 77)
    assert autumn_date.season_offsets() == (49, 39)
    assert winter_date_end_of_year.season_offsets() == (1, 88)
    assert winter_date_start_of_year.season_offsets() == (17, 72)
    assert border_date.season_offsets() == (0, 89)


def test_season_offsets_unanchored_dates():
    missing_year = Date('04-24', '%m-%d')
    missing_day = Date('2018-04', '%Y-%m')

    assert missing_year.season_offsets() == (34, 57)
    assert missing_day.season_offsets() == (25, 66)


def test_minimum_season_offsets():
    fmt = '%Y-%m-%d'
    dates = [
        Date('2018-04-24', fmt),
        Date('2018-7-7', fmt),
        Date('2018-11-11', fmt),
        Date('2018-12-22', fmt),
        Date('2019-1-7', fmt),
        Date('2018-12-21', fmt)
    ]

    negative_shift, positive_shift = minimum_season_offsets(dates)
    assert (negative_shift, positive_shift) == (0, 39)


def test_random_year_day_shift():
    annotations = [
        '2018-04-24',
        '2018-7-7',
        '2018-11-11',
        '2018-12-22',
        '2019-1-7',
        '2018-12-21'
    ]

    for _ in range(100):
        date_surrogates = DateSurrogates(annotations,
                                         year_shift_base=65,
                                         year_shift_fuzz=10,
                                         random_data=None)

        # number of years to shift should be between 65+-10 years
        # according to year_shift_base and year_shift_fuzz
        assert date_surrogates.year_shift in list(range(55, 76))
        # number of days to shift should be in [1,39] see test_minimum_season_offsets test case
        assert date_surrogates.day_shift in list(range(1, 40))


def test_date_surrogate_generator():
    annotations = [
        '01 januari 1915', '01-02', 'marc 2001', 'February 2001', '01-02-2010',
    ]

    date_surrogates = DateSurrogates(annotations, random_data=RandomData(42))
    assert date_surrogates.replace_all() == [
        '09 januari 2006',
        '09-02',
        None,
        'February 2086',
        '09-02-2095'
    ]


def test_date_surrogate_generator_unanchored_weekdays():
    class RandomDataMock(RandomData):
        def randint(self, a, b):
            # 0 year fuzz
            if a == 0 and b == 0:
                return 0
            # shift by 2 days
            return 2

    annotations = [
        '01 januari 1915',
        '01-02',
        # unanchored Friday will be set to 15/01/1900 (which is not a Friday, but this is ignored)
        'vrijdag',
    ]

    date_surrogates = DateSurrogates(annotations,
                                     year_shift_base=10,
                                     year_shift_fuzz=0,
                                     random_data=RandomDataMock())
    assert date_surrogates.replace_all() == [
        '03 januari 1925',
        '03-02',
        'maandag',  # 17/01/1910 is a monday
    ]


def test_date_surrogate_generator_all_unanchored():
    class RandomDataMock(RandomData):
        def randint(self, a, b):
            # 0 year fuzz
            if a == 0 and b == 0:
                return 0
            # shift by 2 days
            return 2

    annotations = [
        '01 januari',
        '01-02',
        # unanchored Friday will be set to 15/01/1900 (which is not a Friday, but this is ignored)
        'vrijdag',
    ]

    date_surrogates = DateSurrogates(annotations,
                                     year_shift_base=10,
                                     year_shift_fuzz=0,
                                     random_data=RandomDataMock())
    assert date_surrogates.replace_all() == [
        '03 januari',
        '03-02',
        'maandag',  # 17/01/1910 is a monday
    ]


def test_switch_locale():
    import pydateinfer as dateinfer
    import locale

    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    assert dateinfer.infer(['12 January']) == '%d %B'
    assert dateinfer.infer(['12 januari']).split()[1] == 'januari'

    locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
    assert dateinfer.infer(['12 januari']) == '%d %B'

    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    assert dateinfer.infer(['12 January']) == '%d %B'
    assert dateinfer.infer(['12 januari']).split()[1] == 'januari'
