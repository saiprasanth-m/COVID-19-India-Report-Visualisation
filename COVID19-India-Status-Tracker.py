'''
MIT License
Copyright (c) 2020 Sai Prasanth
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import numpy as np
import datetime
import json

cur_date = str(datetime.date.today())
##cur_date = "2020-05-07"

def get_data_from_url(Url):
    resp = requests.get(Url)
    if resp.status_code == 200:
        print("Scrapping the site...\n")
        soup = BeautifulSoup(resp.content, 'html.parser')

        status = soup.find_all('div', class_='status-update')[0]
        Title = str(status.get_text()).split('\n')
        Head = Title[1].split(' ')
        Datetime = Head[6]+' '+Head[5]
        print(Title[1])
        
        ### Getting Active Cases ###
        active_cases = soup.find_all('li', class_='bg-blue')[0]
        active_cases = active_cases.get_text().split("\n")[2]
        print("Total Active Cases: "+active_cases)
        
        ### Getting Total Recovered ###
        tot_recovered = soup.find_all('li', class_='bg-green')[0]
        tot_recovered = tot_recovered.get_text().split("\n")[2]
        print("Recovered Cases: "+tot_recovered)

        ### Getting Total Deaths ###
        tot_death = soup.find_all('li', class_='bg-red')[0]
        tot_death = tot_death.get_text().split("\n")[2]
        print("Death Cases: "+tot_death+"\n")

        case_stats = Datetime+ ":" +active_cases+ "," + tot_recovered+ "," +tot_death+ "\n"
        
        print("Getting state table data")
        
        ### Getting Table details ###
        table = soup.find_all('table')[0]
        
        columns = []
        for head in table.find_all('th'):
            columns.append(head.get_text())

        rows = 0
        colm = []
        for row in table.find_all('tr'):
            cols = 0
            for col in row.find_all('td'):
                colm.append(col.get_text())
                cols += 1
                
        final = []
        for i in range(0,len(colm)):
            new_colm = []
            for j in range(i,len(colm), 5):
                new_colm.append(colm[j])
            final.append(new_colm)
            
        fin_dict = {}
        check = []
        for cnt in range(0,len(columns)):
            fin_dict[columns[cnt]] = final[cnt]
            check = len(fin_dict[columns[cnt]])
            if check>34:
                fin_dict[columns[cnt]] = fin_dict[columns[cnt]][:-1]
            
        return case_stats,fin_dict,columns,Title[1]
    
def create_json(out_data):
    stat_dict = {}
    for data in out_data:
        date = data.split(":")[0]
        counts = data.split(":")[1]
        stat_dict[date]=counts
        
    with open("Case-stats.json", "w") as file:
        obj = json.dumps(stat_dict)
        file.write(obj)
        file.close()
    return obj
        
def read_data_from_file(filename):
    read_file = open(filename,"r",encoding = 'utf-8')
    out = read_file.readlines()
    read_file.close()
    json_ = create_json(out)
    return out 
    
def write_data_to_file(filename,case_stats):
    out = read_data_from_file(filename)
    last_entry = out[len(out)-1]
    
    if last_entry != case_stats:
        if last_entry.split(":")[0] == case_stats.split(":")[0]: #If case data has been updated in the same date
            temp_data = out[:len(out)-1]
            temp_str = ""
            for val in temp_data:
                temp_str = temp_str+val
            temp_str = temp_str+case_stats
                
            write_file = open(filename,"w")
            write_file.write(temp_str)
            write_file.close()
            print("Data has been written in: "+filename)
        else:
            
            write_file = open(filename,"a")
            write_file.write(case_stats)
            write_file.close()
            print("Data has been written in: "+filename)

def get_date_wise_data(input_date,filename):
    out = read_data_from_file(filename)
    input_date = input_date.split('-')[2]
    for data in out:
        data = data.split(":")
        date_data = data[0].split(' ')
        if date_data[1] == input_date:
            case_data = data[1]
            case_data = case_data.split(",")
            active_data = case_data[0]
            recov_data = case_data[1]
            death_data = case_data[2]
            break
    
    return active_data, recov_data, death_data

def plot_state_wise_data(date,states,confirmed,recovered,death,title):

    """
    To Visualize state-wise covid-19 case counts in a bar chart
    X-axis - States/Union Territories
    Y-axis - Counts in range of 100

    Inputs:
    date      - current date to get the total case counts | Data_Type- String | Format- 'yyyy-mm-dd'
    states    - List of corona affected states in india
    confirmed - List of active case counts with respect to states list
    recovered - List of recovered case counts with respect to states list
    death     - List of death case counts with respect to states list

    Outputs:
    returns NULL
    """

    X = np.arange(len(states))
    fig = plt.figure(figsize = (20,10))

    plt.bar(X, confirmed, 0.25, color='g')
    plt.bar(X+0.25, recovered, 0.25, color='b')
    plt.bar(X+0.50, death, 0.25, color='r')

    plt.xticks(X, states, rotation=45)
    max_cnt = sorted(confirmed)
    min_val = 0
    max_val = max_cnt[len(max_cnt)-1]+ 500
    plt.yticks(np.arange(min_val,max_val,1000),fontsize = 12)
   
    plt.xlabel('States/UT',fontsize = 15)
    plt.ylabel('Count',fontsize = 15)
    plt.title(title,fontsize = 15)

    active_data, recov_data, death_data = get_date_wise_data(cur_date,filename)
    
    plt.legend(labels=['Active Cases - '+active_data,'Recovered - '+recov_data, 'Deaths - '+death_data],loc ='upper right', fontsize = 15)
    for index, value in enumerate(confirmed):
        plt.text(index, value, str(value), fontsize = 20, color='r',horizontalalignment = 'center',verticalalignment = 'bottom')

    plt.savefig(r'State-wise Reports/State-wise Report-'+cur_date+'.png')

def plot_date_wise_data():

    '''
    To Visualize date-wise covid-19 case counts in a bar chart
    X-axis - Date
    Y-axis - Counts in range of 100

    Inputs:
    No input arguments

    Outputs:
    returns NULL
    '''


    stat_dates = []
    actives = []
    recovs = []
    deaths = []

    out = read_data_from_file(filename)
    for data in out:
        data = data.split(":")
        date_data = data[0]
        case_data = data[1]

        stat_dates.append(date_data)

        case_data = case_data.split(",")
        active_data = case_data[0]
        recov_data = case_data[1]
        death_data = case_data[2]
        
        actives.append(int(active_data))
        recovs.append(int(recov_data))
        deaths.append(int(death_data))
        
    X = np.arange(len(stat_dates))
    fig = plt.figure(figsize = (20,10))

    plt.bar(X, actives, 0.25, color='g')
    plt.bar(X, recovs, 0.25, color='b')
    plt.bar(X, deaths, 0.25, color='r')

    plt.xticks(X, stat_dates, fontsize = 12, rotation=45)
    plt.yticks(np.arange(0,actives[-1]+10001,6000), fontsize = 12)

    plt.xlabel('Cases',fontsize = 15)
    plt.ylabel('Count',fontsize = 15)
    plt.title('Covid-19 India - Datewise Report',fontsize = 15)

    plt.legend(labels=['Active Cases','Recovered','Deaths'],loc ='upper right', fontsize = 15)
    for index, value in enumerate(actives):
        plt.text(index , value, str(value), fontsize = 20, color='g',horizontalalignment = 'center',verticalalignment = 'bottom')
    for index, value in enumerate(recovs):
        plt.text(index+0.35 , value+300, str(value), fontsize = 15, color='b',horizontalalignment = 'center',verticalalignment = 'bottom')
    for index, value in enumerate(deaths):
        plt.text(index+0.35 , value, str(value), fontsize = 15, color='r',horizontalalignment = 'center',verticalalignment = 'bottom')

    plt.savefig(r'Date-wise Reports/Date-wise Report-'+cur_date+'.png')

def plot_active_vs_recovered_data():

    '''
    To Visualize active vs recovered percentage rates of covid-19 case counts.
    X-axis - Date
    Y-axis - Counts in range of 20

    Inputs:
    No input arguments

    Outputs:
    returns NULL
    '''
    
    stat_dates = []
    actives = []
    recovs = []
    deaths = []

    out = read_data_from_file(filename)
    for data in out:
        data = data.split(":")
        date_data = data[0]
        case_data = data[1]

        stat_dates.append(date_data)

        case_data = case_data.split(",")
        active_data = case_data[0]
        recov_data = case_data[1]
        death_data = case_data[2]
        
        actives.append(int(active_data))
        recovs.append(int(recov_data))
        deaths.append(int(death_data))

    active_rate = [round(100*(actives[ind]-actives[ind-1])/actives[ind-1]) if ind!=0 else 0 for ind,data in enumerate(actives)]
    recov_rate = [round(100* abs(recovs[ind]-recovs[ind-1])/recovs[ind-1]) if ind!=0 else 0 for ind,data in enumerate(recovs)]
    death_rate = [round(100*(deaths[ind]-deaths[ind-1])/deaths[ind-1]) if ind!=0 else 0 for ind,data in enumerate(deaths)]
##
##    active_rate = [actives[ind]-actives[ind-1] if ind!=0 else 0 for ind,data in enumerate(actives)]
##    recov_rate = [recovs[ind]-recovs[ind-1] if ind!=0 else 0 for ind,data in enumerate(recovs)]
##    death_rate = [deaths[ind]-deaths[ind-1] if ind!=0 else 0 for ind,data in enumerate(deaths)]

##    print(recov_rate)
    X = np.arange(0,len(stat_dates))
    fig = plt.figure(figsize=(20,10))

    plt.title("Active vs Recovered Rate", fontsize=15)
    plt.xlabel("Date", fontsize=15)
    plt.ylabel("New Cases percentage(%)", fontsize=15)
    sns.pointplot(stat_dates, active_rate, color="r", linewidth=5, markers='o')
    sns.pointplot(stat_dates, recov_rate, color="coral", linewidth=5, markers='o')

    plt.xticks(X, stat_dates, rotation=45)
    plt.yticks(np.arange(0, 100, 25))
    plt.legend(labels = ["Active", "Recovered"], fontsize=15)

    plt.savefig(r'Rate-Active-vs-Recovered.png')

def plot_active_vs_death_data():
    '''
    To Visualize active vs death percentage rates of covid-19 case counts.
    X-axis - Date
    Y-axis - Counts in range of 20

    Inputs:
    No input arguments

    Outputs:
    returns NULL
    '''
    stat_dates = []
    actives = []
    recovs = []
    deaths = []

    out = read_data_from_file(filename)
    for data in out:
        data = data.split(":")
        date_data = data[0]
        case_data = data[1]

        stat_dates.append(date_data)

        case_data = case_data.split(",")
        active_data = case_data[0]
        recov_data = case_data[1]
        death_data = case_data[2]
        
        actives.append(int(active_data))
        recovs.append(int(recov_data))
        deaths.append(int(death_data))

    active_rate = [round(100*(actives[ind]-actives[ind-1])/actives[ind-1]) if ind!=0 else 0 for ind,data in enumerate(actives)]
    recov_rate = [round(100* abs(recovs[ind]-recovs[ind-1])/recovs[ind-1]) if ind!=0 else 0 for ind,data in enumerate(recovs)]
    death_rate = [round(100*(deaths[ind]-deaths[ind-1])/deaths[ind-1]) if ind!=0 else 0 for ind,data in enumerate(deaths)]

    X = np.arange(0, len(stat_dates))
    fig = plt.figure(figsize=(20,10))

    plt.title("Recovery vs Death Rate", fontsize=15)
    plt.xlabel("Date", fontsize=15)
    plt.ylabel("New Cases percentage(%)", fontsize=15)
    sns.pointplot(stat_dates, recov_rate, color="coral", linewidth=5, markers='o')
    sns.pointplot(stat_dates, death_rate, color="r", linewidth=5, markers='o')

    plt.xticks(X, stat_dates, rotation=45)
    plt.yticks(np.arange(0, 100, 25))
    plt.legend(labels = ["Recovery", "Death"], fontsize=15)

    plt.savefig(r'Rate-Recovery-vs-Death.png')

    
if __name__ == "__main__":
    
    filename = r'Case-stats.txt'
    case_stats,fin_dict,columns,title = get_data_from_url("https://www.mohfw.gov.in/")

    write_data_to_file(filename,case_stats)
        
    table = pd.DataFrame(data=fin_dict)
    table.to_excel(r'excel_data/'+"COVID-19 INDIA "+cur_date+".xlsx",index = False)

    new_table = table[:-1] # Eliminating last row
    
    states = new_table[columns[1]]
    confirmed = new_table[columns[2]].map(int)
    recovered = new_table[columns[3]].map(int)
    death = new_table[columns[4]].map(int)

    print("\nStarted plotting...")
    
    plot_state_wise_data(cur_date,states,confirmed,recovered,death,title)
    plot_date_wise_data()

    plot_active_vs_recovered_data()
    plot_active_vs_death_data()
