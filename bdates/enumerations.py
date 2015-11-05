days_of_the_week_verbose = ["Sunday","Monday","Tuesday","Wednesday","Wenesday","Wendsday","Thursday","Friday","Saturday"]

days_of_the_week_abbreviated = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

# range generates a list of numbers from 1 to 31
# map converts everthing in the list to unicode
days_of_the_month_as_numbers = map(unicode, list(reversed(range(1,32))))

# ordinal is a function that converts a number to its ordinal
# for example it converts 22 to 22nd
# we start it with __ because we want to keep it private
__ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
days_of_the_month_as_ordinal = [__ordinal(n) for n in range(1,32)]

months_verbose = ["January","Febuary","February","March","April","May","June","July","August","September","October","November","December"]

months_abbreviated = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"] 

# range generates a list of numbers from 1 to 12
# map converts everthing in the list to unicode
months_as_numbers = map(unicode,range(1,13))
