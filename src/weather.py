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
    elif r.status_code == 401:
        print('Invalid client id.')
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
        
def main():
    f = open("secret.txt","r")
    client_id = str(f.read(36))
    f.close()

    #lol
    pd.set_option('mode.chained_assignment',None)
    
    # Make query date
    today = date.today()
    now = today.strftime("%Y-%m-%d")
    day = int(today.strftime("%d"))+1
    tomorrow = today.strftime("%Y-%m-")+str(day)
    querydate = str(now+'/'+tomorrow)

    # Get desired location: 
    name_src = str(input("Type location: [yme, statfjord a/b/c, troll a/b/c, .. etc] \n"))

    # Source request
    end_src = 'https://frost.met.no/sources/v0.jsonld?'
    param_src = {
        'name': name_src
    }

    # Source response 
    source_body = getdata(end_src,param_src,client_id)
    source_id = source_body[0]['id']
    stationholder = source_body[0]['name']
    stationholder = stationholder[0]+stationholder[1:len(stationholder)].lower()

    # Data choice list
    elem = ['sea_water_speed','sea_surface_wave_significant_height','wind_speed','air_temperature']
    i = int(input('Plot options:\nCurrent[1], Wave Hs[2], Wind[3], Temp[4]: '))
    
    # Observation request
    elem_type = str(elem[i-1])
    end_elem = 'https://frost.met.no/observations/v0.jsonld'
    param_elem = {
        'sources': source_id,
        'elements': elem_type,
        'referencetime': querydate,
    }

    # Observation response
    data = getdata(end_elem,param_elem,client_id)
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
    
    # TEST COMMENT
    
    # Convert m/s to kts (Is only done for wind and current)
    if df['unit'][1]=='m/s':
        unit_label = '[kts]'
        for j in range(len(df['value'])):
            df['value'][j]=df['value'][j]*1.94384449 #to kts

    # Calculate plot limits
    mag_max = str(round(max(df['value']),1))
    mag_min = str(round(min(df['value']),1))
    # Scale limits
    ylim_param = (float(mag_min)-0.4*float(mag_min),float(mag_max)+0.1*float(mag_max))
    
    # Handle exception if min==max
    if ylim_param == (0,0):
        ylim_param = None
    
    # Make element name prettier
    mag_label = df['elementId'][1].replace('_',' ')

    # Data for x-axis
    x = df.loc[:,'referenceTime']
    y = df['value']

    # remove unecessary digits from timestamp to get format -> [hh:mm]
    for entry in range(0, len(x)):
        x[entry] = x.loc[entry][:-8]
        x[entry] = x.loc[entry][11:]
    
    # Plot the data
    fig, ax = plt.subplots()
    ax.plot(x, y)

    ax.set(xlabel='time [hh:mm]', 
            ylabel=unit_label, 
            ylim=ylim_param,
            title= 'Displaying '+mag_label+ ' at '+stationholder+'.\n Data for '+ now +' from '+source_id+'. Max: '+mag_max+', Min: '+mag_min )
    ax.grid()
    plt.setp(ax.get_xticklabels(), rotation=60, ha='right')
    plt.setp(ax.get_xticklabels()[::2], visible=False,fontsize=2)
    
    fig.savefig("Plot.png")

if __name__ == "__main__":
    main()
