import base64
from email.mime.text import MIMEText
import mimetypes
import httplib2
import os
import ConfigParser
import re
import datetime
from email import utils

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import evelink.api
import evelink.char

mailLabel="eve"

def remove_tags(text):
    text1 = re.sub('<br>', "\r\n",text)
    return re.sub('<[^>]*>', '',text1)
    
def create_address(to):
    return to+"<"+to.replace(" ","_")+"@eve.com>"

def CreateMessage(sender, to, subject, message_text,labelID,timestamp):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
    An object containing a base64 encoded email object.
    """
    tolist=";".join(to)
    message = MIMEText(message_text)
    message['to'] = tolist
    message['from'] = create_address(sender)
    message['subject'] = subject
    message.add_header('Date',utils.formatdate(timestamp))
    return {'raw': base64.urlsafe_b64encode(message.as_string()),'labelIds':[labelID]}

    

    
    
    
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.insert https://www.googleapis.com/auth/gmail.labels'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Evemail Uploader'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'evemailuploader.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print 'Storing credentials to ' + credential_path
    return credentials

    
def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    
    config = ConfigParser.RawConfigParser()
    config.read('mailloader.cfg')
    
    apiid=config.get('API','id')
    vcode=config.get('API','vcode')
    highestID=config.getint('EVEMAIL','highestid')
    newHighest=highestID
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    
    response = service.users().labels().list(userId='me').execute()
    labels = response['labels']
    labelID=''
    for label in labels:
        if label['name']==mailLabel:
            labelID=label['id']
    if labelID=='':
        print 'No label with the right name. Set one up'
        quit()
    
    
    eve = evelink.eve.EVE()
    api = evelink.api.API(api_key=(apiid, vcode))
    id_response = eve.character_id_from_name("Steve Ronuken")
    char = evelink.char.Char(char_id=id_response.result, api=api)
    evemails = char.messages()
    getMailList={}
    for mail in evemails.result:
        if mail['id']>highestID:
            if mail['id']>newHighest:
                newHighest=mail['id']
            getMailList[mail['id']]=mail
    config.set('EVEMAIL','highestid',newHighest)

    if newHighest==highestID:
        quit()

    mailBodies = char.message_bodies(getMailList.keys()).result
    
    mailingLists = char.mailing_lists().result
    
    
    for mailid in getMailList.keys():
        to=[]
        if getMailList[mailid]['to']['char_ids'] is not None:
            for charid in getMailList[mailid]['to']['char_ids']:
                to.append(create_address(eve.character_name_from_id(charid).result))
        if getMailList[mailid]['to']['org_id'] is not None:
            for orgid in getMailList[mailid]['to']['org_id']:
                to.append(create_address(eve.org_name_from_id(orgid).result))
        if getMailList[mailid]['to']['list_ids'] is not None:
            for listid in getMailList[mailid]['to']['list_ids']:
                to.append(create_address(mailingLists[listid]))
        
        title=getMailList[mailid]['title'].decode('utf-8')
        body=mailBodies[mailid].encode('ascii','ignore')
        body=remove_tags(body)
        name = eve.character_name_from_id(getMailList[mailid]['sender_id']).result
        message=CreateMessage(name,to,title,body,labelID,getMailList[mailid]['timestamp'])
        results = service.users().messages().insert(userId='me',body=message,internalDateSource='dateHeader').execute()

     
    if newHighest>highestID:
        with open('mailloader.cfg', 'wb') as configfile:
            config.write(configfile)

if __name__ == '__main__':
    main()
