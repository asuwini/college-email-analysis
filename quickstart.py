#!/usr/bin/python
"""
This is a piece of example code pulled from
https://developers.google.com/gmail/api/quickstart/quickstart-python

It is copyright by Google under the Apache 2.0 License.
"""
import httplib2

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from apiclient import errors


def auth():
    """
    Return an authenticated Gmail service.

    Based on example code from Google's website.
    """
    # Path to the client_secret.json file downloaded from the Developer Console
    CLIENT_SECRET_FILE = 'client_secret.json'
    OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'

    # Location of the credentials storage file
    STORAGE = Storage('gmail.storage')
    # Start the OAuth flow to retrieve credentials
    flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
    http = httplib2.Http()

    # Try to retrieve credentials from storage or run the flow to generate them
    credentials = STORAGE.get()
    if credentials is None or credentials.invalid:
        credentials = run(flow, STORAGE, http=http)
    # Authorize the httplib2.Http object with our credentials
    http = credentials.authorize(http)

    # Build the Gmail service from discovery
    gmail_service = build('gmail', 'v1', http=http)
    return gmail_service


def get_threads(gmail_service):
    """
    Takes an authenticated Gmail service and returns a list of email thread IDs.
    """
    # Retrieve a page of threads
    threads = gmail_service.users().threads().list(userId='me').execute()
    # Print ID for each thread
    if threads['threads']:
        for thread in threads['threads']:
          print 'Thread ID: %s' % (thread['id'])


def list_labels(service, user_id):
    """
	Get a list all labels in the user's mailbox.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.

    Returns:
        A list all Labels in the user's mailbox.
    """
    try:
        response = service.users().labels().list(userId=user_id).execute()
        labels = response['labels']
        return labels
    except errors.HttpError, error:
        print 'An error occurred: %s' % error


def list_messages_with_label(service, user_id, label_ids=[]):
    """
    List all Messages of the user's mailbox with label_ids applied.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        label_ids: Only return Messages with these labelIds applied.

    Returns:
        List of Messages that have all required Labels applied. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate id to get the details of a Message.
    """
    try:
        response = service.users().messages().list(userId=user_id,
                   labelIds=label_ids).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id,
                       labelIds=label_ids, pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except errors.HttpError, error:
        print 'An error occurred: %s' % error

def main():
    gmail_service = auth()
    print list_labels(gmail_service, "me")
    #print list_messages_with_label(auth(), "me", "SENT")

if __name__ == "__main__":
    main()
