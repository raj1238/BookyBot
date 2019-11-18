import json

#with open('AMD-JAI-flight-results.txt') as fp:
#	data = json.load(fp)

#print(len(data))

def flight_data(sorted_list):
	
	flight = []
	para = ['airline','ticket price','flight duration']
	for i in range(len(sorted_list)-1):
		flight.append([])
		for j in range(len(para)):
			flight[i].append(sorted_list[i][para[j]])
		stops = (len(sorted_list[i]['timings']) - 1)
		airport_stops = ''
		if(stops>0):
			for k in range(stops):
				airport_stops = airport_stops + sorted_list[i]['timings'][k]['arrival_airport'] + ' ' +'And' + ' '

			flight[i].append(airport_stops[:-4])
			flight[i].append(sorted_list[i]['timings'][0]['departure_time'])
			flight[i].append(sorted_list[i]['timings'][stops]['arrival_time'])
		else:
			flight[i].append(sorted_list[i]['stops'])
			flight[i].append(sorted_list[i]['timings'][0]['departure_time'])
			flight[i].append(sorted_list[i]['timings'][stops]['arrival_time'])

	return flight


'''
for i in range(len(flight)):
	print('')
	print(i)
	print(flight[i])
	print('')

'''
#print(data[1]['arrival'])