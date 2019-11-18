import json
import requests
from lxml import html
from collections import OrderedDict
import argparse

def parse_my(source,destination,date):
	for i in range(20):
		try:
			url = "https://www.expedia.co.in/Flights-Search?trip=oneway&leg1=from:{0},to:{1},departure:{2}TANYT&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass%3Aeconomy&mode=search&origref=www.expedia.com".format(source,destination,date)
			print(url)
			headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
			#print(url)
			response = requests.get(url, headers=headers, verify=False)
			parser = html.fromstring(response.content)
			#print(response.content)
			json_data_xpath = parser.xpath("//script[@id='cachedResultsJson']//text()")
			raw_json =json.loads(json_data_xpath[0] if json_data_xpath else '')
			flight_data = json.loads(raw_json["content"])
			flight_info  = OrderedDict() 
			lists=[]

			for i in flight_data['legs'].keys():
				total_distance =  flight_data['legs'][i].get("formattedDistance",'')
				exact_price = float(flight_data['legs'][i].get('price',{}).get('totalPriceAsDecimal',''))
				departure_location_airport = flight_data['legs'][i].get('departureLocation',{}).get('airportLongName','')
				departure_location_city = flight_data['legs'][i].get('departureLocation',{}).get('airportCity','')
				departure_location_airport_code = flight_data['legs'][i].get('departureLocation',{}).get('airportCode','')
				
				arrival_location_airport = flight_data['legs'][i].get('arrivalLocation',{}).get('airportLongName','')
				arrival_location_airport_code = flight_data['legs'][i].get('arrivalLocation',{}).get('airportCode','')
				arrival_location_city = flight_data['legs'][i].get('arrivalLocation',{}).get('airportCity','')
				airline_name = flight_data['legs'][i].get('carrierSummary',{}).get('airlineName','')
				
				no_of_stops = flight_data['legs'][i].get("stops","")
				flight_duration = flight_data['legs'][i].get('duration',{})
				flight_hour = flight_duration.get('hours','')
				flight_minutes = flight_duration.get('minutes','')
				flight_days = flight_duration.get('numOfDays','')

				if no_of_stops==0:
					stop = "Nonstop"
				else:
					stop = str(no_of_stops)+' Stop'

				#total_flight_duration = "{0} days {1} hours {2} minutes".format(flight_days,flight_hour,flight_minutes)
				total_flight_duration = "{0} hours {1} minutes".format(flight_hour,flight_minutes)
				departure = departure_location_airport+", "+departure_location_city
				arrival = arrival_location_city #arrival_location_airport+", "+
				carrier = flight_data['legs'][i].get('timeline',[])[0].get('carrier',{})
				plane = carrier.get('plane','')
				plane_code = carrier.get('planeCode','')
				formatted_price = exact_price #"{0:.2f}".format(exact_price)

				if not airline_name:
					airline_name = carrier.get('operatedBy','')
				
				timings = []
				for timeline in  flight_data['legs'][i].get('timeline',{}):
					if 'departureAirport' in timeline.keys():
						departure_airport = timeline['departureAirport'].get('longName','')
						departure_time = timeline['departureTime'].get('time','')
						arrival_airport = timeline.get('arrivalAirport',{}).get('longName','')
						arrival_time = timeline.get('arrivalTime',{}).get('time','')
						flight_timing = {
											'departure_airport':departure_airport,
											'departure_time':departure_time,
											'arrival_airport':arrival_airport,
											'arrival_time':arrival_time
						}
						timings.append(flight_timing)

				flight_info={'stops':stop,
					'ticket price':formatted_price,
					#'departure':departure,
					#'arrival':arrival,
					'flight duration':total_flight_duration,
					'airline':airline_name,
					'plane':plane,
					'timings':timings
					#'plane code':plane_code
				}
				error = {
					'error':'none'
				}
				lists.append(flight_info)
			sortedlist = sorted(lists, key=lambda k:int(k['ticket price']),reverse=False)
			#sortedlist=lists
			sortedlist.append(error)
			print ("Writing data to output file")
			#with open('%s-%s-flight-results.txt'%(source,destination),'w') as fp:
			#	json.dump(sortedlist,fp,indent = 4)
			return sortedlist

		except ValueError:
			print ("Retrying...")
		sortedlist=[]
		sortedlist.append({"error":"failed to process the page"})
		#with open('%s-%s-flight-results.txt'%(source,destination),'w') as fp:
		#	json.dump(sortedlist,fp,indent = 4)
		return sortedlist

#if __name__=="__main__":
	'''argparser = argparse.ArgumentParser()
		argparser.add_argument('source',help = 'Source airport code')
		argp'arser.add_argument('destination',help = 'Destination airport code')
	argparser.add_argument('date',help = 'DD/MM/YYYY')

	args = argparser.parse_args()
	source = args.source
	destination = args.destination
	date = args.date
	print ("Fetching flight details")'''
	#scraped_data = parse(source,destination,date)
#	parse('AMD','MAA','11/11/2019')
	'''print ("Writing data to output file")
	with open('%s-%s-flight-results.txt'%(source,destination),'w') as fp:
		json.dump(scraped_data,fp,indent = 4)'''
