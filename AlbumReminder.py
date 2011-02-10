#!/usr/bin/python2

# AlbumReminder.py: Reads ~/bands and reminds you of new albums
# Copyright 2011, Austin Pocus. See LICENSE for details.

import re
import datetime
import os
import sys
import socket
import smtplib

class Album:
    def __init__(self, artist, date):
	self.artist = artist
	self.date = date

	# check for a full date (mm/dd/yyyy)
	match = re.search('^(\d{2})/(\d{2})/(\d{4})$', date)
	if match:
	    (self.month, self.day, self.year) = [int(m) for m in match.groups()]
	    return
	# try a month and year (mm/yyyy)
	match = re.search('^(\d{2})/(\d{4})$', date)
	if match:
	    (self.month, self.year) = [int(m) for m in match.groups()]
	    self.day = 0
	    return

	# or just a year (yyyy)
	match = re.search('^(\d{4})$', date)
	if match:
	    self.year = [int(m) for m in match.groups()]
	    self.day = self.month = 0
	    return
	else:
	    pass
	
    def is_coming_soon(self):
	now = datetime.datetime.now()
	if (self.year == now.year and 
	    self.month == now.month):
	    return True
	else:
	    return False

fname = os.environ['HOME'] + '/bands'
def file_to_albums(fname):
    fd = open(fname)
    entries = [line.rstrip() for line in fd]

    # strip the ending \n, if needed
    if entries[-1] == '':
	entries.pop()

    albums = []
    for entry in entries:
	(artist, date) = entry.split(': ')
        albums.append(Album(artist, date))

    return albums

sender = os.getlogin() + "@" + socket.gethostname() + ".localdomain"
to = sys.argv[1]
albums = file_to_albums(fname)
monthly = []
for album in albums:
    if album.is_coming_soon():
	if album in monthly:
	    monthly.pop(album)

	artist = album.artist
	date = album.date

	if album.day == 0:
	    day = ""
	else:
	    day = str(album.day)

	text = "%s is coming soon: %s" % (artist, date)
	mailer = smtplib.SMTP('localhost')
	mailer.sendmail(sender, [to], text)
	mailer.quit()

    else:
	monthly.append(album)

# monthly list is mailed on the first of the month
now = datetime.datetime.now()
if now.day == 1:
    text = ("Wake up,\r\n" * 3) + "It's the first of the month!\r\n"
    for album in monthly:
	text += "%s: %s\r\n" % (album.artist, album.date)

    mailer = smtplib.SMTP('localhost')
    mailer.sendmail(sender, [to], text)
    mailer.quit()

