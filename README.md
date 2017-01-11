## Nessus Downloader

This script will download the latest scan that is specified and it will save it to a specified directory.

## Usage
```
python nessus_dl.py -e server -n DA_Server -c DA -o /Users/belnox/workspace/nessus_api
```

## Help
```
usage: nessus_dl.py [-h] -e ENVIRONMENT -n SCANNAME -c CLIENTNAME -o PATH [-l] [-f]

A script to download the latest nessus scan

optional arguments:
  -h, --help      show this help message and exit
  -e ENVIRONMENT  The environment, eg. -e workstation
  -n SCANNAME     The scan name, eg. -e DA_Server_Weekly
  -c CLIENTNAME   The client name, eg. -c DA
  -o PATH         The full path to where the file will be saved, eg. -o /home/nessus/drop/      
  -l              Lists the files in the "My Scans" folder
  -f              Forces the download of the latest file
 ```

