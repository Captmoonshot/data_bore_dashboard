"""The following Dash App will automatically detect if running in local
development mode and will use the local version of the Django REST API (called Data-Bore) running
in the background.  If for testing or other reasons, you wish to run without the local version of
Django REST API (Data-Bore), simply set the environment variable API_IS_UP=False.  This will
use the movie_and_demographic_data.csv for its pandas DataFrame.  And will allow the user to run 
the Dash up in a stand-alone fashion."""

import os

from dotenv import load_dotenv

import requests
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

import pandas as pd

load_dotenv()

# df = pd.read_csv('movie_and_demographic_data.csv')
# response = requests.get("http://127.0.0.1:8000/api/sentiment/")

# def get_data(source):
# 	"""this function to fetch API data is appropriate when
# 	there's no authentication required at the endpoint."""
# 	results = []

# 	response = requests.get(source)
# 	sentiments = json.loads(response.text)
# 	df = pd.DataFrame(sentiments)
# 	df = df.set_index(['id'])
# 	for row in df['results']:
# 		if row == 1:
# 			results.append('Loved it!')
# 		else:
# 			results.append('Hated it!')
# 	df['results'] = results
# 	return df

def get_sentiment_data_local(path):
	"""this function is only used when the API is not working
	for whatever reason both locally and production-wise.  Based
	on an environment variable API_IS_UP=True. This is really for testing purposes."""
	results = []
	df = pd.read_csv(path)
	for row in df['results']:
		if row == 1:
			results.append('Loved it!')
		else:
			results.append('Hated it!')
	df['results'] = results
	return df





external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

environment = os.getenv('FLASK_ENV', 'production')


def generate_table(dataframe, max_rows=10):
	return html.Table([
		html.Thead(
			html.Tr([html.Th(col) for col in dataframe.columns])
		),
		html.Tbody([
			html.Tr([
				html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
			]) for i in range(min(len(dataframe), max_rows))
		])
	])

def get_sentiment_data(env=None):
	
	if env == "development":
		URL = 'http://127.0.0.1:8000/api-auth/login/'
	else:
		URL = 'https://data-bore.herokuapp.com/api-auth/login/'

	client = requests.session()
	client.get(URL)
	if 'csrftoken' in client.cookies:
		csrftoken = client.cookies['csrftoken']
	else:
		csrftoken = client.cookies['csrf']

	login_data = dict(
		username=os.getenv('USERNAME', 'you-will-never-know'),
		password=os.getenv('PASSWORD', 'you-will-never-know'),
		csrfmiddlewaretoken=csrftoken,
		next='/api/sentiment/'
	)
	r = client.post(URL, data=login_data, headers=dict(Referer=URL))

	results = []

	sentiments = json.loads(r.text)
	df = pd.DataFrame(sentiments)
	df = df.set_index(['id'])
	for row in df['results']:
		if row == 1:
			results.append('Loved it!')
		else:
			results.append('Hated it!')
	df['results'] = results
	return df

def serve_layout(env=None):
	env = environment

	df = get_sentiment_data(env=env)

	return html.Div(children=[
		html.H4(children='Movie Review and Demographic Data'),
		generate_table(df),
		html.Br(),
		html.Br()
	])

def serve_layout_local():
	df = get_sentiment_data_local(path='movie_and_demographic_data.csv')

	return html.Div(children=[
		html.H4(children='Movie Review and Demographic Data'),
		generate_table(df),
		html.Br(),
		html.Br()
	])


api_is_up = os.getenv('API_IS_UP', True)

if api_is_up == True:
	app.layout = serve_layout
elif api_is_up == False:
	app.layout = serve_layout_local





if __name__ == '__main__':
	app.run_server(debug=True)


