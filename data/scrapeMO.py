import numpy
# from lxml import html
from lxml import etree
import requests
import re
import urllib
import os
import sys
import requests
import json
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError
import time
import xmltodict
import ujson
import time


 # Global Information about all the observations
datasetInfo = {}
datasetInfo["count"] = 0
datasetInfo["names"] = {}
# datasetInfo["ids"] = []

# Create info for specific date, not everything
def processDatasetInfoParallel(date):
    if not os.path.exists('./dataset_summaries'):
        os.mkdir('./dataset_summaries')
    for name in datasetInfo['names']:
        datasetInfo['names'][name]['count'] = len(datasetInfo['names'][name]['ids'])
    datasetInfoJSON = ujson.dumps(datasetInfo)
    with open('./dataset_summaries/datasetInfo_'+date+'.json', 'w', encoding='utf8') as outfile:
        ujson.dump(datasetInfoJSON, outfile)

# Write summary info to file
def processDatasetInfo():
    for name in datasetInfo['names']:
        datasetInfo['names'][name]['count'] = len(datasetInfo['names'][name]['ids'])
    datasetInfoJSON = ujson.dumps(datasetInfo)
    with open('datasetInfo.json', 'w', encoding='utf8') as outfile:
        ujson.dump(datasetInfoJSON, outfile)

def logger(str_to_log):
    # log str to log file.
    with open('logfile.txt', 'a', encoding='utf8') as outfile:
        outfile.write(str_to_log + '\n')

# date is in the format of 'yyyy-mm-dd' or '2016' etc.
# This finds all the observations on date, downloads them, and creates respective JSON files
def getObservations(date):
    try:
        # Get the list of observation Ids for the date
        url = 'http://mushroomobserver.org/api/observations?date='+ date #+'&detail=high'
        print("The API call to get Ids: " + url)
        obIds = []
        response1 = requests.get(url)
        response1 = xmltodict.parse(response1.content)
        for result in response1['response']['results']['result']:
            obIds.append(result['@id'])
        print("Total number of ids to be processed is " + str(len(obIds)))
        total_num_ids = len(obIds)
        # Ensure dir where we will store everything exists
        if not os.path.exists('./dataset'):
            os.mkdir('./dataset')

        # Go through each observation
        # for ob in observations:
        count_ids_processed = 0
        for obId in obIds:
            try:
                time_start = time.time()
                url = 'http://mushroomobserver.org/api/observations?id='+obId+'&detail=high'
                response2 = requests.get(url)
                response2 = xmltodict.parse(response2.content)
                ob = response2['response']['results']['result']

                # Skip if no images:
                if ob['primary_image'] is None:
                    continue

                # Construct the sample JSON for file
                obJSON = {}
                obJSON['id'] = ob['@id']
                obJSON['url'] = ob['@url']
                obJSON['name'] = ob['consensus_name']['name']['#text'].replace(" ", "_")
                obJSON['nameId'] = ob['consensus_name']['@id']
                obJSON['confidence'] = ob['confidence']['#text'] # on a scale of -3 to 3
                obJSON['created_at'] = ob['created_at']['#text']
                obJSON['location'] = {}
                obJSON['location']['name'] = ob['location']['name']['#text']
                obJSON['location']['latitude_north'] = ob['location']['latitude_north']['#text']
                obJSON['location']['latitude_south'] = ob['location']['latitude_south']['#text']
                obJSON['location']['longitude_east'] = ob['location']['longitude_east']['#text']
                obJSON['location']['longitude_west'] = ob['location']['longitude_west']['#text']

                # Create or find directory to store JSON and images
                if not os.path.exists('./dataset/' + obJSON['name']):
                    os.mkdir('./dataset/' + obJSON['name'])

                baseDir = "./dataset/" + obJSON['name'] + "/"
                baseName = obJSON['id'] + '.' + obJSON['name']
                baseURL = "https://images.mushroomobserver.org/320/"

                # Get the primary image (it is stored separately from the others):
                imgId = ob['primary_image']['@id']
                imgFileName = baseName + '.0.jpg'
                imgRes = requests.get(baseURL + imgId + '.jpg')
                if imgRes.status_code == 200:
                    with open(baseDir + imgFileName, 'wb') as outfile:
                        outfile.write(imgRes.content)
                del imgRes

                # Store image ids in JSON file
                obJSON['imageIds'] = [imgId]

                # test if images exists
                if not ob['images'].get('image') == None:
                    # Get all remaining images
                    i = 1
                    for img in ob['images']['image']:
                        try:
                            imgId = img['@id']
                            imgFileName = baseName + '.' + str(i) + '.jpg'
                            imgRes = requests.get(baseURL + imgId + '.jpg')
                            if imgRes.status_code == 200:
                                with open(baseDir + imgFileName, 'wb') as outfile:
                                    outfile.write(imgRes.content)
                            del imgRes
                            obJSON['imageIds'].append(imgId)
                            i += 1
                        except:# Exception as err:
                            logger('IMAGE_FIND_ERROR for observation id: ' + obJSON['id'])
                            continue

                # Write observation JSON file to same directory.
                with open(baseDir + baseName + '.json', 'w', encoding='utf8') as outfile:
                    ujson.dump(obJSON, outfile)

                datasetInfo["count"] += 1
                if datasetInfo['names'].get(obJSON['name']) == None:
                    datasetInfo['names'][obJSON['name']] = {}
                    datasetInfo['names'][obJSON['name']]['ids'] = []
                datasetInfo['names'][obJSON['name']]['ids'].append(obJSON['id'])

                time_end = time.time()
                count_ids_processed += 1
                print("Fetched id " + str(obJSON['id']) + " in " + str(time_end - time_start) + "s :: In date " + date + " :: id " + str(count_ids_processed) + "/" + str(total_num_ids))
                
            except Exception as err:
                logger("ERROR for observation id: "+obId)
                logger(f'{err}')
                continue

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    # except Exception as err:
    #     print(f'Other error occurred: {err}') 



