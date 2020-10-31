import os

from dotenv import load_dotenv

import requests
import json

import dash
import dash_core_components as dcc
import dash_html_components as html

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


def generate_table(dataframe, max_rows=7):
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


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

environment = os.getenv('FLASK_ENV', 'production')

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

app.layout = serve_layout





if __name__ == '__main__':
	app.run_server(debug=True)


