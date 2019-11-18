from textblob import TextBlob
import datefinder
import pandas as pd
from datetime import datetime
import os

string = 'I want one mumbai-ahmedabad ticket on 11 nov'
#string = 'I want to go from mumbai to delhi'
def to_comp(string):
    string = string.lower()
    df = pd.read_csv(os.getcwd()+'/BookyBotApp/flightdata.csv')
    list = string.split()
    get_indexes = lambda list, xs: [i for (y, i) in zip(xs, range(len(xs))) if list == y]

    if len(get_indexes('to', list)) == 0:
        #print('Hi')
        return "No Data"
    else:
        for i in get_indexes('to', list):
            #print(list[i + 1])
            if list[i+1] in df['City'].to_list():
                string1 = str(list[i+1])
            else:
                string1 = "Destination not Found"
        return string1

def from_comp(string):
    string = string.lower()
    df = pd.read_csv(os.getcwd()+'/BookyBotApp/flightdata.csv')
    list = string.split()
    get_indexes = lambda list, xs: [i for (y, i) in zip(xs, range(len(xs))) if list == y]

    if len(get_indexes('from', list)) == 0:
        return "No Data"
    else:
        for i in get_indexes('from', list):
            #print(list[i+1])
            if list[i + 1] in df['City'].to_list():
                return str(list[i + 1])
            else:
                return "Source not Found"

def blob_search(string):
    destination = ""
    source = ""
    finaldate = ""
    #print(string)
    blob = TextBlob(string.title())
    blob1 = TextBlob(string)
    txt = blob.tags
    #print(txt)
    arr =[]
    df = pd.read_csv(os.getcwd()+'/BookyBotApp/flightdata.csv')
    for i in range(len(txt)):
        if txt[i][1] == "NNP":
            if str(txt[i][0]).lower() in df['City'].to_list():
                if txt[i-1][1] == "TO":
                    destination = txt[i][0]
                elif txt[i-1][1] != "TO":
                    source = txt[i][0]
            else:
                continue
        else:
            continue

    for i in range(len(txt)):
        if txt[i][0] == "To":
            if str(txt[i+1][0]).lower() in df['City'].to_list():
                destination = txt[i+1][0]
        elif txt[i][0] == "From":
            if str(txt[i+1][0]).lower() in df['City'].to_list():
                source = txt[i+1][0]

    for i in range(len(txt)):
        if '-' in txt[i][0]:
            tmp = txt[i][0]
            tmp = tmp.replace('-', ' ').split(' ')
            if len(tmp) == 2:
                if tmp[0].lower() in df['City'].to_list():
                    source = tmp[0]
                if tmp[1].lower() in df['City'].to_list():
                    destination = tmp[1]



    today = datetime.now()
    dates = datefinder.find_dates(str(blob1.correct()))
    for date in dates:
        if date is None:
            finaldate = ""
        else:
            finaldate = date
            if finaldate < today:
                finaldate = finaldate.replace(year=today.year+1)
            finaldate = str(finaldate.strftime("%d/%m/%Y"))
    arr = [source.lower(), destination.lower(), str(finaldate)]
    return arr

#print(blob_search(string))