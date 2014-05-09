#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
from bs4 import BeautifulSoup


class NoResultsException(Exception):

    def __init__(self, url):
        self.url = url


class Opodo(object):

    def __init__(
        self,
        departureAirportCodes,
        arrivalAirportCodes,
        departureDates,
        ):
        if isinstance(departureAirportCodes, list) and len(departureAirportCodes) <= 4:
            self.params = {
                'collectionMethodValue' : 'Cheapest',
                'reset' : 'true',
                'backButton' : '',
                'tripType' : 'C',
                'numberOfAdults' : '2',
                'numberOfChildren' : '0',
                'numberOfInfants' : '0',
                'preferredAirlinesSelected' : 'NA',
                'cabinType' : '',
                'backButton' : '',
                }
            for idx, dcode in enumerate(departureAirportCodes):
                self.params['departureAirportCodes[%1d]' %(idx)] = dcode
                self.params['departureAirports[%1d]' %(idx)] = ''
                self.params['departureTimes[%1d]' %(idx)] = 'ANY'
            for idx, acode in enumerate(arrivalAirportCodes):
                self.params['arrivalAirportCodes[%1d]' %(idx)] = acode
                self.params['arrivalAirports[%1d]' %(idx)] = ''
            for idx, acode in enumerate(arrivalAirportCodes):
                self.params['arrivalAirportCodes[%1d]' %(idx)] = acode
            for idx, date in enumerate(departureDates):
                self.params['departureDays[%1d]' %(idx) ] = '%02d' % date.day
                self.params['departureMonths[%1d]' %(idx)] = '%04d%02d' % (date.year, date.month)
            
            self.url = 'http://www.opodo.de/opodo/buchen/flug/gabelFlug/ergebnis-ueberblick?' \
                + urllib.urlencode(self.params)
        elif isinstance(departureAirportCodes, str):
            self.params = {
                'tripType': 'O',
                'departureAirportCode': 'BLQ',
                'departureDay': '04',
                'departureMonth': '201103',
                'departureTime': 'ANY',
                'arrivalAirportCode': 'DUB',
                'directFlight': 'false',
                'flexible': 'false',
                'numberOfAdults': '1',
                'numberOfChildren': '0',
                'numberOfInfants': '0',
                'cabinType': 'E',
                'searchLowCost': 'true',
                'includeRailAndFly': 'false',
                }
            self.params['departureAirportCode'] = departureAirportCodes
            self.params['arrivalAirportCode'] = arrivalAirportCodes
            self.params['departureDay'] = '%02d' % departureDates.day
            self.params['departureMonth'] = '%04d%02d' \
                % (departureDates.year, departureDates.month)
            self.url = 'http://www.opodo.de/opodo/flights/search?' \
                + urllib.urlencode(self.params)
        else:
            raise Exception('Parameter wrong')
        self.url2 = 'http://www.opodo.de/opodo/flights/getPageV2'

    def getCookieContent(self):
        res = urllib2.urlopen(self.url)
        if res.read().find('Non ci sono risultati') != -1:
            raise NoResultsException(self.url)
        return res.info().get('set-cookie')

    def getHtml(self, cookie):
        req = urllib2.Request(self.url2)
        req.add_header('Cookie', cookie)
        r = urllib2.urlopen(req)
        return r.read().decode("UTF-8")

    def search(self):
        cookie = self.getCookieContent()
        self.html = self.getHtml(cookie)
        return self.getPrice()

    def getPrice(self):
        soup = BeautifulSoup(self.html)
        return soup.find('span',{'class':'price'}).text.encode('utf-8').strip()


if __name__ == '__main__':
    import datetime
    opodo = Opodo(['FRA', 'AKL', 'BNE'], ['AKL', 'BNE', 'FRA'], [datetime.date(2015, 3, 1),datetime.date(2015, 3, 21), datetime.date(2015, 3, 28),])
    #opodo = Opodo('FRA', 'AKL', datetime.date(2015, 3, 1))
    #print opodo.url
    print str(opodo.search())
