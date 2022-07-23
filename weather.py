import requests
import numpy as np
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt

"""
Two https GET requests are chained together, so that
a source id for a manually inputted location is
requested and used to request data using the source id
attached to the desired location. Four observation types
can then be selected.

Data is currently requested for the current day.
"""

class Weather:
    today = date.today()
    now   = today.strftime("%Y-%m-%d")
    day   = int(today.strftime("%d"))+1
    tomorrow = today.strftime("%Y-%m-")+str(day)

    def __init__(self, end_src, end_observ) -> None:
        try:
            elem = ['sea_water_speed','sea_surface_wave_significant_height','wind_speed','air_temperature']

            # Supress pd error messages
            pd.set_option('mode.chained_assignment',None)

            with open("secret.txt", "r") as file:
                client_id = file.readline()
            
            # Response is bundled in 'sensorsystem'
            sensorsystem = self.get_data(end_src, self.get_src(), client_id)

            # Extract id and name
            source_id     = sensorsystem[0]['id']
            stationholder = sensorsystem[0]['name']
            # The name is returned in all caps, and formatted properly below:
            stationholder = stationholder[0]+stationholder[1:len(stationholder)].lower()

            # Observation selection
            print("Found source %s (%s)" % (source_id,stationholder))
            i = int(input('Plot options:\nCurrent[1], Wave Hs[2], Wind[3], Temp[4]: '))

            param_observ = {
                'sources'      : source_id,
                'elements'     : str(elem[i-1]),
                'referencetime': str(self.now+'/'+self.tomorrow)
            }

            observations = self.get_data(end_observ, param_observ, client_id)
            self.plot_data(observations, stationholder, source_id)

        except Exception as e:
            print("Error: %s" %e)
            main()

    def get_src(self):
        return {
            'name': str(input("Type location: [yme, statfjord a/b/c, troll a/b/c, .. etc] \n"))
        }
        
    def get_data(self, endpoint, parameters,_client_id): # Done
        client_id = _client_id

        r = requests.get(endpoint, parameters, auth=(client_id,''))
        # Extract JSON data
        json = r.json()
        
        # Check if the request worked, print out any errors
        if r.status_code == 200:
            data = json['data']
            return np.asarray(data)
        else:
            print("Error %i, %s" %(r.status_code,r.reason))
        
    def plot_data(self, data, stationholder, source_id): #Done
        df = pd.DataFrame()

        # Handle returned array
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
        mag_max = str(round(max(df['value']),1))
        mag_min = str(round(min(df['value']),1))
        
        # Scale limits
        ylim_param = (float(mag_min)-0.4*float(mag_min),float(mag_max)+0.1*float(mag_max))

        if ylim_param == (0,0):
            ylim_param = None
        
        # Observation name formatting
        mag_label = df['elementId'][1].replace('_',' ')

        # Data for plot 
        x = df.loc[:,'referenceTime']
        y = df['value']

        # Remove unecessary digits from timestamp to get format -> [hh:mm]
        for entry in range(0, len(x)):
            x[entry] = x.loc[entry][:-8]
            x[entry] = x.loc[entry][11:]
        
        print("Latest entry: \t%s" %str(x.iloc[-1]))
        
        # Plot the data
        fig, ax = plt.subplots()
        ax.plot(x, y)

        # Display every nth label
        n = int(len(y)/8)
        for index, label in enumerate(ax.xaxis.get_ticklabels()):
            if int(index) % n != 0:
                label.set_visible(False)

        # Plot options
        plt.title('Displaying '+mag_label+ ' at '+stationholder+'.\n Data for '+ self.now +' from '+source_id+'. Max: '+mag_max+', Min: '+mag_min )
        plt.xlabel('Time [hh:mm]')
        plt.ylabel(unit_label)
        plt.grid()
        #plt.show()
        plt.draw()
        plt.pause(1)
        input("<ENTER to close plot>")
        plt.close(fig)

def main():
    obj = Weather('https://frost.met.no/sources/v0.jsonld?','https://frost.met.no/observations/v0.jsonld')

if __name__ == "__main__":
    main()
