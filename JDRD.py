import json
import requests
import sys
import time
import xml.etree.ElementTree as ET
import os

import urllib.parse as urlparse
from urllib.parse import parse_qs


###########################
#   Configuration Items   #
###########################

# DLAPI Server Information
DLAPI_SERVER = os.environ['DLAPI_SERVER']
DLAPI_KEY = os.environ['DLAPI_KEY']

# From your own jackett server
JACKETT_SERVER = os.environ['JACKETT_SERVER']
JACKETT_KEY = os.environ['JACKETT_KEY']

# Set a limit to the number of torrents jacket can return.
SEARCH_LIMIT = 300

# Paths to both movie and tv directories. Make sure '/' is at the end!
MOVIE_OUTPUT_DIR =  os.environ['MOVIE_OUTPUT']
TV_OUTPUT_DIR = os.environ['TV_OUTPUT']

# Header for DLAPI
dl_header = {'Authorization': DLAPI_KEY}

###########################
# End Configuration Items #
###########################

"""
Search jackett for urls.
query: The string to search for (i.e. TV Name)
limit: The limit of results to return.
returns: request text, otherwise raises exception.
"""
def search_jacket(query, categories="5000,5010,5030,5040,5045,5050,5060,5070,5080,2000,2010,2020,2030,2040,2045,2050,2060,2070,2080", limit=5):
    req = requests.get(JACKETT_SERVER + "?apikey=%s&cat=%s&t=search&limit=%d&q=%s" % (JACKETT_KEY, categories, limit, query))
    if req.status_code == 200:
        return req.text
    else:
        raise Exception("Jackett Query Failed.")

"""
Convert a result string from search
res: The string result from searching jackett.
returns: The ElementTree
"""
def convert_xml(res):
    return ET.fromstring(res)

"""
Convert a jackett result into a dictionary
root: The root of an xml string.
returns: A dictionary of {title: {url, seeders}} strings.
"""
def get_magnet_links(root):
    info = {}
    for child in root.iter('item'):
        title = child.find('title').text
        url = child.find('link').text
        try:
            url = requests.get(url).url
        except requests.exceptions.InvalidSchema as e:
            url = str(e).split("'")[1]
        seeders = -1
        for subchild in child.iter('{http://torznab.com/schemas/2015/feed}attr'):
            if subchild.attrib['name'] == 'seeders':
                seeders = int(subchild.attrib['value'])
                break
        info[title] = {'url' : url, 'seeders' : seeders}
    return info


# Release main method.
def main():

    # Get what show type it is
    showType = ""
    while True:
        showType = input("(T)V, (M)ovie or (E)xit: ").lower()
        if showType == "e":
            sys.exit(0)
            break
        if showType == 't' or showType == 'm':
            break

    # Movies can just be saved to the movies directory. Update categories fed to jacket.
    categories = '2000,2010,2020,2030,2040,2045,2050,2060,2070,2080'
    location = MOVIE_OUTPUT_DIR
    if showType == 't':
        categories = '5000,5010,5030,5040,5045,5050,5060,5070,5080'
        location = TV_OUTPUT_DIR

    # Ask user for name
    query = input("Enter search query: ")
    req = search_jacket(query, categories=categories, limit=SEARCH_LIMIT)

    # Convert to xml and get all magnet links
    root = convert_xml(req)
    links = get_magnet_links(root)
    links = {k: v for k, v in sorted(links.items(), key=lambda x: -1 * x[1]['seeders'])}
    #print(linkss)
    titles = list(links.keys())
    ind = -1

    # When there is zero results, end.
    if len(titles) == 0:
        print("Zero titles were found.")
        sys.exit(-1)
    
    # Get user to select which torrent they want to download.
    boundMax = 10
    curBound = boundMax
    while ind < 0 or ind > len(titles) - 1:
        print('---------------------------')
        for i in range(max(0, curBound-10), min(curBound, len(titles))):
            try:
                print("ID: %d - %s - Seeders: %d" % (i, titles[i], links[titles[i]]['seeders']))
            except:
                print("ID: %d - NON UNICODE TITLE - Seeders: %d" % (i, links[titles[i]]['seeders']))
        print('---------------------------')
        try: 
            ind = input("Select ID to Download (-1 to Exit, '+' to see next %d, '-' to see previous %d): " % (boundMax, boundMax))

            # Allow scrolling up and down in search list
            if ind == '+':
                curBound = min(curBound + boundMax, len(titles))
            elif ind == '-':
                curBound = max(curBound - boundMax, boundMax)
            ind = int(ind)

        except:
            ind = -2
            print("\n\n")
        if ind == -1:
            sys.exit(-1)

    # Get the magnet link of the selected item.
    mag = links[titles[ind]]['url']

    # Offer to listen to RD updates
    if showType == 't':
        print("Please enter metadata information for the show your trying to download.")
        series = input("Enter show name: ")

        while True:
            # Ask if there is any sub folders. A complete pack only needs to be downloaded to a master folder.
            isFull = input("Is the torrent multi-folder (Y/N): ").lower()
            if isFull == 'y' or isFull == 'n':
                break

        # If its not a complete torrent, get the season number to place the files in
        if isFull == 'n':
            
            # Verify season number
            while True:
                try:
                    season = int(input("Enter season number: "))
                    break
                except:
                    pass
            location += series + "/S" + str(season) + "/"
        else:
            # Just add the series name to the location.
            location += series + "/"

    # END MOVED FUNCTION
    print("Location: %s" % location)
    req = requests.post(DLAPI_SERVER + "/api/v1/content", json={'magnet_url': mag, 'path': location}, headers=dl_header)
    if req.status_code != 200:
        print("Error in sending to DLAPI: Status code %d, Info: %s" % (req.status_code, req.text))
    else:
        print("Download has been sent to DLAPI server.")
    
if __name__ == "__main__":
    main()