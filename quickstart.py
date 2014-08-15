#!/usr/bin/env python
"""A simple script to download all Gmail emails with a given label.

This script will write a CSV file with the name passed to '--output-file'.
The CSV file will have the format:
   <sender domain name>,<email subject>,<email text>

The label you wish to download all emails from is provided with '--label'
and is the label name that you see in Gmail's web interface.

All functions labeled as 'example code' are copyright
by Google under the Apache 2.0 license. The docstrings
for those functions cite the specific sources for
those code samples.

All code that is not explicitly labeled as Google example code
is licensed under the MIT license, with James Mishra
(j@jamesmishra.com) as the copyright holder.
"""
from __future__ import print_function
import httplib2
import base64
import email
import unicodecsv
import unicodedata
import argparse
import sys
import re
from BeautifulSoup import BeautifulSoup
from lxml.html.clean import Cleaner
# The below imports are for the Gmail API.
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from apiclient import errors

# Allows the handling of very large CSV fields.
# May cause errors in some architectures.
unicodecsv.field_size_limit(sys.maxsize)


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


def get_raw_message_from_id(service, user_id, msg_id):
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
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ascii'))
        return msg_str
    except errors.HttpError, error:
        print("An error occured: %s" % error)


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
    Given a Python MIME message object, walk through the MIME
    multipart tree and concatenate all of the text we can find.
    Return this text.
    """
    text = ""
    for part in mime_msg.walk():
        payload = part.get_payload(decode=True)
        if payload is not None:
            text += " "
            text += payload
    return text


def fix_spaces_cr_lf(input_str):
    """
    Given an input string,
    remove HTML entity non-breaking spaces, carriage returns,
    and line feeds, replacing them all with spaces. Also,
    remove all consecutive spaces with one space. Finally,
    strip all whitespace on the ends of the string.
    """
    input_str = input_str.replace("&nbsp;", " ").replace("\r", " ")\
        .replace("\n", " ").strip()
    return " ".join(input_str.split()).strip()


URL_REGEX = re.compile(r'http.+? ', re.DOTALL)


def remove_urls(text):
    """
    Given a text string, return it without any URLs in it.
    """
    return re.sub(URL_REGEX, '', text)


#UNICODE_PUNCTUATION = dict.fromkeys(i for i in xrange(sys.maxunicode)
#                      if unicodedata.category(unichr(i)).startswith('P'))
#
#HTML_ENTITY_REGEX = re.compile(r'&[^\s]*;')


def remove_punctuation(text):
    return text
#    text = re.sub(HTML_ENTITY_REGEX, '', text)
#    return text.translate(UNICODE_PUNCTUATION)


def html_to_text(html_page_string):
    """
    Takes a full HTML document as a string and returns
    the text within the <body>
    """
    #return html_page_string
    # Stripts CSS from the HTML
    html_page_string = Cleaner(style=True).clean_html(html_page_string)
    # Now we strip everything else...
    # BeautifulSoup is unable to strip CSS <style> tags by
    # itself, so that's why Cleaner helps out.
    soup = BeautifulSoup(html_page_string)
    # Concatenate all of the text in tags, and then remove
    # all of the embedded URLs.
    return remove_urls(" ".join(soup.findAll(text=True)))


def save_str_to_csv(raw_msg, output_file, append=True):
    """
    Takes a single Python string (`raw_msg`) and saves it
    to a one-row-wide CSV file with the filename `output_file`.
    """
    if append:
        mode = "a"
    else:
        mode = "w"
    with open(output_file, mode) as handle:
        writer = unicodecsv.writer(handle, quoting=unicodecsv.QUOTE_ALL)
        writer.writerow([raw_msg])


def process_raw_msg(raw_msg, formatted_output_file, append=True):
    """
    Given a Python list of raw messages and an output CSV file
    to write to, write details of the messages out to the CSV
    file in the format:
        <sender-domain>,<subject>,<message-text>
    """
    if append:
        mode = "ab"
    else:
        mode = "wb"
    mime_msg = email.message_from_string(raw_msg)
    text = remove_punctuation(html_to_text(concat_email_text(mime_msg)))
    subject = mime_msg.get("Subject")
    # Decode escaped character sets in the subject line
    subject = u" ".join([a[0].decode('utf-8', 'replace')
                         for a in email.header.decode_header(subject)])
    subject = remove_punctuation(subject.replace("\r", " ").replace("\n", " "))
    sender_domain = mime_msg.get("From").split("@")[1].split(">")[0]#\
                                                      #.decode("utf-8")
    # Strip whitespace
    csv_line = [fix_spaces_cr_lf(s) for s in [sender_domain, subject, text]]
    # If any of our strings are empty, replace with a placeholder
    # to make sure each CSV line has three items.
    csv_line = map(lambda s: (u'' == s) and u"PLACEHOLDERNONE" or s ,
                   csv_line)
    if formatted_output_file == "STDOUT":
        writer = unicodecsv.writer(sys.stdout,
                                 quoting=unicodecsv.QUOTE_ALL)
        writer.writerow(csv_line)
    else:
        with open(formatted_output_file, mode) as handle:
            writer = unicodecsv.writer(handle,
                                   quoting=unicodecsv.QUOTE_ALL)
            writer.writerow(csv_line)


def make_argparser():
    """
    Configures and returns an ArgumentParser object
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-file', type=str, required=True, help=
                        """The file to write CSV output in. Type 'STDOUT' for
                        output to standard output. Setting 'STDOUT' will
                        trigger '--quiet'""")
    parser.add_argument('--label', type=str, required=True, help=
                        """The name of the Gmail label that contains all of the
                        emails you wish to download""")
    parser.add_argument('--quiet', action='store_true', help=
                        """Keep error messages quiet""")
    parser.add_argument('--download-only', action='store_true', help=
                        """Downloads emails and writes *raw* MIME email messages
                        to the output file. This option is useful in conjunction
                        with '--import-raw' for repeated debugging of this
                        program without downloading the same messages over
                        and over again from the Internet.

                        This parameter is also useful in the event you want
                        the raw MIME emails without any customization.

                        The output filename does not change with this
                        parameter, but the CSV format just becomes
                        one column containing the entire MIME string.

                        One thing to worry about is that some programs
                        might return errors with the extremely long CSV fields
                        created by this format.""")
    parser.add_argument('--import-raw', type=str, default='', help=
                        """Imports a CSV file created by the '--download-only'
                        parameter.""")
    parser.add_argument('--user', type=str, default='me', help=
                        """A different username to send to the Gmail API.
                        The default value is 'me', which the Gmail API
                        interprets as the authenticated user.""")
    return parser


