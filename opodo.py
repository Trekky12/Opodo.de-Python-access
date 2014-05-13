#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import time

from opodo import opodo


def datesiterator(start, end):
    assert start <= end
    while start <= end:
        yield start
        start += datetime.timedelta(days=1)

def createTable(tables):
    f = open('/var/www/opodo.html', 'r+')
    htmlContent = '{table}'
    htmlContent += '<div class="panel panel-primary">'
    htmlContent += '<div class="panel-heading">%s</div>' % (time.strftime('%d. %b %Y %H:%M:%S'))
    htmlContent += '<div class="panel-body">'
    for table in tables:
        htmlContent += table
    htmlContent += '</div>'
    htmlContent += '</div>'
    htmlFileContent = f.read()
    f.seek(0)
    f.write(htmlFileContent.format(table=htmlContent))
    f.truncate()
    f.close()

def findFly(departureAirportCode, arrivalAirportCode, departureDate, maxPrice, maxStay):
    o = opodo.Opodo(departureAirportCode, arrivalAirportCode, departureDate, maxPrice, maxStay)
    try:
        return o.search()
    except opodo.NoResultsException, v:
        return ('None', v.url)
        

        

if __name__ == '__main__':
    tablelist = []
    for d1 in datesiterator(datetime.date(2015, 3, 1),datetime.date(2015, 3, 3)):
        for d2 in datesiterator(datetime.date(2015, 3, 21),datetime.date(2015, 3, 23)):
            for d3 in datesiterator(datetime.date(2015, 3, 28),datetime.date(2015, 3, 31)):    
              (resultlist, table) = findFly(['FRA', 'AKL', 'BNE'], ['AKL', 'BNE', 'FRA'], [d1, d2, d3], maxPrice=1350, maxStay = '09:00')
              tablelist.append(table)
              print d1, d2, d3
              for result in resultlist:
                  print result.price
              print '=' * 10
    createTable(tablelist)
