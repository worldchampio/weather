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
        print('Data retrieved from ' + endpoint)
        data = json['data']
        return np.asarray(data)
    else:
        print('Error! Returned status code %s' % r.status_code)
        print('Message: %s' % json['error']['message'])
        print('Reason: %s' % json['error']['reason'])
        if 'name' in parameters:
            new_src = input("Not found, try another name: ")
            new_param = {'name':new_src}
            return np.asarray(getdata(endpoint,new_param,client_id))
        elif 'sources' in parameters:
            main()
    
    
def main():
    client_id = '<CLIENT ID HERE>'

    #lol
    pd.set_option('mode.chained_assignment',None)
    
    # Make query date
    today = date.today()
    now = today.strftime("%Y-%m-%d")
    day = int(today.strftime("%d"))+1
    tomorrow = today.strftime("%Y-%m-")+str(day)
    querydate = now+'/'+tomorrow

    # Get desired location: 
    name_src = str(input("Skriv navn på ønsket målested: [yme, statfjord a/b/c, troll a/b/c, .. etc] \n"))

    # Source request
    end_src = 'https://frost.met.no/sources/v0.jsonld?'
    param_src = {
        'name': name_src
    }
    
    
    # Source response 
    source_body = getdata(end_src,param_src,client_id)
    source_id = source_body[0]['id']
    stationholder = source_body[0]['name']
    stationholder = stationholder[0]+stationholder[1:100].lower()


    # Data choice list
    elem = ['sea_water_speed','sea_surface_wave_significant_height','wind_speed','air_temperature']
    i = int(input('Current[1], Wave Hs[2], Wind[3], Temp[4]: '))
    
    elem_type = str(elem[i-1])

    end_elem = 'https://frost.met.no/observations/v0.jsonld'
    param_elem = {
        'sources': source_id,
        'elements': elem_type,
        'referencetime': str(querydate),
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
    df2 = df[columns].copy()
    df2['referenceTime'] = pd.to_datetime(df2['referenceTime'],)
    
    # uncomment to show data in terminal
    # print(df2)
    
    unit_label = df2['unit'][1]
    mag_label = df2['elementId'][1]
    mag_label = mag_label.replace('_',' ')

    x = df.loc[:,'referenceTime']
    
    for entry in range(0, len(x)):
        x[entry] = x.loc[entry][:-8]
        x[entry] = x.loc[entry][11:]
    
    y = df['value']

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set(xlabel='time [hh:mm]', ylabel=unit_label,
            title='Data for '+ now +' from '+source_id+'\n Displaying '+mag_label+ ' at '+stationholder+': ' )
    ax.grid()
    plt.setp(ax.get_xticklabels(), rotation=60, ha='right')
    plt.setp(ax.get_xticklabels()[::2], visible=False)
    fig.savefig("Plot.png")

if __name__ == "__main__":
    main()
