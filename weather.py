import requests
import numpy as np
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
from dateutil import parser
"""
Two https GET requests are chained together, so that
a source id for a manually inputted location is
requested and used to request data using the source id
attached to the desired location. Four observation types
can then be selected.

Data is requested for the current day.
"""
# Auxiliary Input functions
def getElementInput():
    elementNames=['sea_water_speed','sea_surface_wave_significant_height','wind_speed','air_temperature']
    i = int(input('Plot options:\nCurrent[1], Wave Hs[2], Wind[3], Temp[4]: '))
    return str(elementNames[i-1])
def getSourceInput():
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

class Weather:
    def __init__(self, 
        source='',
        element='',
        date     = '',  
        plotData = True ):
        try:
            if not source: source = getSourceInput()
            if not element: element = getElementInput()
            sourceEndpoint      = 'https://frost.met.no/sources/v0.jsonld?'
            observationEndpoint = 'https://frost.met.no/observations/v0.jsonld'
            pd.set_option('mode.chained_assignment',None)
            with open("secret.txt", "r") as file: clientID = file.readline()
            sensorsystem = self.requestData(sourceEndpoint,{'name':source},clientID)
            sourceID     = sensorsystem[0]['id']
            sourceOwner  = sensorsystem[0]['name']
            sourceOwner  = str(sourceOwner[0]+sourceOwner[1:len(sourceOwner)].lower())
            print("Found source %s (%s)" % (sourceID,sourceOwner))
            observationParameters = {
                'sources'      : sourceID,
                'elements'     : element,
                'referencetime': self.formatDate(date)
            }
            observations = self.requestData(observationEndpoint,observationParameters,clientID)
            if plotData: self.plotData(observations, sourceOwner, sourceID)
            else: return observations
        except Exception as e:
            print("Error: \n\t%s" %(e))
            main()

    def formatDate(self, today):
        if not today: today = date.today()
        else: today = parser.parse(today)
        now   = today.strftime("%Y-%m-%d")
        day   = int(today.strftime("%d"))+1
        tomorrow = today.strftime("%Y-%m-")+str(day)
        self.now = now
        return now+'/'+tomorrow

    def requestData(self, endpoint, parameters,clientID):
        r = requests.get(endpoint, parameters, auth=(clientID,''))
        if r.status_code == 200: return np.asarray(r.json()['data'])
        else: print("Error %i, %s" %(r.status_code,r.reason))
    
    def plotData(self, data, sourceOwner, source_id):
        df = pd.DataFrame()
        for i in range(len(data)):
            row = pd.DataFrame(data[i]['observations'])
            row['referenceTime'] = data[i]['referenceTime']
            row['sourceId']      = data[i]['sourceId']
            df = pd.concat([df,row])
        df = df.reset_index()
        unit_label = '['+df['unit'][1]+']'
        # Convert m/s to kts (Is only done for wind and current)
        if df['unit'][1]=='m/s':
            unit_label = '[kts]'
            for j in range(len(df['value'])):
                df['value'][j]=df['value'][j]*1.94384449
        # Calculate plot limits
        dataMax = str(round(max(df['value']),1))
        dataMin = str(round(min(df['value']),1))
        # Scale limits
        ylim_param = (float(dataMin)-0.4*float(dataMin),float(dataMax)+0.1*float(dataMax))
        if ylim_param == (0,0):
            ylim_param = None
        # Observation name formatting
        displayLabel = df['elementId'][1].replace('_',' ')
        timeData = df.loc[:,'referenceTime']
        observationData = df['value']
        # Remove unecessary digits from timestamp to get format -> [hh:mm]
        for entry in range(0, len(timeData)):
            timeData[entry] = timeData.loc[entry][:-8]
            timeData[entry] = timeData.loc[entry][11:]
        latestTime = timeData.iloc[-1]
        print("Latest entry: \t%s" %str(latestTime))
        fig, ax = plt.subplots()
        ax.plot(timeData, observationData)
        # Display every nth label
        n = int(len(observationData)/8)
        for index, label in enumerate(ax.xaxis.get_ticklabels()):
            if int(index) % n != 0:
                label.set_visible(False)
        plt.title('Displaying '+displayLabel+ ' at '+sourceOwner+'.\n Data for '+ self.now +' from '+source_id+'. Max: '+dataMax+', Min: '+dataMin )
        plt.xlabel('Time [hh:mm]')
        plt.ylabel(unit_label)
        plt.grid()
        plt.draw()
        plt.pause(1)
        input("<ENTER to close plot>")
        plt.close(fig)

def main():
    Weather()
if __name__ == "__main__":
    main()
