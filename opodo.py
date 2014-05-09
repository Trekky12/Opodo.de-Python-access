#!/usr/bin/python
# -*- coding: utf-8 -*-
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

        # return (3.14, o.url)
        # raise opodo.NoResultsException(o.url)

        return (o.search(), o.url)
    except opodo.NoResultsException, v:
        return ('None', v.url)


if __name__ == '__main__':
    for d1 in datesiterator(datetime.date(2015, 3, 1),datetime.date(2015, 3, 3)):
        for d2 in datesiterator(datetime.date(2015, 3, 18),datetime.date(2015, 3, 21)):
            for d3 in datesiterator(datetime.date(2015, 3, 27),datetime.date(2015, 3, 31)):    
              (euros, link) = findFly(['FRA', 'AKL', 'BNE'], ['AKL', 'BNE', 'FRA'], [d1, d2, d3])
              print d1, d2, d3
              print euros, 'Euros'
              print link
              print '=' * 10
