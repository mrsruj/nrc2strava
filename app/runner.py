import os
import glob
from os.path import join
from gpx_builder import gpx_gen
from extract import extract
import requests


def listdir_nohidden(path):
	return [f for f in os.listdir(path) if not f.startswith('.')]


class nike(object):
	
	def __init__(self, nike_bearer_token=None):
		self.bearer_token = nike_bearer_token

	def pull_activities(self):
		"""
		pull data from nike servers
		"""
		if(self.bearer_token == None):
			return {'code':'Error', 'message': 'Missing bearer_token'}

		try:
			os.system(f'bash pull_activities.bash {self.bearer_token}')
		except:
			return {'code':'Error', 'message':'Error in executing pull_activities.bash'}

		if(len(listdir_nohidden('./activities_json')) == 0):
			return {'code':'Error', 'message': 'Unauthorized bearer_token'}
		else:
			return {'code':'Success', 'message': f"{len(listdir_nohidden('./activities_json'))} Nike workouts successfully retrieved."} 

	def json2gpx(self):
		"""
		convert json to gpx
		"""
		files = [join('./activities_json',f) for f in listdir_nohidden('./activities_json')]
		for file in files:
			data = extract(file)
			if(data!=None):
				gpx_gen(data[0],data[1],data[2],data[3],data[4])

		n_files = len(listdir_nohidden('./activities_gpx'))
		if(n_files == 0):    	
			return {'code':'Error', 'message': 'No run activities were found'}    
		return {'code':'Success', 'message': f"{n_files}Nike runs converted to gpx."}

	def cleanup(self):
		"""
		clean up files post upload
		"""
		os.system('rm -rf ./activities_json/* & rm -rf ./activities_gpx/*')



class strava(object):

	def __init__(self, client_id=None, client_secret=None):
		self.client_id = client_id
		self.client_secret = client_secret

	def get_token(self, exchange_token=None):
		
		if(exchange_token == None):
			return {'code':'Error', 'message': 'No exchange_token found'}
		
		query = {
			'client_id': self.client_id,
			'client_secret': self.client_secret,
			'code': exchange_token,
			'grant_type': 'authorization_code',
		}
		
		try:
			response = requests.post('https://www.strava.com/oauth/token', params=query)
		except:
			if(response.status_code != 200):
				return {'code':'Error', 'message': 'strava-authorization error'}
		
		bearer_token = response.json()['access_token']
		athlete_name = response.json()['athlete']['firstname'] + ' ' + response.json()['athlete']['lastname']
		return {'code':'Success', 'athlete_name': athlete_name, 'bearer_token': bearer_token}

	def push_activities(self, files=None, bearer_token=None):
		"""
		push data to strava
		"""
		if(len(files)==0 or files == None ):
			return {'code':'Error', 'message': 'No files selected for upload'}
		
		headers = {
			'Accept': 'application/json',
			'Authorization': f'Bearer {bearer_token}',
		}
		not_uploaded = []

		for fi in files:
			query = {
				'name': fi.split('_')[0].replace('-', ' '),
				'data_type': 'gpx',
			}
			try:
				with open(join('./activities_gpx',fi),'rb') as f:
					file = {'file': f}
					response = requests.post('https://www.strava.com/api/v3/uploads', headers=headers, params=query, files=file)
					if(response.status_code != 201):
						not_uploaded.append(fi)	
			except:
				return {'code':'Error', 'message':response.json()}
		return {'code':'Success', 'message': f'{len(files)-len(not_uploaded)} out of {len(files)} files successfully transfered.', 'not_uploaded':not_uploaded}
