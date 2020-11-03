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
	if df['results'].dtypes == 'int64':
		for row in df['results']:
			if row == 1:
				results.append('Loved it!')
			else:
				results.append('Hated it!')
		df['results'] = results
		return df
	return df


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

environment = os.getenv('FLASK_ENV', 'production')

api_is_up = os.getenv('API_IS_UP', 'True')


def generate_table(dataframe, max_rows=6):
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
		# Change 'results' column to something human-readable
		if row == 1:
			results.append('Loved it!')
		else:
			results.append('Hated it!')
	df['results'] = results
	# Sort by most recent reviews
	df.sort_values(by=['timestamp'], inplace=True, ascending=False)
	return df

def serve_layout(env=None):
	env = environment

	df = get_sentiment_data(env=env)

	# A second DataFrame where all the movies were loved
	filt = df['results'] == 'Loved it!'
	df_loved = df[filt]

	# A column for df_loved with binned ages
	bins = [12, 25, 35, 60, 100]
	group_names = ["Teenager", "Young-adult", "Middle-aged", "Senior"]
	age_binned = pd.cut(df_loved['age'], bins, labels=group_names)
	df_loved['age_binned'] = age_binned

	fig1 = px.bar(df, x="movie_title", color="results", barmode="group")
	fig2 = px.bar(df_loved, x="movie_title", color="gender", barmode="group")
	fig3 = px.bar(df_loved, x="movie_title", color="country", barmode="group")
	fig4 = px.bar(df_loved, x="movie_title", color="age_binned", barmode="group")

	return html.Div(children=[
		html.H4(children='Movie Review and Demographic Data'),
		generate_table(df),
		html.Br(),
		html.Br(),
		html.H4(children='Loved it! vs. Hated it!'),
		dcc.Graph(
			id='graph-1',
			figure=fig1
		),
		html.Br(),
		html.Br(),
		html.H4(children='Breakdown By Gender for those who Loved it'),
		dcc.Graph(
			id='graph-2',
			figure=fig2
		),
		html.Br(),
		html.Br(),
		html.H4(children='Breakdown By Country for those who Loved it'),
		dcc.Graph(
			id='graph-3',
			figure=fig3
		),
		html.Br(),
		html.Br(),
		html.H4(children='Breakdown By Age for those who Loved it'),
		dcc.Graph(
			id='graph-4',
			figure=fig4
		),
		html.Br(),
		html.Br()
	])


def serve_layout_local():
	df = get_sentiment_data_local(path='movie_and_demographic_data.csv')

	# A second DataFrame where all the movies were loved
	filt = df['results'] == 'Loved it!'
	df_loved = df[filt]

	# A column for df_loved with binned ages
	bins = [12, 25, 35, 60, 100]
	group_names = ["Teenager", "Young-adult", "Middle-aged", "Senior"]
	age_binned = pd.cut(df_loved['age'], bins, labels=group_names)
	df_loved['age_binned'] = age_binned

	fig1 = px.bar(df, x="movie_title", color="results", barmode="group")
	fig2 = px.bar(df_loved, x="movie_title", color="gender", barmode="group")
	fig3 = px.bar(df_loved, x="movie_title", color="country", barmode="group")
	fig4 = px.bar(df_loved, x="movie_title", color="age_binned", barmode="group")

	return html.Div(children=[
		html.H4(children='Movie Review and Demographic Data'),
		generate_table(df),
		html.Br(),
		html.Br(),
		html.H4(children='Loved it! vs. Hated it!'),
		dcc.Graph(
			id='graph-1',
			figure=fig1
		),
		html.Br(),
		html.Br(),
		html.H4(children='Breakdown By Gender for those who Loved it'),
		dcc.Graph(
			id='graph-2',
			figure=fig2
		),
		html.Br(),
		html.Br(),
		html.H4(children='Breakdown By Country for those who Loved it'),
		dcc.Graph(
			id='graph-3',
			figure=fig3
		),
		html.Br(),
		html.Br(),
		html.H4(children='Breakdown By Age for those who Loved it'),
		dcc.Graph(
			id='graph-4',
			figure=fig4
		),
		html.Br(),
		html.Br()
	])



if api_is_up == 'True':
	app.layout = serve_layout
if api_is_up == 'False':
	app.layout = serve_layout_local




if __name__ == '__main__':
	app.run_server(debug=True)





