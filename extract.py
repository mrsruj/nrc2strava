import json 
import logging
from datetime import datetime

def extract(filename):
	"""
	Extract data from json.

	:param time: filepath to json 
	:type time: str

	:return: (time, name, [timestamps], [latitude], [longitude])
	:rtype: tuple
	"""
	with open(filename, 'r') as f:
		data = json.load(f)

	if(data['type']=='run'):
		timestamps, lat, lon = [], [], []
		try:
			time = datetime.utcfromtimestamp(data['start_epoch_ms']/1000).replace(microsecond=0).isoformat()+'Z'
			name = data['tags']['com.nike.name'] or "test"
# 			name = data['tags']['com.nike.name'] or datetime.utcfromtimestamp(data['start_epoch_ms']/1000).strftime("%A %d/%m/%Y")
# 			temp = data['tags']['com.nike.temperature'] or data['tags']['emetemperature']
# 			for summary in data['summaries']:
# 				if(summary['type']=='heart_rate'):
# 					heartrate = metric['value']
# 				elif(metric['type']=='distance'):
# 					distance = metric['value']
			for metric in data['metrics']:
				if(metric['type']=='latitude'):
					lat_values = metric['values']
				elif(metric['type']=='longitude'):
					lon_values = metric['values']
				
			for lat1, lon1 in zip(lat_values, lon_values):
				timestamps.append(datetime.utcfromtimestamp(lat1['start_epoch_ms']/1000).replace(microsecond=0).isoformat()+'Z')
				lat.append(lat1['value'])
				lon.append(lon1['value'])
# 			return time, name, temp, heartrate, distance, timestamps, lat, lon;
			return time, name, timestamps, lat, lon;
		except ExtractError as e:
			logging.exception("message")
			return None
