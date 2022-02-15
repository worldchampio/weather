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
    def __init__(self, end_src, end_observ) -> None:
        try:
            elem = ['sea_water_speed','sea_surface_wave_significant_height','wind_speed','air_temperature']

            # Make query date
            today = date.today()
            now = today.strftime("%Y-%m-%d")
            day = int(today.strftime("%d"))+1
            tomorrow = today.strftime("%Y-%m-")+str(day)

            # Supress pd error messages (hey if it works)
            pd.set_option('mode.chained_assignment',None)

            # Load client id
            f = open("secret.txt","r")
            client_id = str(f.read(36))
            f.close()
            
            # Format source parameters with user input
            param_src = self.get_src()

            # Response is bundled in 'sensorsystem'
            sensorsystem = self.getdata(end_src, param_src, client_id)
            
            # Extract id and name
            source_id = sensorsystem[0]['id']
            stationholder = sensorsystem[0]['name']
            # The name is returned in all caps, and formatted properly below:
            stationholder = stationholder[0]+stationholder[1:len(stationholder)].lower()

            # Observation selection
            i = int(input('Plot options:\nCurrent[1], Wave Hs[2], Wind[3], Temp[4]: '))

            param_observ = {
                'sources': source_id,
                'elements': str(elem[i-1]),
                'referencetime': str(now+'/'+tomorrow)
            }

            observations = self.getdata(end_observ, param_observ, client_id)
        
            self.plotdata(observations, stationholder, source_id, now)
        except ValueError:
            print("Valueerror raised")
            main()
        except TypeError:
            print("Typeerror raised")
            main()

    def get_src(self):
        return {
            'name': str(input("Type location: [yme, statfjord a/b/c, troll a/b/c, .. etc] \n"))
        }
        
    def getdata(self, endpoint, parameters,_client_id): # Done
        client_id = _client_id

        r = requests.get(endpoint, parameters, auth=(client_id,''))
        # Extract JSON data
        json = r.json()
        # Check if the request worked, print out any errors
        if r.status_code == 200:
            data = json['data']
            return np.asarray(data)
        # Handle source with no available data
        else:
            print("No data found. ("+r.status_code+")")
            main()

    def plotdata(self, data, stationholder, source_id, t_now): #Done
        df = pd.DataFrame()

        # Handle returned array
        for i in range(len(data)):
            row = pd.DataFrame(data[i]['observations'])
            row['referenceTime'] = data[i]['referenceTime']
            row['sourceId'] = data[i]['sourceId']
            df = df.append(row)

        df = df.reset_index()
        columns = ['sourceId','referenceTime','elementId','value','unit']

        unit_label = '['+df['unit'][1]+']'
            
        # Convert m/s to kts (Is only done for wind and current)
        if df['unit'][1]=='m/s':
            unit_label = '[kts]'
            for j in range(len(df['value'])):
                df['value'][j]=df['value'][j]*1.94384449

        # Calculate plot limits
        #   Find the max value of the row, round
        #   to 1 decimal point, convert to string
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
        
        # Plot the data
        fig, ax = plt.subplots()
        ax.plot(x, y)

        # Display every nth label
        n = int(len(y)/8)
        for index, label in enumerate(ax.xaxis.get_ticklabels()):
            if int(index) % n != 0:
                label.set_visible(False)

        # Plot options
        plt.title('Displaying '+mag_label+ ' at '+stationholder+'.\n Data for '+ t_now +' from '+source_id+'. Max: '+mag_max+', Min: '+mag_min )
        plt.xlabel('Time [s]')
        plt.ylabel(unit_label)
        plt.grid()
        fig.savefig("Plot.png")
        
def main():    
    obj = Weather('https://frost.met.no/sources/v0.jsonld?','https://frost.met.no/observations/v0.jsonld')

if __name__ == "__main__":
    main()
