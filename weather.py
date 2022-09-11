import requests
import numpy as np
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
from dateutil import parser
import rolling
"""
Two https GET requests are chained together, so that
a source id for a manually inputted location is
requested and used to request data using the source id
attached to the desired location. Four observation types
can then be selected.
"""
class Weather:
    def __init__(self, 
        source  = '',
        element = '',
        date    = '',
        windowSizes = [5]
    ):
        self.fig, self.ax = plt.subplots()
        self.windowSizes = windowSizes
        with open("secret.txt", "r") as file: self.clientID = file.readline()
        try:
            if not source: source = self.getSourceInput()
            if not element: element = self.getElementInput()
            sourceEndpoint      = 'https://frost.met.no/sources/v0.jsonld?'
            observationEndpoint = 'https://frost.met.no/observations/v0.jsonld'
            pd.set_option('mode.chained_assignment',None)
            sensorsystem = self.requestData(sourceEndpoint,{'name':source})
            sourceOwner   = sensorsystem[0]['name']
            self.sourceOwner  = str(sourceOwner[0]+sourceOwner[1:len(sourceOwner)].lower())
            self.sourceID = sensorsystem[0]['id']
            #print("Found source %s (%s)" % (self.sourceID,self.sourceOwner))
            observationParameters = {
                'sources'      : self.sourceID,
                'elements'     : element,
                'referencetime': self.formatDate(date)
            }
            observations = self.requestData(observationEndpoint,observationParameters)
            self.formatData(observations)
            self.plotData()
        except Exception as e:
            print("Error: \n\t%s" %(e))
            main()
        except KeyboardInterrupt:
            exit()

    def getElementInput(self):
        elementNames=['sea_water_speed','sea_surface_wave_significant_height','wind_speed','air_temperature']
        i = int(input('Plot options:\nCurrent[1], Wave Hs[2], Wind[3], Temp[4]: '))
        return str(elementNames[i-1])
   
    def getSourceInput(self):
        supportedSources="""
            Yme
            Statfjord a/b/c
            Troll a/b/c
            Draugen
            Sola\n"""
        print("List of some updated sources:\n%s"%supportedSources)
        sourceName = str(input("Type location: "))
        if sourceName in {"exit","stop","out","break","abort","^C"}: exit()
        return sourceName

    def reportInfo(self):
        print("Found source %s (%s)" % (self.sourceID,self.sourceOwner))
        print("Latest entry: \t%s (%i entries)" %(str(self.time.iloc[-1]),self.time.size))

    def formatDate(self, today):
        if not today: today = date.today()
        else: today = parser.parse(today)
        now   = today.strftime("%Y-%m-%d")
        tomorrow = today.strftime("%Y-%m-")+str(int(today.strftime("%d"))+1)
        self.now = now
        return now+'/'+tomorrow

    def requestData(self, endpoint, parameters):
        r = requests.get(endpoint, parameters, auth=(self.clientID,''))
        if r.status_code == 200: return np.asarray(r.json()['data'])
        else: print("Error %i, %s" %(r.status_code,r.reason))
    
    """
    Create a dataset and corresponding legends with calculated
    rolling average of the raw data if any windowsize is given in c-tor.
    [module @rolling.py]
    """
    def addRollingAverages(self):
        legends = ["Raw data"]
        for windowSize in self.windowSizes:
            legends.append(r"$w_{Size}$=%i" %windowSize)
            averageData = rolling.RollingAverage(self.data,windowSize).getData()   
            self.ax.plot(self.time, averageData)
        return legends

    def formatData(self, data):
        df = pd.DataFrame()
        for i in range(len(data)):
            row = pd.DataFrame(data[i]['observations'])
            row['referenceTime'] = data[i]['referenceTime'][11:-8] #remove unecessary parts of timestamp
            row['sourceId']      = data[i]['sourceId']
            df = pd.concat([df,row])
        df = df.reset_index()
        self.unitLabel = '['+df['unit'][1]+']'
        
        # Convert m/s to kts (Is only done for wind and current)
        if df['unit'][1]=='m/s':
            self.unitLabel = '[kts]'
            for j in range(len(df['value'])):
                df['value'][j]=df['value'][j]*1.94384449
        
        # Calculate plot limits
        self.dataMax = str(round(max(df['value']),1))
        self.dataMin = str(round(min(df['value']),1))
        
        # Store data in object
        self.displayLabel = df['elementId'][1].replace('_',' ')
        self.time = df.loc[:,'referenceTime']
        self.data = df['value']
        self.reportInfo()

    def spaceLabels(self):
        # Display every nth label
        n = int(len(self.data)/8)
        for index, label in enumerate(self.ax.xaxis.get_ticklabels()):
            if int(index) % n != 0: label.set_visible(False)

    def plotData(self):         
        self.ax.plot(self.time, self.data)
        updatedLegends = self.addRollingAverages()
        plt.title(
            'Displaying '+self.displayLabel+ ' at '+self.sourceOwner+
            '.\n Data for '+ self.now +' from '+self.sourceID+
            r'. $D_{max}: $'+self.dataMax+r', $D_{min}: $ '+self.dataMin
        )

        plt.xlabel('Time [hh:mm]')
        plt.ylabel(self.unitLabel)
        self.spaceLabels()
        plt.legend(updatedLegends)
        plt.grid()
        plt.draw()
        plt.pause(1)
        input("<ENTER to close plot>")
        plt.close(self.fig)

def main():
    Weather()
if __name__ == "__main__":
    main()
