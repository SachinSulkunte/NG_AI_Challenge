
## Oh boy, libraries that I don't know what they do
import pandas as pd
import datetime
import httplib2
from googleapiclient.discovery import build
from collections import defaultdict
from dateutil import relativedelta
import argparse
from oauth2client import client
from oauth2client import file
from oauth2client import tools


## This is supposed to send you to some site? I'm not really sure, I'm just copying and pasting
site = 'https://www.yoursite.com'

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
DISCOVERY_URI = ('https://www.googleapis.com/discovery/v1/apis/customsearch/v1/rest')

CLIENT_SECRETS_PATH = r'C:\Users\wkcov\PycharmProjects\GoogleCrawl\client_secrets.json'

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])
flags = parser.parse_args([])

flow = client.flow_from_clientsecrets(
    CLIENT_SECRETS_PATH, scope=SCOPES,
    message=tools.message_if_missing(CLIENT_SECRETS_PATH))

storage = file.Storage(r'C:\Users\wkcov\PycharmProjects\GoogleCrawl\searchconsolereporting.dat')
credentials = storage.get()

if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)
http = credentials.authorize(http=httplib2.Http())

webmasters_service = build('webmasters', 'v3', http=http)

"""
Step 4 Make your first API Call
"""

site_list = webmasters_service.sites().list().execute()

verified_sites_urls = [s['siteUrl'] for s in site_list['siteEntry']
                       if s['permissionLevel'] != 'siteUnverifiedUser'
                       and s['siteUrl'][:4] == 'http']

for site_url in verified_sites_urls:
    print(site_url)