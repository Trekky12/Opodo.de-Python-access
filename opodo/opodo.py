#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
from bs4 import BeautifulSoup
import re
import time


class NoResultsException(Exception):

    def __init__(self, url):
        self.url = url


class SearchResult():
    
    def __init__(self):
        self.locations = []
        self.stops = []
        self.locations = []
        self.durations = []
        self.price = ""
        self.resultNr = -1

    def addStop(self, stop, location, duration):
        self.stops.append(stop)
        self.locations.append(location)
        self.durations.append(duration)
    
    def setPrice(self, price):
        self.price = price
        
    def setStay(self, searchresult): 
        self.stops = searchresult.stops
        self.locations = searchresult.locations
        self.durations = searchresult.durations
        self.resultNr = searchresult.resultNr
    
        
    def __str__(self):
        return str(self.price)+"|"+str(self.stops)+"|"+str(self.locations)+"|"+str(self.durations)
        
    def __repr__(self):
        return repr((self.price, self.stops, self.durations))

class Opodo(object):

    def __init__(
        self,
        departureAirportCodes,
        arrivalAirportCodes,
        departureDates,
        maxPrice = None,
        maxStay = None
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
                
            self.multi = True
            self.arrivalAirportCodes = arrivalAirportCodes
            self.departureAirportCodes = departureAirportCodes
            self.departureDates = departureDates
            
        elif isinstance(departureAirportCodes, str):
            self.params = {
                'tripType': 'O',
                'departureTime': 'ANY',
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
            self.multi = False
            self.arrivalAirportCodes = [arrivalAirportCodes]
            self.departureAirportCodes = [departureAirportCodes]
            self.departureDates = [departureDates]
        else:
            raise Exception('Parameter wrong')
        
        self.url2 = 'http://www.opodo.de/opodo/flights/getPageV2'
        self.maxPrice = maxPrice
        self.maxStay = maxStay
        

    def getCookieContent(self):
        res = urllib2.urlopen(self.url)
        if res.read().find('Non ci sono risultati') != -1:
            raise NoResultsException(self.url)
        return res.info().get('set-cookie')

    def getHtml(self, url):
        req = urllib2.Request(url)
        req.add_header('Cookie', self.cookie)
        r = urllib2.urlopen(req)
        return r.read().decode("UTF-8")

    def search(self):
        self.cookie = self.getCookieContent()
        self.html = self.getHtml(self.url2)
        resultlist = self.getPriceAndStops()
        table = self.getTable(resultlist)
        return  resultlist, table
           

    def getPriceAndStops(self):
        soup = BeautifulSoup(self.html)
        resultlist = []
        
        maxstay = time.strptime(self.maxStay, '%H:%M') if self.maxStay != None else None
        
        # Iterate over all results
        for htmlDiv in soup.find_all(id=re.compile('outer-[0-9]*', re.I)):
        
            result = SearchResult()   
            price = htmlDiv.find('span',{'class':'price'}).text.encode('utf-8').strip()
            price = float(re.sub(r'[^\w|\.]', '', price.replace('.', '').replace(',','.')))
            
            # Filter Max Price
            if self.maxPrice != None and price >= self.maxPrice:
                break;                                
            result.setPrice(price)
            
            staydurationResult = self.getStayDurations(htmlDiv, maxstay)
            
            # Filter StayDuration
            if staydurationResult:
                result.setStay(staydurationResult)
                resultlist.append(result)
                
        return resultlist
	
  
    def getStayDurations(self, htmlDiv, maxStayduration):
        result = SearchResult()
        # Get the different Flights (Multi)
        for flight in range(0, len(self.departureAirportCodes)):
            result_id = htmlDiv.get('id').split('-')[1]
            result.resultNr = result_id
            
            if self.multi:
                # Get only the first result of the flight (the others are only different fly times but the same price and similar stay duration)
                duration_table_cell = htmlDiv.find('div',{'id':'inner-%s%s' %(result_id,flight)}).find(id='LOrecommendations%s' %(flight)).find('td',{'class':'cell cell03'})
            else:
                duration_table_cell = htmlDiv.find('div',{'id':'inner-%s' %(result_id)}).find('td',{'class':'cell cell03'})
                
            # Get stay location and duration 
            if duration_table_cell.div.text.strip() != 'Direkt':
                params = re.search('populatePopupDetails\(\'([\w.]*)\',([\d]),\'([\w_]*)\'',  duration_table_cell.div.a.get('onmouseover')).groups()
                durations, locations = self.getStops(params)
                for duration in durations:
                    if maxStayduration != None and duration >= maxStayduration:
                        return None
                result.addStop(duration_table_cell.div.text.strip(), locations, [time.strftime('%H:%M', duration) for duration in durations])
            else:
                result.addStop(duration_table_cell.div.text.strip(), '' , 0)
        
        return result
            
            
    def getStops(self, params):
        url = 'http://www.opodo.de/opodo/flights/getRolloverDetails?group=%s&bound=%s&leg=%s' %(params[0], params[1],params[2])
        rolloverHtml = self.getHtml(url)
        soup = BeautifulSoup(rolloverHtml)
        sd_line = soup.find_all('div',{'class':'sd_boxst'})
        durations = []
        locations = []
        for stops in sd_line:
            # get stay duration
            duration = re.findall('[0-9]{2}:[0-9]{2}', stops.div.text)
            duration_time = time.strptime(duration[0], '%H:%M')
            durations.append(duration_time)
            # get stay location
            sdline_ai = stops.find('div', {'class':'ai'}).text.strip()
            location = re.findall('^[A-z ]+', sdline_ai)[0].strip()
            locations.append(location)
        
        return durations, locations
        
    def getTable(self, resultlist):
        table = ''
        if len(resultlist) > 0:
            table += '<div class="panel panel-default">'
            table +='<table class="table">'
            table += '<thead>'
            table +=  '<tr>'
            table +=  '<th><span class="glyphicon glyphicon-plane"></span></th>'
            for idx, depairport in enumerate(self.departureAirportCodes):
                table +=  '<th>%s <span class="glyphicon glyphicon-arrow-right"></span> %s</th>' %(depairport,self.arrivalAirportCodes[idx])
            table +=  '</tr>'
            
            table +=  '<tr>'
            table +=  '<th>Datum</th>'
            for date in self.departureDates:
                table +=  '<th>%s</th>' %(date)
            table +=  '</tr>'
            table += '</thead><tbody>'
            
            
            for result in resultlist:
                
                table +=  '<tr class="active">'
                table +=  '<td colspan="%s"><b>%s Euro <a href="%s#outer-%s" target="_blank" style="margin-left:2em">Gehe zum Angebot</a></b></td>' % (len(result.stops)+1, result.price, self.url, result.resultNr)
                table +=  '</tr>'
                
                table +=  '<tr>'
                table +=  '<td>Stops</td>'
                for stop in result.stops:
                    table +=  '<td>%s</td>' %(stop.encode('utf-8'))
                table +=  '</tr>'
                
                table +=  '<tr>'
                table +=  '<td>Dauer</td>'
                for duration in result.durations:
                    table +=  '<td>%s</td>' %(', '.join(duration) if duration != 0 else '')
                table +=  '</tr>'
                
                table +=  '<tr>'
                table +=  '<td>Ort</td>'
                for location in result.locations:
                    table +=  '<td>%s</td>' %(', '.join(location) if location != '' else '')
                table +=  '</tr>'
                            
            table +=  '</tbody></table>'
            table += '</div>'
        
        return table        



if __name__ == '__main__':
    import datetime
    opodo = Opodo(['FRA', 'AKL', 'BNE'], ['AKL', 'BNE', 'FRA'], [datetime.date(2015, 3, 3),datetime.date(2015, 3, 23), datetime.date(2015, 3, 28),], maxPrice=1350, maxStay='06:00')
    #opodo = Opodo('FRA', 'AKL', datetime.date(2015, 3, 1))
    print opodo.url
    resultlist, table = opodo.search()
    #for result in resultlist:
    #    print result
    print table
