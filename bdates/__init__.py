from collections import Counter
from datetime import datetime
import enumerations
import pytz
import re

# the tzinfo (a.k.a. timezone) defaults to UTC
# you can override this by setting bdates.timezone to what you wish
global tzinfo
tzinfo = pytz.UTC

month_to_number = {
                 "Jan": 1,
                 "January": 1,
                 "Feb": 2,
                 "Febuary": 2,
                 "February": 2,
                 "Mar": 3,
                 "March": 3,
                 "Apr": 4,
                 "April": 4,
                 "May": 5,
                 "Jun": 6,
                 "June": 6,
                 "Jul": 7,
                 "July": 7,
                 "Aug": 8,
                 "August": 8,
                 "Sep": 9,
                 "Sept": 9,
                 "September": 9,
                 "Oct": 10,
                 "October": 10,
                 "Nov": 11,
                 "November": 11,
                 "Dec": 12,
                 "December": 12
}

def generate_patterns():
    global patterns
    patterns = {}

    # iterate through the names of the variables in the enumerations
    for key in dir(enumerations):

        # ignore inherited methods that come with most python modules
        # also ignore short variables of 1 length
        if not key.startswith("__") and len(key) > 1:
            pattern = "(?P<" + key + ">" + "|".join(getattr(enumerations, key)) + ")"

            # check to see if pattern is in unicode
            # if it's not convert it
            if isinstance(pattern, str):
                pattern = pattern.decode("utf-8")

            patterns[key] = pattern

    #merge months as regular name, abbreviation and number all together
    patterns['day'] = u'(?P<day_of_the_month>' + patterns['days_of_the_month_as_numbers'] + u'|' + patterns['days_of_the_month_as_ordinal'] + ')(?!\d{2,4})'

    #merge months as regular name, abbreviation and number all together
    # makes sure that it doesn't pull out 3 as the month in January 23, 2015
    patterns['month'] = u'(?<!\d)(?P<month>' + patterns['months_verbose'] + u'|' + patterns['months_abbreviated'] + u'|' + patterns['months_as_numbers'] + u')'

    # matches the year as two digits or four
    # tried to match the four digits first
    # (?!, \d{2,4}) makes sure it doesn't pick out 23 as the year in January 23, 2015
    patterns['year'] = u'(?P<year>\d{4}|\d{2})(?!, \d{2,4})'

    # spaces or punctuation separatings days, months and years
    # blank space, comma, dash, period, backslash
    # todo: write code for forward slash, an escape character
    patterns['punctuation'] = u"(?: |,|-|\.|\/){1,2}"

global patterns
generate_patterns()

def get_date_from_match_group(match):
    #print "starting get_date_from_match_group with ", match
    #print dir(match)
    #print match.group(0)
    #print match.groupdict()
    month = match.group("month")
    if month.isdigit():
        month = int(month)
    else:
        month = month_to_number[month]

    try:
        day = int(match.group("day_of_the_month"))
    except Exception as e:
        #print "exception is", e
        day = 1

    return datetime(int(match.group("year")), month, day, tzinfo=tzinfo)
 
def extract_dates(text):
    global patterns

    # convert to unicode if the text is in a bytestring
    # we conver to unicode because it is easier to work with
    # and it handles text in foreign languages much better
    if isinstance(text, str):
        text = text.decode('utf-8')

    dates = []

    matches = []
    
    # add day month year to matches
    for match in re.finditer(re.compile(u"(?P<date>" + "(" + patterns['day'] + patterns['punctuation'] + ")?" + patterns['month'] + patterns['punctuation'] + patterns['year'] + u")", re.MULTILINE|re.IGNORECASE), text):
        dates.append(get_date_from_match_group(match))

    # add month day year to matches
    for match in re.finditer(re.compile(u"(?P<date>" + patterns['month'] + patterns['punctuation'] + patterns['day'] + patterns['punctuation'] + patterns['year'] + u")", re.MULTILINE|re.IGNORECASE), text):
        dates.append(get_date_from_match_group(match))

    # add year month day to matches
    # to make sure don't match 23 May 2015 as May 2, 2023
    for match in re.finditer(re.compile(u"(?P<date>" + patterns['year'] + patterns['punctuation'] + patterns['month'] + patterns['punctuation'] + patterns['day'] + u")", re.MULTILINE|re.IGNORECASE), text):
        dates.append(get_date_from_match_group(match))

    # sorts the dates by the number of times they appear in the text
    dates = [date for date, freq in Counter(dates).most_common()]

    return dates
