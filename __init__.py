from datetime import datetime
import enumerations
import pytz
import re

# the tzinfo (a.k.a. timezone) defaults to UTC
# you can override this by setting bdates.timezone to what you wish
global tzinfo
tzinfo = pytz.UTC

month_to_number = {
                 "January": 1,
                 "Febuary": 2,
                 "February": 2,
                 "March": 3,
                 "April": 4,
                 "May": 5,
                 "June": 6,
                 "July": 7,
                 "August": 8,
                 "September": 9,
                 "October": 10,
                 "November": 11,
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
            print 'key is', key
            pattern = "(?P<" + key + ">" + "|".join(getattr(enumerations, key)) + ")"

            # check to see if pattern is in unicode
            # if it's not convert it
            if isinstance(pattern, str):
                pattern = pattern.decode("utf-8")

            patterns[key] = pattern

    #merge months as regular name, abbreviation and number all together
    patterns['day'] = u'(?P<day_of_the_month>' + patterns['days_of_the_month_as_numbers'] + u'|' + patterns['days_of_the_month_as_ordinal'] + ')'

    #merge months as regular name, abbreviation and number all together
    patterns['month'] = u'(?P<month>' + patterns['months_verbose'] + u'|' + patterns['months_abbreviated'] + u'|' + patterns['months_as_numbers'] + u')'

    # matches the year as two digits or four
    # tried to match the four digits first
    patterns['year'] = u'(?P<year>\d{4}|\d{2})'

    # spaces or punctuation separatings days, months and years
    # blank space, comma, dash, period, backslash
    # todo: write code for forward slash, an escape character
    patterns['punctuation'] = u"(?: |,|-|\.|\/){1,2}"

global patterns
generate_patterns()

def get_date_from_match_group(match):
    print "starting get_date_from_match_group with ", match
    print dir(match)
    print match.group(0)
    print match.groupdict()
    month = match.group("month")
    if month.isdigit():
        month = int(month)
    else:
        month = month_to_number[month]

    return datetime(int(match.group("year")), month, int(match.group("day_of_the_month")), tzinfo=tzinfo)
 
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
    for match in re.finditer(re.compile(u"(?P<date>" + patterns['day'] + patterns['punctuation'] + patterns['month'] + patterns['punctuation'] + patterns['year'] + u")", re.MULTILINE|re.IGNORECASE), text):
        dates.append(get_date_from_match_group(match))

    # add month day year to matches
    for match in re.finditer(re.compile(u"(?P<date>" + patterns['month'] + patterns['punctuation'] + patterns['day'] + patterns['punctuation'] + patterns['year'] + u")", re.MULTILINE|re.IGNORECASE), text):
        dates.append(get_date_from_match_group(match))

    # add year month day to matches
    for match in re.finditer(re.compile(u"(?P<date>" + patterns['year'] + patterns['punctuation'] + patterns['month'] + patterns['punctuation'] + patterns['day'] + u")", re.MULTILINE|re.IGNORECASE), text):
        dates.append(get_date_from_match_group(match))

    return dates