def quiet_print_maker(quiet):
    """
    Creates a custom print function that is silent if quiet=True.

    This is a cheap way to enable/disable all debug output at once.
    """
    if quiet:
        return lambda *x: None
    else:
        return print

def main():
    # The next two lines are a common hack for enabling UTF-8
    # support in Python 2. They're generally *not* recommended,
    # but this avoids UnicodeEncodeErrors and UnicodeDecodeErrors
    # when passing strings in and around third party libraries.
    #
    # This isn't a shortcut for true Unicode support, so don't
    # use this hack in production.
    reload(sys)
    sys.setdefaultencoding("utf-8")
    args = make_argparser().parse_args()
    # If we are writing CSV output to standard output,
    # then we don't want it clouded up with progress output.
    if args.output_file == "STDOUT":
        args.quiet = True
    qp = quiet_print_maker(args.quiet)
    if args.import_raw:
        qp("Importing stored messages")
        count = 1
        with open(args.import_raw, 'r') as handle:
            reader = unicodecsv.reader(handle, errors='replace')
            for raw_msg in reader:
                raw_msg = raw_msg[0]
                process_raw_msg(raw_msg, args.output_file)
                print("Processed", count)
                count += 1
    else:
        # The first time the program runs, the user will have to authenticate
        # using a web browser. After that, the credentials will be stored.
        gmail_service = auth()
        label = get_label_id_from_name(gmail_service, args.user, args.label)
        msg_id_list = list_messages_with_label(gmail_service, args.user,
                                               [label])
        num_msgs = len(msg_id_list)
        qp("Total messages:", num_msgs)
        count = 1
        for msg in msg_id_list:
            raw = get_raw_message_from_id(gmail_service, args.user, msg['id'])
            if args.download_only:
                save_str_to_csv(raw, args.output_file)
            else:
                process_raw_msg(raw, args.output_file)
            qp("Processed", count, "of", num_msgs)
            count += 1


if __name__ == "__main__":
    main()
