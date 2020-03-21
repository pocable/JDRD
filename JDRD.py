import json
import requests
import sys
import time
import xml.etree.ElementTree as ET
import myjdapi

import urllib.parse as urlparse
from urllib.parse import parse_qs

###########################
#   Configuration Items   #
###########################

# https://my.jdownloader.org/
JDOWNLOADER_USER = ""
JDOWNLOADER_PASS = ""
JDOWNLOADER_DEVICE = ""

# From your own jackett server
JACKETT_SERVER = ""
JACKETT_KEY = ""

# https://real-debrid.com/apitoken
REAL_DB_KEY = ""

# Set a limit to the number of torrents jacket can return.
SEARCH_LIMIT = 300

# Paths to both movie and tv directories. Make sure '/' is at the end!
MOVIE_OUTPUT_DIR = "/media/movies/"
TV_OUTPUT_DIR = "/media/tv/"

# Should not be changed
REAL_DB_SERVER = "https://api.real-debrid.com/rest/1.0/"
header = {'Authorization': 'Bearer ' + REAL_DB_KEY }

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

"""
Send a magnet url to realdebrid to being downloading.
magnet: The url.
returns: 
"""
def send_to_rd(magnet):
    data = {'magnet': magnet}
    req = requests.post(REAL_DB_SERVER + "torrents/addMagnet", data=data, headers=header)
    if req.status_code != 201:
        print(req.status_code)
        print(req.text)
        raise Exception("Issue adding magnet to RD downloads. Status code:" + str(req.status_code))
    else:
        res = json.loads(req.text)
        ident = res['id']
        req = requests.post(REAL_DB_SERVER + "torrents/selectFiles/%s" % ident, data={'files': "all"}, headers=header)
        if req.status_code != 204 and req.status_code != 202:
            print(req.status_code)
            print(req.text)
            raise Exception("Issue selecting files for RD download. Status code:" + str(req.status_code))
        else:
            return ident

"""
Check if RD has an instant download torrent available.
links: Magnet link to check the has on RD servers.
returns: Boolean if its an instant download link.
"""
def check_magnet_instant(link):

    # Extract hash from each magnet link
    parsed = urlparse.urlparse(link)
    full = parse_qs(parsed.query)['xt'][0].split(':')
    has = full[len(full)-1]

    # Send request for instant availability.
    req = requests.get(REAL_DB_SERVER + "torrents/instantAvailability/" %  has, headers=header)
    print(req.text)


"""
Listener to listen if RD has finished downloading the file.
ident: The RD id of the file.
returns: True if it has finished, False if error.
"""
def launch_listener(ident, delay=10):
    ite = 0
    while(True):
        ite += 1
        req = requests.get(REAL_DB_SERVER + "torrents/info/%s" %  ident, headers=header)
        if(req.status_code == 401 or req.status_code == 403):
            raise Exception("Failed to get torrent info. Status code: " + str(req.status_code))
        res = json.loads(req.text)
        print("Current Status: %s, Iteration: %d" % (res['status'], ite))
        if res['status'] == 'downloaded':
            return True
        elif res['status'] == 'magnet_error':
            return False
        elif res['status'] == 'virus':
            return False
        elif res['status'] == 'error':
            return False
        elif res['status'] == 'dead':
            return False
        time.sleep(delay)
    print("Finished listening to file: %s" % ident)

"""
Get the real debrid download url from the website
ident: The identifier for the show your looking for.
returns: The links associated with the identifier
"""
def get_rd_download_urls(ident):
    req = requests.get(REAL_DB_SERVER + "torrents/info/%s" %  ident, headers=header)
    if(req.status_code == 401 or req.status_code == 403):
        raise Exception("Failed to get torrent info. Status code: " + str(req.status_code))
    res = json.loads(req.text)
    return res['links']

"""
Listen for real debrid updates and then download when RD is done downloading.
ident: The identifer for the show.
"""
def listen_and_download(ident, direc):
    state = launch_listener(ident)
    if state == False:
        print("RD error occured. Please check Real Debrid: https://real-debrid.com/torrents")
    else:
        device = setup_jdownload()
        urls = get_rd_download_urls(ident)
        download_urls = []
        for url in urls:
            req = requests.post(REAL_DB_SERVER + "unrestrict/link", data={'link': url}, headers=header)
            res = json.loads(req.text)
            if(req.status_code == 401 or req.status_code == 403):
                raise Exception("Failed to get torrent info. Status code: " + str(req.status_code))
            download_urls.append(res['download'])
        jdownload(device, download_urls, direc)
        print("Download started!")

"""
Send a list of urls to a jdownloader device
device: The jdownload device
urls: The list of urls to download
path: The path to download to.
"""
def jdownload(device, urls, path):
    print('\n'.join(urls))
    device.linkgrabber.add_links([{'autostart': True, 'links': '\n'.join(urls), 'destinationFolder': path + "", "overwritePackagizerRules": True}])

"""
Setup jdownloader using the given username and password
returns: The device to send downloads to.
"""
def setup_jdownload():
    jd = myjdapi.Myjdapi()
    jd.set_app_key("JDRD")
    jd.connect(JDOWNLOADER_USER, JDOWNLOADER_PASS)
    jd.update_devices()
    device = jd.get_device(JDOWNLOADER_DEVICE)
    return device

# Release main method.
if __name__ == "__main__":

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
        
        for i in range(curBound-10, min(curBound, len(titles))):
            try:
                print("ID: %d - %s - Seeders: %d" % (i, titles[i], links[titles[i]]['seeders']))
            except:
                print("ID: %d - NON UNICODE TITLE - Seeders: %d" % (i, links[titles[i]]['seeders']))
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
        if ind == -1:
            sys.exit(-1)

    # Get the magnet link of the selected item.
    mag = links[titles[ind]]['url']

    # Send to real debrid.
    ident = send_to_rd(mag)
    print("Download Sent. Identifier: %s" % ident)

    # Offer to listen to RD updates
    choice = ""
    while choice != "Y" or choice != "N":
        choice = input("Do you want to listen until the file is finished downloading and then upload to JDownloader?\nOnly use this option when you are not running an RD listen server (Y/N): ")
        if choice.upper() == "Y":


            # Has been moved from earlier. Should be own function.
            # Metadata Information if its a show. Otherwise just download to movies directory.
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
            listen_and_download(ident, location)
            break

        elif choice.upper() == "N":
            print("Goodbye!")
            break
    
