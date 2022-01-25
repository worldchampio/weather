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

def getdata(endpoint, parameters,_client_id):
    client_id = _client_id

    r = requests.get(endpoint, parameters, auth=(client_id,''))
    # Extract JSON data
    json = r.json()

    # Check if the request worked, print out any errors
    if r.status_code == 200:
        #print('Data retrieved from ' + endpoint)
        data = json['data']
        return np.asarray(data)
    else:
        print('Error! Returned status code %s' % r.status_code)
        print('Message: %s' % json['error']['message'])
        print('Reason: %s' % json['error']['reason'])

        # Handle source with no available data
        if 'name' in parameters:
            new_src = input("Not found, try another name: ")
            new_param = {'name':new_src}
            return np.asarray(getdata(endpoint,new_param,client_id))
        elif 'sources' in parameters:
            main()

def plotdata(data, stationholder, source_id, t_now):
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
            df['value'][j]=df['value'][j]*1.94384449 #to kts

    # Calculate plot limits
    #   Find the max value of the row, round
    #   to 1 decimal point, convert to string
    mag_max = str(round(max(df['value']),1))
    mag_min = str(round(min(df['value']),1))
    
    # Scale limits
    #   Maybe the scaling methods of matplotlib
    #   are better but these look nicer 
    ylim_param = (float(mag_min)-0.4*float(mag_min),float(mag_max)+0.1*float(mag_max))
    
    # Handle exception if min==max
    #   If data is supposed to be available,
    #   but for some reason isnt, df['value']
    #   will be all zeros, in which case the
    #   scaling method is set to None to make
    #   matplotlib handle it (ie eliminate error messages)
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

    ax.set(xlabel='time [hh:mm]', 
            ylabel=unit_label, 
            ylim=ylim_param,
            title= 'Displaying '+mag_label+ ' at '+stationholder+'.\n Data for '+ t_now +' from '+source_id+'. Max: '+mag_max+', Min: '+mag_min )
    ax.grid()
    plt.setp(ax.get_xticklabels(), rotation=60, ha='right')
    plt.setp(ax.get_xticklabels()[::2], visible=False)
    
    # This file will be deleted next time the 
    # bash script is executed
    fig.savefig("Plot.png")
        
def main():
    # Client id is stored in secret.txt,
    # and should start on the first character
    # on the first line
    f = open("secret.txt","r")
    client_id = str(f.read(36))
    f.close()

    # Supress pd error messages (hey if it works)
    pd.set_option('mode.chained_assignment',None)
    
    # Make query date
    today = date.today()
    now = today.strftime("%Y-%m-%d")
    day = int(today.strftime("%d"))+1
    tomorrow = today.strftime("%Y-%m-")+str(day)
    
    # Source request
    end_src = 'https://frost.met.no/sources/v0.jsonld?'
    param_src = {
        'name': str(input("Type location: [yme, statfjord a/b/c, troll a/b/c, .. etc] \n"))
    }

    # Source response
    source_body = getdata(end_src,param_src,client_id)
    source_id = source_body[0]['id']
    stationholder = source_body[0]['name']
    # The name is returned in all caps, and formatted properly below:
    stationholder = stationholder[0]+stationholder[1:len(stationholder)].lower()

    # Data choice list
    elem = ['sea_water_speed','sea_surface_wave_significant_height','wind_speed','air_temperature']
    i = int(input('Plot options:\nCurrent[1], Wave Hs[2], Wind[3], Temp[4]: '))
    
    # Observation request
    end_observ = 'https://frost.met.no/observations/v0.jsonld'
    param_observ = {
        'sources': source_id,
        'elements': str(elem[i-1]),
        'referencetime': str(now+'/'+tomorrow),
    }

    # Observation response
    data = getdata(end_observ,param_observ,client_id)

    # Plot the response
    plotdata(data,stationholder,source_id,now)

if __name__ == "__main__":
    main()