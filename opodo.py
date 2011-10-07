import datetime

from opodo import opodo


def datesiterator(start, end):
    assert start <= end
    while start <= end:
        yield start
        start += datetime.timedelta(days=1)


def findFly(departureAirportCode, arrivalAirportCode, departureDate):
    o = opodo.Opodo(departureAirportCode, arrivalAirportCode, departureDate)
    try:
        #return (3.14, o.url)
        #raise opodo.NoResultsException(o.url)
        return (o.search(), o.url)
    except opodo.NoResultsException as v:
        return ('None', v.url)


if __name__ == '__main__':
    for d in datesiterator(datetime.date(2011, 10, 8) ,datetime.date(2011, 10, 15)):
        euros, link = findFly('BLQ', 'LON', d)
        print d
        print euros, 'Euros'
        print link
        print '=' * 10