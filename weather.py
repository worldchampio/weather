import requests
import numpy as np
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import rollingAvg

class Weather:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        pd.set_option('mode.chained_assignment',None)
        with open("secret.txt", "r") as file: client_id = file.readline()
        try:
            self.get_data(client_id)
            self.plot_data()
        except Exception as e:
            print("Error: \n\t%s" %(e))
            main()
        except KeyboardInterrupt:
            exit()

    def get_data(self, client_id):
        sensorsystem = self.request_data('https://frost.met.no/sources/v0.jsonld?',{'name': self.get_source_input() }, client_id)
        source_owner   = sensorsystem[0]['name']
        self.source_owner  = str(source_owner[0]+source_owner[1:len(source_owner)].lower())
        self.source_id = sensorsystem[0]['id']
        
        observationParameters = {
            'sources'      : self.source_id,
            'elements'     : self.get_element_input(),
            'referencetime': self.get_today()
        }
        print("Found source %s (%s)" % (self.source_id,self.source_owner))
        self.format_data(self.request_data('https://frost.met.no/observations/v0.jsonld', observationParameters, client_id))

    def get_element_input(self):
        type = ['sea_water_speed','sea_surface_wave_significant_height','wind_speed','air_temperature']
        opts = 'Plot options:\nCurrent[1], Wave Hs[2], Wind[3], Temp[4]: '
        return str(type[int(input(opts))-1])

    def get_source_input(self):
        supportedSources="""
            Yme
            Statfjord a/b/c
            Troll a/b/c
            Draugen
            Sola\n"""
        print("List of some updated sources:\n%s" % supportedSources)
        return str(input("Type location: "))

    def get_today(self):
        today = date.today()
        now = today.strftime("%Y-%m-%d")
        tomorrow = today.strftime("%Y-%m-")+str(int(today.strftime("%d"))+1)
        self.now = now
        return now+'/'+tomorrow

    def request_data(self, endpoint, parameters, clientId):
        r = requests.get(url = endpoint, params = parameters, auth=(clientId,' '))
        if r.status_code == 200: return np.asarray(r.json()['data'])
        else: print("Error %i, %s" %(r.status_code,r.reason))   

    def add_rolling_averages(self):
        legends = ["Raw data"]
        windowSize = (int(len(self.data)/10))
        legends.append(r"$w_{Size}$=%i" % windowSize)   
        self.ax.plot(self.time, rollingAvg.RollingAverage(self.data,windowSize).get_data())   
        return legends

    def format_data(self, data):
        df = pd.DataFrame()
        for i in range(len(data)):
            row = pd.DataFrame(data[i]['observations'])
            row['referenceTime'] = data[i]['referenceTime'][11:-8]
            row['sourceId']      = data[i]['sourceId']
            df = pd.concat([df,row])
        df = df.reset_index()
        self.unitLabel = '['+df['unit'][1]+']'

        if df['unit'][1]=='m/s':
            self.unitLabel = '[kts]'
            for j in range(len(df['value'])):
                df['value'][j]=df['value'][j]*1.94384449
        self.dataMax = str(round(max(df['value']),1))
        self.dataMin = str(round(min(df['value']),1))
        self.displayLabel = df['elementId'][1].replace('_',' ')
        self.time = df.loc[:,'referenceTime']
        self.data = df['value']
        print("Latest entry: \t%s (%i entries)" %(str(self.time.iloc[-1]),self.time.size))

    def space_labels(self):
        n = int(len(self.data)/8)
        for index, label in enumerate(self.ax.xaxis.get_ticklabels()):
            if int(index) % n != 0: label.set_visible(False)

    def plot_data(self):         
        self.ax.plot(self.time, self.data)
        updatedLegends = self.add_rolling_averages()
        plt.suptitle('Displaying '+self.displayLabel+ ' at '+self.source_owner)
        plt.title(
            'Data for '+ self.now +' from '+self.source_id+
            r'. $D_{max}: $'+self.dataMax+r', $D_{min}: $ '+self.dataMin
        )
        plt.xlabel('Time')
        plt.ylabel(self.unitLabel)
        plt.ylim((float(self.dataMin)/2,float(self.dataMax)*1.1))
        self.space_labels()
        plt.legend(updatedLegends)
        plt.grid(axis='y')
        plt.draw()
        plt.pause(1)
        input("<ENTER to close plot>")
        plt.close(self.fig)

def main():
    Weather()
if __name__ == "__main__":
    main()
