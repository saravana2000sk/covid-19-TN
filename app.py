from flask import Flask,render_template,url_for
import pandas as pd
import requests
from io import BytesIO

app = Flask(__name__,static_folder='templates')
@app.route('/')
def default():
	url = "https://api.covid19india.org/csv/latest/state_wise.csv"
	response=requests.get(url)
	covid=response.content
	TNdata = pd.read_csv(BytesIO(covid))
	TNdata.set_index("State", inplace = True)

	url = "http://api.covid19india.org/v4/min/data.min.json"
	response = requests.get(url)
	covid=response.json()
	dist = covid["TN"]

	url="http://api.covid19india.org/csv/latest/cowin_vaccine_data_districtwise.csv"
	response=requests.get(url)
	covid=response.content
	data = pd.read_csv(BytesIO(covid))
	data.set_index("District_Key", inplace = True)
	chennai = data.loc["TN_Chennai"].iloc[-80:]
	date = []
	vacc = []
	for x in range(0,80,10):
		date.append(chennai.index[x])
		vacc.append(chennai.iloc[x])

	return render_template('index.html',
		confirmedcases=TNdata.loc["Tamil Nadu"]["Confirmed"],
		activecases=TNdata.loc["Tamil Nadu"]["Active"],
		death=TNdata.loc["Tamil Nadu"]["Deaths"],
		recovered=TNdata.loc["Tamil Nadu"]["Recovered"],
		vacinchennai=dist["districts"]["Chennai"]["total"]["vaccinated1"] + dist["districts"]["Chennai"]["total"]["vaccinated2"],
		vacad=dist["total"]["vaccinated1"] + dist["total"]["vaccinated2"],
		totalvacc=dist["total"]["vaccinated1"] + dist["total"]["vaccinated2"],
		chevacc=dist["districts"]["Chennai"]["total"]["vaccinated1"] + dist["districts"]["Chennai"]["total"]["vaccinated2"],
		otherdisvacc=(dist["total"]["vaccinated1"] + dist["total"]["vaccinated2"])-(dist["districts"]["Chennai"]["total"]["vaccinated1"] + dist["districts"]["Chennai"]["total"]["vaccinated2"]),
		
		date=date,vacc=vacc,
		
		conperlak=round(((TNdata.loc["Tamil Nadu"]["Confirmed"]/75695000)*100000),1),
		conperlakpec=round((((TNdata.loc["Tamil Nadu"]["Confirmed"]/75695000)*100000)/1000),1),
		actrio=round((((TNdata.loc["Tamil Nadu"]["Active"])/(TNdata.loc["Tamil Nadu"]["Confirmed"]))*100),1),
		recrio=round((((TNdata.loc["Tamil Nadu"]["Recovered"])/(TNdata.loc["Tamil Nadu"]["Confirmed"]))*100),1),
		casfatalrio=round((((TNdata.loc["Tamil Nadu"]["Deaths"])/(TNdata.loc["Tamil Nadu"]["Confirmed"]))*100),1))
@app.route('/table')
def table():
	url="https://api.covid19india.org/csv/latest/district_wise.csv"
	response=requests.get(url)
	covid=response.content
	data = pd.read_csv(BytesIO(covid))
	TN = data[data.State_Code == "TN"]
	TN=TN.iloc[:,4:9]
	TN.set_index("District", inplace = True)
	TN.drop("Unknown",axis=0,inplace=True)
	TN.drop("Other State",axis=0,inplace=True)
	TN.drop("Railway Quarantine",axis=0,inplace=True)
	TN.drop("Airport Quarantine",axis=0,inplace=True)

	url = "http://api.covid19india.org/v4/min/data.min.json"
	response = requests.get(url)
	covid=response.json()
	dist = covid["TN"]["districts"]
	vaccine = {}
	for i in dist.keys():
		try:
			vaccine[i] = (dist[i]["total"]["vaccinated1"],dist[i]["total"]["vaccinated2"])
		except KeyError:
			pass

	
	return render_template('table.html',TN=TN.to_numpy(),TN_distic=TN.index,vaccine=vaccine)
if __name__ == '__main__':
   app.run(host="0.0.0.0",debug=True)

