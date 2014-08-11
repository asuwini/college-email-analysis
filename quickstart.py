#!/usr/bin/python
"""
All functions labeled as 'example code' are copyright
by Google under the Apache 2.0 license. The docstrings
for those functions cite the specific sources for
those code samples.
"""
from __future__ import print_function
import httplib2
import base64
import email
import unicodecsv
import sys
from BeautifulSoup import BeautifulSoup
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from apiclient import errors

def stderr(*args):
    """
    Convert arguments to string and print them to stderr
    """
    print(" ".join(str(a) for a in args), file=sys.stderr)


def auth():
    """
    Return an authenticated Gmail service.

    Based on example code from
    https://developers.google.com/gmail/api/quickstart/quickstart-python
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

    Based on example code from Google's website.
    """
    # Retrieve a page of threads
    threads = gmail_service.users().threads().list(userId='me').execute()
    # Print ID for each thread
    if threads['threads']:
        for thread in threads['threads']:
          print('Thread ID: %s' % (thread['id']))


def list_labels(service, user_id):
    """
	Get a list all labels in the user's mailbox.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.

    Returns:
        A list all Labels in the user's mailbox.

    Based on example code from
    https://developers.google.com/gmail/api/v1/reference/users/labels/list
    """
    try:
        response = service.users().labels().list(userId=user_id).execute()
        labels = response['labels']
        return labels
    except errors.HttpError, error:
        print('An error occurred: %s' % error)


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

    Based on example code from
    https://developers.google.com/gmail/api/v1/reference/users/messages/list
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
        print('An error occurred: %s' % error)


def get_message_from_id(service, user_id, msg_id):
    """Get a Message with given ID.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: The ID of the Message required.

    Returns:
        A Message.

    Based on example code from
    https://developers.google.com/gmail/api/v1/reference/users/messages/get
    """
    try:
        message = service.users().messages().get(
            userId=user_id, id=msg_id).execute()
        return message
    except errors.HttpError, error:
        print('An error occurred: %s' % error)


def get_mime_message_from_id(service, user_id, msg_id):
    """Get a Message and use it to create a MIME Message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: The ID of the Message required.

    Returns:
        A MIME Message, consisting of data from Message.

    Based on example code from
    https://developers.google.com/gmail/api/v1/reference/users/messages/get
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id,
                                                 format='raw').execute()
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

        mime_msg = email.message_from_string(msg_str)

        return mime_msg
    except errors.HttpError, error:
        print('An error occurred: %s' % error)


def get_label_id_from_name(service, user, label_name):
    """
    Given an authenticated Gmail service, user, and a label name
    (visible in Gmail), find the internal label ID.

    This function returns False if the given label name was
    not found.
    """
    labels = list_labels(service, user)
    for label in labels:
        if label['name'] == label_name:
            return label['id']
    else:
        return False

def concat_email_text(mime_msg):
    """
    if mime_msg.is_multipart():
        sub_messages = mime_msg.get_payload(decode=True)
        if sub_messages is not None:
            return "\n".join(concat_email_text(msg) for msg in sub_messages)
        else:
            return mime_
    else:
        return mime_msg.get_payload(decode=True)
    """
    text = ""
    for part in mime_msg.walk():
        payload = part.get_payload(decode=True)
        if payload is not None:
            text += "\n"
            text += payload
    return text


def html_to_text(html_page_string):
    """
    Takes a full HTML document as a string and returns
    the text within the <body>
    """
    soup = BeautifulSoup(html_page_string)
    # `separator=" "` replaces `<br>` tags with " "
    # preventing `James<br>Mishra` from being turned into
    # `JamesMishra`
    if soup.body is not None:
        text = soup.body.getText(separator=" ")
    else:
        text = soup.getText(separator=" ")
    # Remove all non-breaking spaces with regular ones
    text = text.replace("&nbsp;", " ")
    # Remove multiple spaces with single spaces
    return " ".join(text.split())


def main():
    if len(sys.argv) > 1:
        OUTPUT_CSV_FILE = sys.argv[1]
    else:
        OUTPUT_CSV_FILE = "output.csv"
    gmail_service = auth()
    label = get_label_id_from_name(gmail_service, "me", "College spam")
    messages = list_messages_with_label(gmail_service, "me", [label])
    for msg in messages:
        mime_msg = get_mime_message_from_id(gmail_service, "me", msg['id'])
        try:
            text = html_to_text(concat_email_text(mime_msg))
        except UnicodeEncodeError:
            stderr("Skipping an email")
            stderr("Subject line", mime_msg.get("Subject"))
            continue
        subject = mime_msg.get("Subject")
        sender_domain = mime_msg.get("From").split("@")[1].split(">")[0]
        csv_line = [sender_domain, subject, text]
        with open(OUTPUT_CSV_FILE, 'a') as handle:
            writer = unicodecsv.writer(handle)
            writer.writerow(csv_line)
if __name__ == "__main__":
    main()
