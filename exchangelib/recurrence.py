import logging

from six import string_types

from .fields import IntegerField, EnumField, EnumListField, DateField, DateTimeField, EWSElementField, \
    MONTHS, WEEK_NUMBERS, WEEKDAYS
from .properties import EWSElement, IdChangeKeyMixIn

log = logging.getLogger(__name__)


def _month_to_str(month):
    return MONTHS[month-1] if isinstance(month, int) else month


def _weekday_to_str(weekday):
    return WEEKDAYS[weekday - 1] if isinstance(weekday, int) else weekday


def _week_number_to_str(week_number):
    return WEEK_NUMBERS[week_number - 1] if isinstance(week_number, int) else week_number


class Pattern(EWSElement):
    __slots__ = tuple()


class AbsoluteYearlyPattern(Pattern):
    # MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/absoluteyearlyrecurrence
    ELEMENT_NAME = 'AbsoluteYearlyRecurrence'

    FIELDS = [
        # The month of the year, from 1 - 12
        EnumField('month', field_uri='t:Month', enum=MONTHS, is_required=True),
        # The day of month of an occurrence, in range 1 -> 31. If a particular month has less days than the day_of_month
        # value, the last day in the month is assumed
        IntegerField('day_of_month', field_uri='t:DayOfMonth', min=1, max=31, is_required=True),
    ]

    __slots__ = tuple(f.name for f in FIELDS)

    def __str__(self):
        return 'Occurs on day %s of %s' % (self.day_of_month, _month_to_str(self.month))


class RelativeYearlyPattern(Pattern):
    # MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/relativeyearlyrecurrence
    ELEMENT_NAME = 'RelativeYearlyRecurrence'

    FIELDS = [
        # The weekday of the occurrence, as a valid ISO 8601 weekday number in range 1 -> 7 (1 being Monday).
        # Alternatively, the weekday can be one of the DAY (or 8), WEEK_DAY (or 9) or WEEKEND_DAY (or 10) consts which
        # is interpreted as the first day, weekday, or weekend day in the month, respectively.
        EnumField('weekday', field_uri='t:DaysOfWeek', enum=WEEKDAYS, is_required=True),
        # Week number of the month, in range 1 -> 5. If 5 is specified, this assumes the last week of the month for
        # months that have only 4 weeks
        EnumField('week_number', field_uri='t:DayOfWeekIndex', enum=WEEK_NUMBERS, is_required=True),
        # The month of the year, from 1 - 12
        EnumField('month', field_uri='t:Month', enum=MONTHS, is_required=True),
    ]

    __slots__ = tuple(f.name for f in FIELDS)

    def __str__(self):
        return 'Occurs on weekday %s in the %s week of %s' % (
            _weekday_to_str(self.weekday),
            _week_number_to_str(self.week_number),
            _month_to_str(self.month)
        )


class AbsoluteMonthlyPattern(Pattern):
    # MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/absolutemonthlyrecurrence
    ELEMENT_NAME = 'AbsoluteMonthlyRecurrence'

    FIELDS = [
        # Interval, in months, in range 1 -> 99
        IntegerField('interval', field_uri='t:Interval', min=1, max=99, is_required=True),
        # The day of month of an occurrence, in range 1 -> 31. If a particular month has less days than the day_of_month
        # value, the last day in the month is assumed
        IntegerField('day_of_month', field_uri='t:DayOfMonth', min=1, max=31, is_required=True),
    ]

    __slots__ = tuple(f.name for f in FIELDS)

    def __str__(self):
        return 'Occurs on day %s of every %s month(s)' % (self.day_of_month, self.interval)


