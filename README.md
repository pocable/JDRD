# JDRD
Python script to search Jackett for a movie/tvshow, add it as a torrent to real debrid,
and then once real debrid is done downloading send it to jdownloader2 and store locally.

## Installation
Run these two commands and you are good to go:
```
pip install -r requirements.txt  
python JDRD.py
```

## Configuration
Open up the python file. You will see the following section. You can modify any of the
following information. Ignore the REAL_DB_SERVER and header, they can be changed but
shouldn't be.
```python
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
```
|Config Tag|Description|
|------|:-----:|
|JDOWNLOADER_USER|Username for http://my.jdownloader.org |
|JDOWNLOADER_PASS|Password for http://my.jdownloader.org |
|JDOWNLOADER_DEVICE|Device for http://my.jdownloader.org |
|JACKETT_SERVER|Jackett server torznab address and endpoint. Should look like http://0.0.0.0:9117/api/v2.0/indexers/all/results/torznab |
|JACKETT_KEY|Jackett api key from the top right of Jackett|
|REAL_DB_KEY|Real Debrid API Key https://real-debrid.com/apitoken |
|SEARCH_LIMIT|Limit on the number of Jackett responses returned |
|MOVIE_OUTPUT_DIR|The directory JDownloader2 will download into when movies are selected |
|TV_OUTPUT_DIR|The directory JDownloader2 will download into when tv shows are selected |

## Troubleshooting

|Issue|Fix|
|:-----:|:----:|
|JDownloader2 is unable to find device| Make sure your device name matches te one you assigned on http://my.jdownloader.org. It is case sensitive |
|Throwing Exception| Likely a real debrid issue. Above the exception block there should be a status code. Check here for codes: https://api.real-debrid.com/. Make sure you have a correct API key as well. |
|NON UNICODE TITLE as an option title| Some torrents have non unicode characters in the title. This was a quick fix to display them. |