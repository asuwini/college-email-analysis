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

**Current state**: In progress

### Timing

What time of day are these emails sent? Are they sent during a time
of day when the marketers expect them to be most likely to be read?

What time of the year are these emails sent? Anecdotally, I saw
a trickle of these emails in January 2011, when I was a tenth
grader, and this trickle gradually intensified as I reached
the twelfth grade, and then trickled off again as application
deadlines had passed and high school graduation approached.

**Current state**: Incomplete

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