class RelativeMonthlyPattern(Pattern):
    # MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/relativemonthlyrecurrence
    ELEMENT_NAME = 'RelativeMonthlyRecurrence'

    FIELDS = [
        # Interval, in months, in range 1 -> 99
        IntegerField('interval', field_uri='t:Interval', min=1, max=99, is_required=True),
        # The weekday of the occurrence, as a valid ISO 8601 weekday number in range 1 -> 7 (1 being Monday).
        # Alternatively, the weekday can be one of the DAY (or 8), WEEK_DAY (or 9) or WEEKEND_DAY (or 10) consts which
        # is interpreted as the first day, weekday, or weekend day in the month, respectively.
        EnumField('weekday', field_uri='t:DaysOfWeek', enum=WEEKDAYS, is_required=True),
        # Week number of the month, in range 1 -> 5. If 5 is specified, this assumes the last week of the month for
        # months that have only 4 weeks.
        EnumField('week_number', field_uri='t:DayOfWeekIndex', enum=WEEK_NUMBERS, is_required=True),
    ]

    __slots__ = tuple(f.name for f in FIELDS)

    def __str__(self):
        return 'Occurs on weekday %s in the %s week of every %s month(s)' % (
            _weekday_to_str(self.weekday),
            _week_number_to_str(self.week_number),
            self.interval
        )


class WeeklyPattern(Pattern):
    # MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/weeklyrecurrence
    ELEMENT_NAME = 'WeeklyRecurrence'

    FIELDS = [
        # Interval, in weeks, in range 1 -> 99
        IntegerField('interval', field_uri='t:Interval', min=1, max=99, is_required=True),
        # List of valid ISO 8601 weekdays, as list of numbers in range 1 -> 7 (1 being Monday)
        EnumListField('weekdays', field_uri='t:DaysOfWeek', enum=WEEKDAYS, is_required=True),
        # The first day of the week. Defaults to Monday
        EnumField('first_day_of_week', field_uri='t:FirstDayOfWeek', enum=WEEKDAYS, default=1, is_required=True),
    ]

    __slots__ = tuple(f.name for f in FIELDS)

    def __str__(self):
        if isinstance(self.weekdays, string_types):
            weekdays = [self.weekdays]
        elif isinstance(self.weekdays, int):
            weekdays = [_weekday_to_str(self.weekdays)]
        else:
            weekdays = [_weekday_to_str(i) for i in self.weekdays]
        return 'Occurs on weekdays %s of every %s week(s) where the first day of the week is %s' % (
            ', '.join(weekdays), self.interval, _weekday_to_str(self.first_day_of_week)
        )


class DailyPattern(Pattern):
    # MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/dailyrecurrence
    ELEMENT_NAME = 'DailyRecurrence'

    FIELDS = [
        # Interval, in days, in range 1 -> 999
        IntegerField('interval', field_uri='t:Interval', min=1, max=999, is_required=True),
    ]

    __slots__ = tuple(f.name for f in FIELDS)

    def __str__(self):
        return 'Occurs every %s day(s)' % self.interval


class Boundary(EWSElement):
    __slots__ = tuple()


class NoEndPattern(Boundary):
    # MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/noendrecurrence
    ELEMENT_NAME = 'NoEndRecurrence'

    FIELDS = [
        # Start date, as EWSDate
        DateField('start', field_uri='t:StartDate', is_required=True),
    ]

    __slots__ = tuple(f.name for f in FIELDS)


class EndDatePattern(Boundary):
    # MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/enddaterecurrence
    ELEMENT_NAME = 'EndDateRecurrence'

    FIELDS = [
        # Start date, as EWSDate
        DateField('start', field_uri='t:StartDate', is_required=True),
        # End date, as EWSDate
        DateField('end', field_uri='t:EndDate', is_required=True),
    ]

    __slots__ = tuple(f.name for f in FIELDS)


class NumberedPattern(Boundary):
    # MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/numberedrecurrence
    ELEMENT_NAME = 'NumberedRecurrence'

    FIELDS = [
        # Start date, as EWSDate
        DateField('start', field_uri='t:StartDate', is_required=True),
        # The number of occurrences in this pattern, in range 1 -> 999
        IntegerField('number', field_uri='t:NumberOfOccurrences', min=1, max=999, is_required=True),
    ]

    __slots__ = tuple(f.name for f in FIELDS)


