# University Marketing Email Analysis

## Introduction
Institutions of higher learning send thousands of marketing emails to high
school students as soon as those students' emails appear in various
databases listing prospective university attendees.

I collected over 3000 such marketing emails from January 2011 to January
2013, and this a project to analyze the strategies used by
these marketers in selling their institutions to prospective
students.

## Area of Analysis

### Natural Language Analysis

What sort of language do these marketers use when advertising their
school to prospective students? What words appear frequently?
What words are certain schools more likely to use than others?
Can this detail be used to develop a statistical model
of how to write like a university marketer, or to predict
which university a specific email body came from?

**Current state**: Incomplete. In progress.

### Frequency Analysis

What is the difference between a university that sends many
emails and a university that sends few emails? Are there
correlations between the number of emails a university sends
a student and 

**Current state**: Incomplete. In progress.

### Timing Analysis

What time of day are these emails sent? Are they sent during a time
of day when the marketers expect them to be most likely to be read?

What time of the year are these emails sent? Anecdotally, I saw
a trickle of these emails in January 2011, when I was a tenth
grader, and this trickle gradually intensified as I reached
the twelfth grade, and then trickled off again as application
deadlines had passed and high school graduation approached.

**Current state**: Not started.


## Technical Details

### Python

The Python script `download_gmail.py` uses the Gmail API
(accessed through the Python Google API library) to download
all of the emails in a user-selected Gmail label.

The emails are pulled from Google in raw MIME format,
and then heavily processed to turn rich multipart HTML
emails into flat text messages, at which point they're
written out to a CSV file.

### Wolfram Mathematica

To visualize and do more advanced processing on this
data, we use Wolfram Mathematica. In addition to
Mathematica's powerful general-purpose computing
language, it's strong visualization features make
it easy to create publication-worthy graphs
from the raw CSV data.

## Possible Flaws in Methodology

### n=1 sample size
Although many universities are represented in the sample,
all 3000+ emails are only targeting one specific student.

It is entirely possible that a student of a different gender,
race, academic standing, and/or geographical location would
receive a different pool of emails from the universities
interested in them. Because of this, it may be difficult
to draw very specific conclusions about the marketing
techniques of universities.

### Imperfect Collection Method

It is entirely possible that between January 2011 and January 2013
(when I was collecting the emails for this study) that not all 
of the college marketing emails I received were appropriately
categorized. Some of them may be elsewhere in my inbox, marked as
spam, or otherwise lost.

Additionally, it is very possible that emails that are not from
college marketers (or are tainted by having specific user interaction
with the college--such as applying to them) made it into the
dataset. Although an effort has been made to sanitize the dataset,
nobody can ever be perfectly certain...

## Frequently Asked Questions

**Where can I download the marketing emails used in this analysis?**

You can't... yet. With a little bit more post-processing, and some
checking over to make sure that I am not accidentally publishing
one or two important emails in the dataset of 3000+ emails,
it will be available for download shortly.

If you want a copy of these emails for private analysis, then
send me an email at j@jamesmishra.com
