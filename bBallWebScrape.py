import bs4
import requests
import pandas as pd
import numpy as np
import boto3
import matplotlib.pyplot as plt
from IPython.display import display


def getBasketballLegend(name = 'Michael Jordan'):
    link = 'https://en.wikipedia.org/wiki/' + name.title().replace(" ","_")
    # read the webpage
    response = requests.get(link)

    # create a BeautifulSoup object to parse the HTML  
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    # the player stats are defined  with the attribute CSS class set to
    # 'wikitable sortable'therefore we create a tag object "table"
    table = soup.find(class_='wikitable sortable')
    # the headers of the table are the first table row (tr) we create a tag
    # object that has the first row  
    headers=table.tr

    titles=headers.find_all("abbr")
    abbrevs = {str(title).replace(str(title['title']),'').replace(str('<abbr title="">'),'').replace(str('</abbr>'),''):title['title'] for title in titles}
    return abbrevs


def getBasketballStats(name = 'Michael Jordan', plLegend = None):
    link = 'https://en.wikipedia.org/wiki/' + name.title().replace(" ","_")

    # read the webpage
    response = requests.get(link)

    # create a BeautifulSoup object to parse the HTML  
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    # the player stats are defined  with the attribute CSS class set to
    # 'wikitable sortable' therefore we create a tag object "table"
    sortableTable = True
    table = soup.find(class_='wikitable sortable')

    if type(table) == type(None):
        sortableTable = False
        table = soup.find(class_='wikitable')  
    assert(type(table) != type(None)), 'No data available on wikipedia for ' + name

    # the headers of the table are the first table row (tr) we create a tag
    # object that has the first row  
    headers=table.tr


    # the table column names are displayed  as an abbreviation; therefore we
    # find all the abbr tags and returs an Iterator
    if sortableTable:
        titles=headers.find_all("abbr")
        # we create a dictionary  and pass the table headers as the keys
        data = {title['title']:[] for title in titles}
    else:
        titles=headers.find_all()
        if plLegend == None:
            linkMJ = 'https://en.wikipedia.org/wiki/Michael_Jordan'
            responseMJ = requests.get(linkMJ)
            soupMJ = bs4.BeautifulSoup(responseMJ.text, 'html.parser')
            tableMJ = soupMJ.find(class_='wikitable sortable')
            headersMJ = tableMJ.tr
            titlesMJ=headersMJ.find_all("abbr")
            abbrevsMJ = {str(title).replace(str(title['title']),'').replace(str('<abbr title="">'),'').replace(str('</abbr>'),''):title['title'] for title in titlesMJ}
        else:
            abbrevsMJ = plLegend
        # we create a dictionary  and pass the table headers as the keys
        data = {str(abbrevsMJ[str(titles[i]).replace("\n","").replace("<th>","").replace("</th>","")]) :[] for i in range(2,len(titles))}

    # we store each column as a list in a dictionary, the header of the column
    # will be the dictionary key we iterate over each table row by finding each 
    # table tag tr and assigning it to the object
    for row in table.find_all('tr')[1:]:    
    # we iterate over each cell in the table, as each cell corresponds to a
    # different column, we obtain all of the keys corresponding to the column n 
        for key, a in zip(data.keys(),row.find_all("td")[2:]):
            # we append each elment and strip any extra HTML contnet 
            data[key].append(''.join(c for c in a.text if (c.isdigit() or c == ".")))

    # we remove extra rows by finding the smallest list     
    Min=min([len(x)  for x in data.values()])
    #we convert the elements in the key to floats 
    for key in data.keys():    
        data[key]=list(map(lambda x: float(x), data[key][:Min]))       
    return data



def plotStatVsTime(stat, names):
    plLegendMJ = getBasketballLegend()
    for name in names:
        dataFrame = pd.DataFrame(getBasketballStats(name, plLegend = plLegendMJ))
        availableStats = [key for key, value in dataFrame.iteritems()]         
        try:
            pldatFram = dataFrame[[stat]]
            plt.plot(pldatFram,label=name)
        except KeyError:
            print('Error: No stat called ' + stat + ' is avalable on ' + name +
                  '\'s wikipedia page\nAvalable stats are:\n' + '%s' %
                  '\n'.join(map(str, availableStats)) + '\n')

    plt.legend(shadow=True)
    plt.xlabel('years')
    plt.ylabel(stat)
    plt.show()

namesList =['Michael Jordan','Kobe Bryant','Lebron James','Stephen Curry',
            'Detlef Schrempf', 'Shawn Kemp','Charles Barkley']

plotStatVsTime(stat = 'Field goal percentage', names = ['Detlef Schrempf', 'Michael Jordan'])

plotStatVsTime(stat = '3-point field-goal percentage', names = namesList)