class Occurrence(IdChangeKeyMixIn):
    # MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/occurrence
    ELEMENT_NAME = 'Occurrence'

    LOCAL_FIELDS = [
        # The modified start time of the item, as EWSDateTime
        DateTimeField('start', field_uri='t:Start'),
        # The modified end time of the item, as EWSDateTime
        DateTimeField('end', field_uri='t:End'),
        # The original start time of the item, as EWSDateTime
        DateTimeField('original_start', field_uri='t:OriginalStart'),
    ]
    FIELDS = IdChangeKeyMixIn.FIELDS + LOCAL_FIELDS

    __slots__ = tuple(f.name for f in LOCAL_FIELDS)


# Container elements:
# 'ModifiedOccurrences'
# 'DeletedOccurrences'


class FirstOccurrence(Occurrence):
    # MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/firstoccurrence
    ELEMENT_NAME = 'FirstOccurrence'
    __slots__ = tuple()


class LastOccurrence(Occurrence):
    # MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/lastoccurrence
    ELEMENT_NAME = 'LastOccurrence'
    __slots__ = tuple()


class DeletedOccurrence(EWSElement):
    # MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/deletedoccurrence
    ELEMENT_NAME = 'DeletedOccurrence'

    FIELDS = [
        # The modified start time of the item, as EWSDateTime
        DateTimeField('start', field_uri='t:Start'),
    ]

    __slots__ = tuple(f.name for f in FIELDS)


PATTERN_CLASSES = AbsoluteYearlyPattern, RelativeYearlyPattern, AbsoluteMonthlyPattern, RelativeMonthlyPattern, \
                   WeeklyPattern, DailyPattern
BOUNDARY_CLASSES = NoEndPattern, EndDatePattern, NumberedPattern


class Recurrence(EWSElement):
    # MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/recurrence-recurrencetype
    ELEMENT_NAME = 'Recurrence'

    FIELDS = [
        EWSElementField('pattern', value_cls=Pattern),
        EWSElementField('boundary', value_cls=Boundary),
    ]

    __slots__ = tuple(f.name for f in FIELDS)

    def __init__(self, **kwargs):
        # Allow specifying a start, end and/or number as a shortcut to creating a boundary
        start = kwargs.pop('start', None)
        end = kwargs.pop('end', None)
        number = kwargs.pop('number', None)
        if any([start, end, number]):
            if 'boundary' in kwargs:
                raise ValueError("'boundary' is not allowed in combination with 'start', 'end' or 'number'")
            if start and not end and not number:
                kwargs['boundary'] = NoEndPattern(start=start)
            elif start and end and not number:
                kwargs['boundary'] = EndDatePattern(start=start, end=end)
            elif start and number and not end:
                kwargs['boundary'] = NumberedPattern(start=start, number=number)
            else:
                raise ValueError("Unsupported 'start', 'end', 'number' combination")
        super(Recurrence, self).__init__(**kwargs)

    @classmethod
    def from_xml(cls, elem, account):
        for pattern_cls in PATTERN_CLASSES:
            pattern_elem = elem.find(pattern_cls.response_tag())
            if pattern_elem is None:
                continue
            pattern = pattern_cls.from_xml(elem=pattern_elem, account=account)
            break
        else:
            pattern = None
        for boundary_cls in BOUNDARY_CLASSES:
            boundary_elem = elem.find(boundary_cls.response_tag())
            if boundary_elem is None:
                continue
            boundary = boundary_cls.from_xml(elem=boundary_elem, account=account)
            break
        else:
            boundary = None
        return cls(pattern=pattern, boundary=boundary)

    def __str__(self):
        return 'Pattern: %s, Boundary: %s' % (self.pattern, self.boundary)
