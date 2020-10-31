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

def get_data(source):
	results = []

	response = requests.get(source)
	sentiments = json.loads(response.text)
	df = pd.DataFrame(sentiments)
	df = df.set_index(['id'])
	for row in df['results']:
		if row == 1:
			results.append('Loved it!')
		else:
			results.append('Hated it!')
	df['results'] = results
	return df


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

production_api_source = "https://data-bore.herokuapp.com/api/sentiment/"
development_api_source = "http://127.0.0.1:8000/api/sentiment/"

environment = os.getenv('FLASK_ENV', 'production')

def serve_layout(data_source=None, env=None):
	env = environment
	if env == "development":
		data_source = development_api_source
	else:
		data_source = production_api_source

	df = get_data(data_source)

	return html.Div(children=[
		html.H4(children='Movie Review and Demographic Data'),
		generate_table(df),
		html.Br(),
		html.Br()
	])

app.layout = serve_layout


if __name__ == '__main__':
	app.run_server(debug=True)


