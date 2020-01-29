import os
import requests

from flask import Flask, render_template, request, redirect, url_for, jsonify
from runner import nike, strava

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/authorize', methods=['POST', 'GET'])
def authorize():

	global STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, NIKE_BEARER_TOKEN
	STRAVA_CLIENT_ID = request.form.get('client_id')
	STRAVA_CLIENT_SECRET = request.form.get('client_secret')
	NIKE_BEARER_TOKEN = request.form.get('bearer_token')

	query = {
	'client_id': STRAVA_CLIENT_ID,
	'redirect_uri': 'http://localhost:5000/select',
	'response_type': 'code',
	'approval_prompt': 'auto',
	'scope': 'read,activity:write',
	}

	req = requests.Request('GET', 'https://www.strava.com/oauth/authorize', params=query)
	url = req.prepare().url
	return render_template('authorize.html', authorize_url=url)

@app.route('/select')
def select():

	global STRAVA_BEARER_TOKEN

	exchange_token = request.args.get('code')
	strava_client = strava(STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET)
	err = strava_client.get_token(exchange_token)
	if(err['code']!='Success'):
		return render_template('error.html', error=err['message'])

	#ideally you would store this and the refresh token in a database.
	STRAVA_BEARER_TOKEN = err['bearer_token']
	athlete_name = err['athlete_name']

	nike_client = nike(NIKE_BEARER_TOKEN)
	err = nike_client.pull_activities()
	if(err['code'] != 'Success'):
		return render_template('error.html', error=err['message'])
	
	err = nike_client.json2gpx()
	if(err['code'] != 'Success'):
		return render_template('error.html', error=err['message'])
	files = os.listdir('./activities_gpx')
	return render_template('select.html',files = files, athlete = athlete_name, n_activities=len(os.listdir('./activities_gpx')))

@app.route('/upload', methods=['POST', 'GET'])
def upload():

	# get selected activities and upload
	select_all = request.form.get('select-all') 
	if(select_all == 'on'):
		files = os.listdir('./activities_gpx')
	else:
		files = list(request.form.keys())

	strava_client = strava(STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET)
	err = strava_client.push_activities(files, STRAVA_BEARER_TOKEN)

	if(err['code'] != 'Success'):
		return render_template('error.html', error = err['message'])
	else:
		return render_template('success.html', message = err['message'], missing_files = err['not_uploaded'])

if __name__ == '__main__':
	app.run(debug=True)