def main():
    dates = [
        # "2012-01","2012-02","2012-03","2012-04","2012-05","2012-06",
        # "2012-07","2012-08","2012-09","2012-10","2012-11","2012-12",

        # "2013-01","2013-02","2013-03","2013-04","2013-05","2013-06",
        # "2013-07","2013-08","2013-09","2013-10","2013-11","2013-12",

        # "2014-01","2014-02","2014-03","2014-04","2014-05","2014-06",
        # "2014-07","2014-08","2014-09","2014-10","2014-11","2014-12",

        # "2015-01","2015-02","2015-03","2015-04","2015-05","2015-06",
        # "2015-07","2015-08","2015-09","2015-10","2015-11","2015-12",

        # "2016-01","2016-02","2016-03","2016-04","2016-05","2016-06",
        # "2016-07","2016-08","2016-09","2016-10","2016-11","2016-12",

        # "2017-01","2017-02","2017-03","2017-04","2017-05","2017-06",
        # "2017-07", # STOPPED HERE
        # "2017-08",
        # "2017-09",
        # "2017-10",
        # "2017-11",
        # "2017-12",

        # "2018-01", # STARTED HERE
        # "2018-02",
        # "2018-03",
        # "2018-04",
        # "2018-05",
        # "2018-06",
        # "2018-07",
        "2018-08", # failed at >>> Fetched id 325769 in 6.087580919265747s :: In date 2018-08 :: id 337/6136
        # "2018-09",
        # "2018-10",
        # "2018-11",
        # "2018-12" # failed at >>> Fetched id 350163 in 5.488338947296143s :: In date 2018-12 :: id 668/3174
    ]

    for date in dates:
        try:
            time_start = time.time()
            print("Getting observations for " + date)
            getObservations(date)
            processDatasetInfoParallel(date)
            time_end = time.time()
            print("Fetched date " + date + " in " + str(time_end - time_start) + "s")
        except Exception as err:
            print("Error: " + date + "skipped")
            print(f'The Error is: {err}')
            continue

    # processDatasetInfo()


main()

# date = "2019-05-11"
# getObservations(date)
# processDatasetInfo()





