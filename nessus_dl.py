try:import requests
except: print('Need to install the Requests module before execution'); exit()
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import mmap
import argparse
import datetime
import time
import json
import sys

# <methods>
#
# # Input:
# -The base url of Nessus
# -The File ID of the scan
# -The Export File ID, that is found in the response of the export request
# Return:
# -True if the term "loading" is no longer present in the response of the dlStatus request
# -False if the term "loading" is indeed present in the dlStatus request
def checkStatus(url,fid,eid):
    dlStatus = requests.get('{0}/scans/{1}/export/{2}/status'.format(url, fid, eid), headers=headers, verify=False)

    if "loading" in dlStatus.content:
        return False
    else:
        return True

# Input:
# -The file id of the scan
# -The output of getTime() goes here
# Return:
# -Nothing, but it writes the downloaded file to the location specified in the -o flag.
def exportFile(fid,scanDate):
    print 'Sending the export request'
    data = '{"format" : "nessus"}'
    exportResp = requests.post('{0}/scans/{1}/export'.format(url, fid,), headers=headers, data=data, verify=False)

    if exportResp.status_code != 200:
        e = exportResp.json()
        print e['error']
        sys.exit()

    while checkStatus(url,fid,exportResp.json()['file']) == False:
        print "Waiting for the file to be ready..."
        time.sleep(3)

    print "File is ready to be downloaded"

    dlFile = requests.get('{0}/scans/{1}/export/{2}/download'.format(url, fid, exportResp.json()['file']), headers=headers, verify=False)

    print 'Exporting the scan'

    filename = '{0}_{1}_{2}{3}.nessus'.format(args.clientName, args.environment.capitalize(), scanDate.split('-')[0],scanDate.split('-')[1])

    if not args.path.endswith('/'):
        args.path += '/'

    print('Saving scan results to {0}{1}'.format(args.path, filename))

    with open("{0}{1}".format(args.path, filename), 'w') as f:
        f.write(dlFile.content)

    print "Save successfull"
# Input:
# -The json time value of the scan
# Return:
# -The Nessus time in a readable state - the months is in text with day in number
def getTime(jTime):
    floatedModTime = float(jTime)
    return time.strftime('%B-%d', time.localtime(floatedModTime))

# Input:
# -The API access key
# -The API secret key
# -The base nessus URL
# Return:
# -A JSON file containing all the scan items
def getList(accessKey,secretKey,url):
    listRequest = requests.get("{0}/scans".format(url), headers=headers, verify=False)

    jlist = json.loads(listRequest.content)

    return jlist

# Input:
# -None
# Return:
# -The ID of the folder defined in the global varibles
def getFolderID():
    for item in jList['folders']:
        if folderName in item['name']:
            return item['id']

# </methods>


# <globalVariables>
# # For the script to know what args.environment to access and to name the files correctly with the client name
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
parser = argparse.ArgumentParser(description='A script to download the latest nessus scan')
parser.add_argument("-e", action="store", dest="environment", help='The environment, eg. -e workstation', required=True)
parser.add_argument("-n", action="store", dest="scanName", help='The scan name, eg. -e DA_Server_Weekly', required=True)
parser.add_argument("-c", action="store", dest="clientName", help='The client name, eg. -c DA', required=True)
parser.add_argument("-o", action="store", dest="path", help='The full path to where the file will be saved, eg. -c /home/nessus/drop/', required=True)
parser.add_argument("-l", action="store_true", dest="listBool", help='Lists the files in the "My Scans" folder')
parser.add_argument("-f", action="store_true", dest="forceBool", help='Forces the download of the latest file')
args = parser.parse_args()

# Adapt to speceifc client
accessKey = "9fdb1c116939d7f2f9d431c5753fb5ace9d720b05064088b15fa5344d545845b"
secretKey = "343b7559d78c65426a43b82ae0b5b8f1e3008c1c5ed6da3cbf0efb841d32e57e"

# The request headers
headers = {
'X-ApiKeys': 'accessKey=%s; secretKey=%s'%(accessKey,secretKey),
'content-type': 'application/json',
}

url = "https://10.11.12.28:8834"
listScans = []
listDates = []
verify = False
folderName = "My Scans"
# </globalVariables>

# </methods>


if __name__ == '__main__':
    print
    try:
        with open("history.txt") as myfile:
            pass
    except IOError:
        with open("history.txt", "a") as myfile:
            pass

    jList = getList(accessKey,secretKey,url)

    if args.listBool == True:
        for item in jList['scans']:
            if getFolderID() == item['folder_id']:
                print ("Name: {0}; ID: {1}".format(item['name'], item['id']))
        sys.exit()


    else:
        for item in jList['scans']:
            if getFolderID() == item['folder_id']:
                if args.scanName.lower() in item['name'].lower():
                    listScans.append(item)
                    listDates.append(getTime(item['last_modification_date']))
                    latestScan = item

        latestScanDate = max(listDates)

# Checks and Writes the history file
        with open("history.txt", "r+a") as myfile:
            if (not latestScanDate in myfile.read()) or (args.forceBool):
                scanId = latestScan['id']
                scanDate = getTime(latestScan['last_modification_date'])
                exportFile(scanId,scanDate)
                myfile.write(latestScanDate + "\n")
            else:
                print "ERROR the file has been downloaded before!\nIf you still want to download the file please use the force (-f) flag."

            print "Done"
            print
            sys.exit()
