import dash
import base64
import dash_core_components as dcc
import dash_html_components as html

import flask
import glob

import numpy as np 
import imageio
import json
import cv2
import csv
import os
import io


config_directory = 'config_dir/'
external_stylesheets = [config_directory + 'bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

app.title = "Indonesian Agricultural Data"

img_dir = config_directory + 'img_dir/'
yaml_dir = config_directory + 'yaml_dir/'

Provinsi = [os.path.basename(p).split('.png')[0] for p in glob.glob(img_dir + '/*.png')]

Periode = [str(thn) for thn in range(1961,2015)]
static_image_route = '/static/'

file_json = open(config_directory + "json_wilayah/data_wilayah.json", "r")
data_json = json.load(file_json)

csv_files = [os.path.basename(f).split('.json')[0] for f in glob.glob(config_directory + "json_panen/" + '*.json')]
Komoditi = csv_files


json_panen = dict()
folder_json_panen = config_directory + "json_panen/"
for nf3 in os.listdir(folder_json_panen):
	if nf3.split('.')[-1] != 'json':
		continue
	f3 = open(folder_json_panen + nf3, "r")
	jd3 = json.load(f3)
	f3.close()

	km3 = nf3.split("/")[-1].split('.')[0]
	json_panen[km3] = jd3

nama_kota = list()
for k in data_json.keys():
	for kota in data_json[k].values():
		if kota not in nama_kota:
			nama_kota.append(kota)

dictKomThn = dict()
for kom in json_panen.keys():
	dictKomThn[kom] = dict()
	for k in json_panen[kom].keys():
		for thn in json_panen[kom][k].keys():
			dictKomThn[kom][thn] = list()

for km_ in dictKomThn.keys():
	for th_ in dictKomThn[km_].keys():
		data_temp = 0.0
		for k in json_panen[km_].keys():
			if th_ not in json_panen[km_][k].keys():
				json_panen[km_][k][th_] = 0.0
			data_temp = data_temp + float(json_panen[km_][k][th_])
		mean_ = data_temp / float(len(list(json_panen[km_].keys())))
		for i in range(3):
			dictKomThn[km_][th_].append(mean_ * (i+1)/2.0)
'''
	dictKomThn
	{'komoditas':{'tahun': [q1, mean, q3]}}
'''

colorMap = [(0,255,255), (255,255,0), (0,255,0), (255,0,0), (0,0,0)]

colors = {
	'background': '#111111',
	'text': '#7FDBFF'
}

''' Forecasting
	1. Actual Value
	2. Linear Regression
	3. Quadratic Regression
'''

dir_forecast_data = config_directory + 'forecasting/data/'
dir_rmse_forecasting = config_directory + 'forecasting/RMSE/'

method_forecast = [d_ for d_ in os.listdir(dir_forecast_data) if os.path.isdir(dir_forecast_data + d_)]
print(method_forecast)
dict_forecast = dict()

for mf in method_forecast:
	dict_forecast[mf] = dict()

for mtd in method_forecast:
	dir_mfc = dir_forecast_data + mtd + '/'
	json_files = [f for f in os.listdir(dir_mfc) if f.split('.')[-1] == 'json']
	for json_file in json_files:
		json_open = open(dir_mfc + json_file, 'r')
		json_load = json.load(json_open)
		json_open.close()

		komoditas_forecast = json_file.split('/')[-1].split('.')[0]
		dict_forecast[mtd][komoditas_forecast] = json_load
'''
dict_forecast = { "Linear Regression":
	{
		"Tomato":{........ data dalam json Tomato.json}, ......
	}, "Quadratic Regression":
	{
		"Tomato":{........ data dalam json Tomato.json}, ......
	}
}
'''


def calc_center_contour(contur):
	moment_ = cv2.moments(contur)
	cx_ = int(moment_["m10"] / moment_["m00"])
	cy_ = int(moment_["m01"] / moment_["m00"])
	return (cx_, cy_)


app.layout = html.Div([
	dcc.Tabs(id="tabData", value='tabMAP', children=[
		dcc.Tab(label='MAP', value='tabMAP'),
		dcc.Tab(label='CHART', value='tabCHART'),
		dcc.Tab(label='FORECASTING', value='tabFORECAST')
	], style={"margin-top": 0, "width": "40%", "height":"1vh", "margin-left":640, "display": "block"}),
	html.Div(id='tabOutData')
])


tabCHART = html.Div([
	html.H1(children='Indonesian Agricultural Data', style={"margin-top":0}),
	html.Div([
		html.Div([
			dcc.Dropdown(
				id='Kota',
				options=[{'label': i, 'value': i} for i in nama_kota],
				value=nama_kota[0]
			)
		],
		style={'width': '15%', 'float': 'right', 'margin-top':10, 'margin-right':900}), #, 'display': 'inline-block'

		html.Div([
			dcc.Dropdown(
				id='KomKota',
				options=[{'label': i, 'value': i} for i in Komoditi],
				value=Komoditi[0]
			)
		],
		style={'width': '15%', 'float': 'right', 'margin-top':10, 'margin-left':-100}) # , 'display': 'inline-block'
	]),
	html.Div(id='tampil_kom_kota', style={'margin-top':20, 'fontSize': 30, 'color': 'blue', 'margin-left':500}),
	dcc.Graph(id='all_in_city', style={'width':'100%', 'height': '150%', 'float': 'right', 'margin-top':15})
])

tabFORECAST = html.Div([
	html.H1(children='Indonesian Agricultural Data', style={"margin-top":0}),
	html.Div([
		html.Div([
			dcc.Dropdown(
				id='forecast_kota',
				options=[{'label': i, 'value': i} for i in nama_kota],
				value=nama_kota[0]
			)
		],
		style={'width': '15%', 'float': 'right', 'margin-top':10, 'margin-right':900}), #, 'display': 'inline-block'

		html.Div([
			dcc.Dropdown(
				id='forecast_kom_kota',
				options=[{'label': i, 'value': i} for i in Komoditi],
				value=Komoditi[0]
			)
		],
		style={'width': '15%', 'float': 'right', 'margin-top':10, 'margin-left':-100}) # , 'display': 'inline-block'
	]),
	html.Div(id='forecast_tampil_kom_kota', style={'margin-top':20, 'fontSize': 30, 'color': 'blue', 'margin-left':500}),
	dcc.Graph(id='scatter_value', style={'width':'100%', 'height': '150%', 'float': 'right', 'margin-top':15})
])

@app.callback(
	dash.dependencies.Output('scatter_value', 'figure'),
	[dash.dependencies.Input('forecast_kom_kota', 'value'),
	 dash.dependencies.Input('forecast_kota', 'value')])
def update_figure_kota(kom_, kot_):
	dict_kunci = dict()
	nothing = False
	for mtd_ in method_forecast:
		list_kota = [kt for kt in dict_forecast[mtd_][kom_].keys()]
		if kot_ not in list_kota:
			dict_forecast[mtd_][kom_][kot_] = dict_forecast[mtd_][kom_][list_kota[0]]
			nothing = True
		dict_kunci[mtd_] = np.array([ky for ky in list(dict_forecast[mtd_][kom_][kot_].keys())])
		dict_kunci[mtd_] = np.sort(dict_kunci[mtd_])
		dict_kunci[mtd_] = list(dict_kunci[mtd_])
		if nothing:
			for kx in dict_forecast[mtd_][kom_][kot_].keys():
				dict_forecast[mtd_][kom_][kot_][kx] = '0.0'
			nothing = False

	data_fig = {
		'data': [{'x': [int(t) for t in dict_kunci[mtd_]], 'y': [float(dict_forecast[mtd_][kom_][kot_][str(kc)]) for kc in dict_kunci[mtd_]], 'type': 'markers', 'name': mtd_} for mtd_ in method_forecast]
	}
	return data_fig

@app.callback(
	dash.dependencies.Output('forecast_tampil_kom_kota', 'children'),
	[dash.dependencies.Input('forecast_kom_kota', 'value'),
	dash.dependencies.Input('forecast_kota', 'value')])
def update_slider(str_komoditas, str_kota):
	return str_komoditas + " yields at " + str_kota


@app.callback(
	dash.dependencies.Output('tampil_kom_kota', 'children'),
	[dash.dependencies.Input('KomKota', 'value'),
	dash.dependencies.Input('Kota', 'value')])
def update_slider(str_komoditas, str_kota):
	return str_komoditas + " yields at " + str_kota

@app.callback(
	dash.dependencies.Output('all_in_city', 'figure'),
	[dash.dependencies.Input('KomKota', 'value'),
	 dash.dependencies.Input('Kota', 'value')])
def update_figure_kota(kom_, kot_):
	tahun_ = np.array([int(k) for k in list(json_panen[kom_][kot_].keys())])
	tahun_ = np.sort(tahun_)
	tahun_ = list(tahun_)
	data_fig = {
		'data': [{'x': [int(k)], 'y': [float(json_panen[kom_][kot_][k])], 'type': 'bar', 'name': k} for k in list(json_panen[kom_][kot_].keys())]
	}
	return data_fig

potong_tahun = {}
for i in range(len(Periode)):
	if Periode[i][0] == '2':
		potong_tahun[3*(i+1)] = Periode[i].split('20')[-1]
	else:
		potong_tahun[3*(i+1)] = Periode[i].split('19')[-1]

tabMAP = html.Div([
	html.H1(children='Indonesian Agricultural Data', style={"margin-top":0}),
	html.Div([
		html.Div([
			dcc.Dropdown(
				id='Provinsi',
				options=[{'label': i, 'value': i} for i in Provinsi],
				value=Provinsi[0]
			)
		],
		style={'width': '15%', 'float': 'right', 'margin-top':10, 'margin-right':680}), #, 'display': 'inline-block'

		html.Div([
			dcc.Dropdown(
				id='Komoditas',
				options=[{'label': i, 'value': i} for i in Komoditi],
				value=Komoditi[0]
			)
		],
		style={'width': '15%', 'float': 'right', 'margin-top':10, 'margin-left':-100}) # , 'display': 'inline-block'
	]),
	html.Img(id='image', style={'margin-top':20}),

	dcc.Graph(id='rank-wilayah', style={'width':'50%', 'height': '150%', 'float': 'right', 'margin-top':15}),

	dcc.Slider(
		id='year--slider',
		min=0,
		max=3*len(Periode) ,
		step=None,
		marks=potong_tahun,
		value=6
	),
	html.Div(id='slider_to_year', style={'margin-top':-510, 'fontSize': 25, 'color': 'blue'})
])

@app.callback(
	dash.dependencies.Output('slider_to_year', 'children'),
	[dash.dependencies.Input('year--slider', 'value'),
	dash.dependencies.Input('Komoditas', 'value')])
def update_slider(value, str_komoditas):
	tahun = Periode[int(int(value)/3) -1]
	return str_komoditas + " yields, " + tahun

@app.callback(
	dash.dependencies.Output('rank-wilayah', 'figure'),
	[dash.dependencies.Input('Provinsi', 'value'),
	dash.dependencies.Input('Komoditas', 'value'),
	dash.dependencies.Input('year--slider', 'value')])
def update_rank_bar(prov, komo, valyear):
	n_str_wilayah = data_json[prov]
	tahun = Periode[int(int(valyear)/3) -1]
	for i in range(len(n_str_wilayah)):
		if tahun not in json_panen[komo][n_str_wilayah[str(i+1)]].keys():
			json_panen[komo][n_str_wilayah[str(i+1)]][tahun] = 0.0
	data_figure = {
			'data': [{'x': [i+1], 'y': [float(json_panen[komo][n_str_wilayah[str(i+1)]][tahun])], 'type':'bar', 'name':n_str_wilayah[str(i+1)]} for i in range(len(n_str_wilayah))],
			'layout': {
				'title': komo + " yields, " + tahun,
				'plot_bgcolor': colors['background'],
				'paper_bgcolor': colors['background'],
				'font': {
					'color': colors['text']
				}
			}
		}
	return data_figure


@app.callback(
	dash.dependencies.Output('image', 'src'),
	[dash.dependencies.Input('Provinsi', 'value'),
	 dash.dependencies.Input('Komoditas', 'value'),
	 dash.dependencies.Input('year--slider', 'value')])
def update_image_src(prov_im, kom_im, slider_im):
	n_str_wilayah = data_json[prov_im]
	tahun = Periode[int(int(slider_im)/3) -1]

	name_file_img = img_dir + prov_im
	namaProvinsi = name_file_img.split("/")[-1]
	test_base64 = base64.b64encode(open(name_file_img + '.png', 'rb').read()).decode('ascii')
	img_ = imageio.imread(io.BytesIO(base64.b64decode(test_base64)))
	img_ = cv2.cvtColor(img_, cv2.COLOR_RGB2BGR)

	name_file_yaml = yaml_dir + prov_im
	yaml_node = cv2.FileStorage(name_file_yaml + ".yaml", cv2.FILE_STORAGE_READ)
	nwilayah = int(yaml_node.getNode("nwilayah").real())

	h,w,c = img_.shape
	m2 = 255*np.ones((h,40,3), np.uint8)

	isi = h - 10
	x = 35

	lcmp_m1 = len(colorMap)-1
	for k in range(lcmp_m1):
		cv2.line(m2, (x,int(float(h)*(lcmp_m1-k-1)/4.0)), (x, int(float(h)*(lcmp_m1-k)/4.0)), colorMap[k], 8)
	cv2.line(m2, (x,isi), (x,h), colorMap[-1], 8) # No data -> hitam

	img_ = np.concatenate((img_, m2), axis=1)

	center_contours = []
	for k in range(nwilayah):
		contur = yaml_node.getNode("Corner_" + str(k)).mat()
		contur = np.expand_dims(contur, axis=1)
		contours = [contur]

		kota_ = n_str_wilayah[str(k+1)]
		val_panen = float(json_panen[kom_im][kota_][tahun])

		color2draw = colorMap[-1]
		if (val_panen > 0.0):
			if val_panen <= dictKomThn[kom_im][tahun][0]:
				color2draw = colorMap[0]
			elif val_panen <= dictKomThn[kom_im][tahun][1]:
				color2draw = colorMap[1]
			elif val_panen <= dictKomThn[kom_im][tahun][2]:
				color2draw = colorMap[2]
			elif val_panen > dictKomThn[kom_im][tahun][2]:
				color2draw = colorMap[3]

		img_ = cv2.drawContours(img_, contours, 0, (0,0,0), 3)
		img_ = cv2.drawContours(img_, contours, 0, color2draw, -1)

		lcmp_m2 = len(colorMap)-2
		for k in range(lcmp_m2):
			cv2.putText(img_, "<= "+ str(dictKomThn[kom_im][tahun][lcmp_m2-k-1]), (w-25, int(float(h)*((k+1)/4.0 + 0.125))), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,255), 1)
		cv2.putText(img_, "> "+ str(dictKomThn[kom_im][tahun][2]), (w-25, int(float(h)*(0/4.0 + 0.125))), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,255), 1)
		cv2.putText(img_, "No data", (w-25,isi), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,255), 1)		

		center_contours.append(calc_center_contour(contur))

	for l in range(nwilayah):
		cv2.putText(img_, str(l+1), center_contours[l], cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,255), 2) #+data_json[namaProvinsi][str(l+1)]

	img_ = cv2.resize(img_, (w-40,h))

	_, ecd = cv2.imencode(".png", img_)
	tobyte = base64.b64encode(ecd).decode('ascii')

	to_src = 'data:image/png;base64,{}'.format(tobyte)
	
	return to_src



@app.callback(dash.dependencies.Output('tabOutData', 'children'),
			  [dash.dependencies.Input('tabData', 'value')])
def render_content(tab):
	if tab == 'tabMAP':
		return tabMAP
	elif tab == 'tabCHART':
		return tabCHART
	elif tab == 'tabFORECAST':
		return tabFORECAST


if __name__ == '__main__':
	app.run_server(debug=True, host='127.0.0.17')







# '''
# REFERENCE:

# 1. https://stackoverflow.com/questions/45923296/convert-base64-string-to-an-image-thats-compatible-with-opencv
# 2. https://stackoverflow.com/questions/40928205/python-opencv-image-to-byte-string-for-json-transfer/40930153

# '''