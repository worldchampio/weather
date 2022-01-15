import requests
import numpy as np
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt 

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
    
    elem_type = str(elem[i-1])
    end_elem = 'https://frost.met.no/observations/v0.jsonld'
    param_elem = {
        'sources': source_id,
        'elements': elem_type,
        'referencetime': querydate,
    }

    data = getdata(end_elem,param_elem,client_id)
    # This will return a Dataframe with all of the observations in a table format
    df = pd.DataFrame()

    for i in range(len(data)):
        row = pd.DataFrame(data[i]['observations'])
        row['referenceTime'] = data[i]['referenceTime']
        row['sourceId'] = data[i]['sourceId']
        df = df.append(row)

    df = df.reset_index()
    columns = ['sourceId','referenceTime','elementId','value','unit']

    # Calculate plot limits
    mag_max = str(max(df['value']))
    mag_min = str(min(df['value']))
    # Scale limits
    ylim_param = (float(mag_min)-0.8*float(mag_min),float(mag_max)+0.1*float(mag_max))
    
    # Handle exception if min==max
    if ylim_param == (0,0):
        ylim_param = None
    
    # Make labels pretty
    unit_label = '['+df['unit'][1]+']'
    mag_label = df['elementId'][1]
    mag_label = mag_label.replace('_',' ')

    x = df.loc[:,'referenceTime']
    
    for entry in range(0, len(x)):
        x[entry] = x.loc[entry][:-8]
        x[entry] = x.loc[entry][11:]
    
    y = df['value']

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
