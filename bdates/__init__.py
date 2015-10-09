from collections import Counter
from dt import datetime
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

#num converts text to a number
def num(text):
    if text:
        if text.isdigit():
            return int(text)
        else:
            text_title = text.title()
            if text_title in month_to_number:
                return month_to_number[text_title] 
            else:
                return None

# normalizes year to four digits
# e.g., 90s to 1990 and 11 to 2011
def normalize_year(y):
    current_year = date.today().year
    y_str = str(y).rstrip('s').rstrip("'")
    if len(y_str) == 2:
        y_int = int(y_str)
        if y_int > int(str(current_year+1)[2:]):
            y_int = int(str(current_year-100)[0:2] + y_str)
        else:
            y_int = int(str(current_year)[0:2] + y_str)
        return y_int
    else:
        return int(y)
    

def generate_patterns():
    global patterns
    patterns = {}

    # iterate through the names of the variables in the enumerations
    for key in dir(enumerations):

        # ignore inherited methods that come with most python modules
        # also ignore short variables of 1 length
        if not key.startswith("__") and len(key) > 1:
            pattern = "(?:" + "|".join(getattr(enumerations, key)) + ")"

            # check to see if pattern is in unicode
            # if it's not convert it
            if isinstance(pattern, str):
                pattern = pattern.decode("utf-8")

            patterns[key] = pattern

    #merge months as regular name, abbreviation and number all together
    patterns['day'] = u'(?P<day>' + patterns['days_of_the_month_as_numbers'] + u'|' + patterns['days_of_the_month_as_ordinal'] + ')(?!\d{2,4})'

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
    patterns['punctuation_nocomma'] = u"(?: |-|\.|\/){1,2}"
    

    patterns['dmy'] = u"(?P<dmy>" + patterns['day'].replace("day", "day_dmy") + patterns['punctuation'] + patterns['month'].replace("month","month_dmy") + patterns['punctuation'] + patterns['year'].replace("year", "year_dmy") + u")"

    patterns['mdy'] = u"(?P<mdy>" + patterns['month'].replace("month", "month_mdy") + patterns['punctuation'] + patterns['day'].replace("day","day_mdy") + patterns['punctuation'] + patterns['year'].replace("mdy","year_mdy") + u")"

    patterns['ymd'] = u"(?P<ymd>" + patterns['year'].replace("year","year_ymd") + patterns['punctuation'] + patterns['month'].replace("month","month_ymd") + patterns['punctuation'] + patterns['day'].replace("day","day_ymd") + u")"
    
    patterns['my'] = u"(?P<my>" + patterns['month'].replace("month","month_my") + patterns['punctuation_nocomma'] + patterns['year'].replace("year","year_my") + u")"

    patterns['date'] = u"(?P<date>" + patterns['mdy'] + "|" + patterns['dmy'] + "|" + patterns['ymd'] + "|" + patterns['my'] + u")"

global patterns
generate_patterns()

def date_from_dict(match):
    month = match['month']
    if month.isdigit():
        month = int(month)
    else:
        month = month_to_number[month.title()]

    try:
        day = int(match.group("day"))
    except Exception as e:
        #print "exception is", e
        day = 1

    try:
        return datetime(int(match.group("year")), month, day, tzinfo=tzinfo)
    except Exception as e:
        print e


def is_date_in_list(date, list_of_dates):
    return any((are_dates_same(date, d) for d in list_of_dates))

def are_dates_same(a,b):
    for level in ("year","month","day"):
        if level in a and level in b and a[level] != b[level]:
            return False
    return True
    

def remove_duplicates(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]
 
def extract_dates(text, sorting=None):
    global patterns

    # convert to unicode if the text is in a bytestring
    # we conver to unicode because it is easier to work with
    # and it handles text in foreign languages much better
    if isinstance(text, str):
        text = text.decode('utf-8')

    matches = []
    completes = []
    partials = []

    for match in re.finditer(re.compile(patterns['date'], re.MULTILINE|re.IGNORECASE), text):
    #    print "match is", match.groupdict()
        # this goes through the dictionary and removes empties and changes the keys back, e.g. from month_myd to month
        match = dict((k.split("_")[0], num(v)) for k, v in match.groupdict().iteritems() if num(v))

        if all(k in match for k in ("day","month", "year")): 
            completes.append(match)
        else:
            partials.append(match)

    #print "\ncompletes are", completes

    # iterate through partials
    # if a more specific date is given in the completes, drop the partial
    # for example if Feb 1, 2014 is picked up and February 2014, too, drop February 2014

    partials = [partial for partial in partials if not is_date_in_list(partial, completes)]
    #print "\npartials are", partials
  
    #convert completes and partials and return list ordered by:
    # complete/partial, most common, most recent
    completes = [date(normalize_year(d['year']),d['month'],d['day']) for d in completes]

    if sorting:
        counter = Counter(completes)
        completes = remove_duplicates(sorted(completes, key = lambda x: (counter[x], x.toordinal()), reverse=True))

    #average_date = mean([d for d in completes])

    return completes
e=extract_dates

def getFirstDateFromText(text):
    global patterns

    # convert to unicode if the text is in a bytestring
    # we conver to unicode because it is easier to work with
    # and it handles text in foreign languages much better
    if isinstance(text, str):
        text = text.decode('utf-8')

    for match in re.finditer(re.compile(patterns['date'], re.MULTILINE|re.IGNORECASE), text):
        match = dict((k.split("_")[0], num(v)) for k, v in match.groupdict().iteritems() if num(v))
        if all(k in match for k in ("day","month", "year")):
            return date(normalize_year(match['year']),match['month'],match['day'])

# the date of a webpage, like a blog or article, will often be the first date mentioned
getPageDate = getFirstDateFromText
