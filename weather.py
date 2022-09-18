import requests
import numpy as np
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
from dateutil import parser
import rollingAvg

class Weather:
    """
    Two https GET requests are chained together, so that
    a source id for a manually inputted location is
    requested and used to request data using the source id
    attached to the desired location. Four observation types
    can then be selected.
    Rolling average can be calculated, with windowsize = 5 as default.
    +------+
    | FLOW |
    +------+
    INPUT: location:
        -> GET(location)        -> ID
    INPUT: element:
        -> GET(..,ID,element)   -> DATA
    INPUT: windowSize(s)
        -> calculate RollingAverage(s)

    plot(DATA)
    plot(RollingAverage(s))
    """
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
            observationParameters = {
                'sources'      : self.sourceID,
                'elements'     : element,
                'referencetime': self.formatDate(date)
            }
            observations = self.requestData(observationEndpoint,observationParameters)
            self.formatData(observations)
            self.reportInfo()
            self.plotData()
        except Exception as e:
            print("Error: \n\t%s" %(e))
            main()
        except KeyboardInterrupt:
            exit()
    # Prompt user for element selection
    def getElementInput(self):
        elementNames=['sea_water_speed','sea_surface_wave_significant_height','wind_speed','air_temperature']
        i = int(input('Plot options:\nCurrent[1], Wave Hs[2], Wind[3], Temp[4]: '))
        return str(elementNames[i-1])
    # Prompt user for location name
    def getSourceInput(self):
        supportedSources="""
            Yme
            Statfjord a/b/c
            Troll a/b/c
            Draugen
            Sola\n"""
        print("List of some updated sources:\n%s"%supportedSources)
        sourceName = str(input("Type location: "))
        if sourceName in {"exit","stop","out","break","abort"}: exit()
        return sourceName
    # Print source ID, owner name and last entry timestamp.
    def reportInfo(self):
        print("Found source %s (%s)" % (self.sourceID,self.sourceOwner))
        print("Latest entry: \t%s (%i entries)" %(str(self.time.iloc[-1]),self.time.size))
    """
    Param  : dateInput (format must be 'YYYY-MM-DD')
    Return : today/tomorrow in format 'YYYY-MM-DD/YYYY-MM-DD'
    """
    def formatDate(self, dateInput):
        if not dateInput: dateInput = date.today()
        else: dateInput = parser.parse(dateInput)
        now   = dateInput.strftime("%Y-%m-%d")
        tomorrow = dateInput.strftime("%Y-%m-")+str(int(dateInput.strftime("%d"))+1)
        self.now = now
        return now+'/'+tomorrow
    # Send a GET-request to the REST-API endpoint, return data  if successful
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
        for i in range(0,len(self.windowSizes)):
            windowSize = self.windowSizes[i]
            if (windowSize > len(self.data)): windowSize = len(self.data)
            legends.append(r"$w_{Size}$=%i" % windowSize)
            averageData = rollingAvg.RollingAverage(self.data,windowSize).getData()   
            self.ax.plot(self.time, averageData)
        
        return legends
    # Extract data recieved from the REST-API to use for plotting
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
        self.dataMax = str(round(max(df['value']),1))
        self.dataMin = str(round(min(df['value']),1))
        self.displayLabel = df['elementId'][1].replace('_',' ')
        self.time = df.loc[:,'referenceTime']
        self.data = df['value']
    # Space plot labels n entries apart
    def spaceLabels(self):
        n = int(len(self.data)/8)
        for index, label in enumerate(self.ax.xaxis.get_ticklabels()):
            if int(index) % n != 0: label.set_visible(False)
    # Plot data, and calculate+plot rolling averages, if any were requested.
    def plotData(self):         
        self.ax.plot(self.time, self.data)
        updatedLegends = self.addRollingAverages()
        plt.suptitle('Displaying '+self.displayLabel+ ' at '+self.sourceOwner)
        plt.title(
            'Data for '+ self.now +' from '+self.sourceID+
            r'. $D_{max}: $'+self.dataMax+r', $D_{min}: $ '+self.dataMin
        )
        plt.xlabel('Time')
        plt.ylabel(self.unitLabel)
        plt.ylim((float(self.dataMin)*0.9,float(self.dataMax)*1.1))
        self.spaceLabels()
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