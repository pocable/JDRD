# JDRD
Python script to search Jackett for a movie/tvshow and send it to DLAPI. I'm just gonna call
this a temp prototype frontend for DLAPI.

## Installation
Run these two commands and you are good to go:
```
pip install -r requirements.txt  
python JDRD.py
```

## Configuration
Open up the python file. You will see the following section. You can modify any of the
following information. Ignore the REAL_DB_SERVER, header and dl_header, they can be changed 
but shouldn't be.
```python
###########################
#   Configuration Items   #
###########################

# DLAPI Server Information
DLAPI_SERVER = ""
DLAPI_KEY = ""

# From your own jackett server
JACKETT_SERVER = ""
JACKETT_KEY = ""

# Set a limit to the number of torrents jacket can return.
SEARCH_LIMIT = 300

# Paths to both movie and tv directories. Make sure '/' is at the end!
MOVIE_OUTPUT_DIR = "/media/movies/"
TV_OUTPUT_DIR = "/media/tv/"

# Header for DLAPI
dl_header = {'Authorization': DLAPI_KEY}

###########################
# End Configuration Items #
###########################
```
|Config Tag|Description|
|------|:-----:|
|DLAPI_SERVER|Server IP address for DLAPI host. |
|DLAPI_KEY|API Key set in environment variables for DLAPI |
|JACKETT_SERVER|Jackett server torznab address and endpoint. Should look like http://0.0.0.0:9117/api/v2.0/indexers/all/results/torznab |
|JACKETT_KEY|Jackett api key from the top right of Jackett|
|SEARCH_LIMIT|Limit on the number of Jackett responses returned |
|MOVIE_OUTPUT_DIR|The directory JDownloader2 will download into when movies are selected |
|TV_OUTPUT_DIR|The directory JDownloader2 will download into when tv shows are selected |

## Troubleshooting

|Issue|Fix|
|:-----:|:----:|
|Throwing Exception| Make sure you are connected to the internet. Other than that post in issues your crash. |
|NON UNICODE TITLE as an option title| Some torrents have non unicode characters in the title. This was a quick fix to display them. |