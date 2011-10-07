import urllib
import urllib2


class NoResultsException(Exception):
    def __init__(self, url):
        self.url = url


class Opodo(object):
    def __init__(self, departureAirportCode, arrivalAirportCode, departureDate):
        self.params = {'tripType': 'O', 'departureAirportCode': 'BLQ',
                       'departureDay': '04', 'departureMonth': '201103',
                       'departureTime': 'ANY', 'arrivalAirportCode': 'DUB',
                       'directFlight': 'false', 'flexible': 'false',
                       'numberOfAdults': '1', 'numberOfChildren': '0',
                       'numberOfInfants': '0', 'cabinType': 'E',
                       'searchLowCost': 'true', 'includeRailAndFly': 'false'}
        self.params['departureAirportCode'] = departureAirportCode
        self.params['arrivalAirportCode'] = arrivalAirportCode
        self.params['departureDay'] = '%02d' % departureDate.day
        self.params['departureMonth'] = '%04d%02d' % (departureDate.year, departureDate.month)
        self.url = 'http://www.opodo.it/opodo/flights/search?' +  urllib.urlencode(self.params)
        self.url2 = 'http://www.opodo.it/opodo/flights/getPageV2'

    def getCookieContent(self):
        res = urllib2.urlopen(self.url)
        if res.read().find('Non ci sono risultati') != -1:
            raise NoResultsException(self.url)
        return res.info().get('set-cookie')

    def getHtml(self, cookie):
        req = urllib2.Request(self.url2)
        req.add_header('Cookie', cookie)
        r = urllib2.urlopen(req)
        return r.read()

    def search(self):
        cookie = self.getCookieContent()
        self.html = self.getHtml(cookie)
        return self.getPrice()

    def getPrice(self):
        i = self.html.find('"price"') + len('"price">')
        j = self.html.find('&', i)
        return float(self.html[i:j].replace(',', '.'))


if __name__ == '__main__':
    import datetime
    opodo = Opodo('FRL', 'LON', datetime.date(2011, 3, 5))
    print opodo.search()