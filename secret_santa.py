#!/usr/bin/python
#
# script: secret_santa.py
# author: Brian Rodriguez (`thatbrod@gmail.com' for any questions!)
# last-modified: 6 December 2014
#
#   fun little script that auto-magically pairs the given participants together
# randomly with an optional set of restrictions.
#
#   to actually send an e-mail out, you have to use the flag -s or --send,
# otherwise, the script will just print out an example of who it matches.
#
#   so send the message like this:
#       python secret_santa.py -s
#       python secret_santa.py --send
#
#   finally, as much as i appreciate the sentiment (<3) please don't send me any
# secret santa e-mails, i'm already in enough of 'em!
#

email_details = {
# details needed to connect to an e-mail client (here i use gmail, you can use
# w/e you want!)
"Host"     : "smtp.gmail.com:587",
"Username" : "thatbrod",
"Password" : "************************************************************",

# details sent out to the secret santas
"Subject" : "Secret Santa 2014~",
"Message" : '''HO HO HO! This year, you are ${SANTEE}'s Secret Santa! The \
spending limit is $50, and we plan on exchanging gifts Christmas night! Have \
fun!! :)''',
# note: ${SANTEE} will be replaced w/ the santee's name!
}

# the script is kinda dumb, so each participant needs to have a UNIQUE name. it
# won't check for you and will give you broken results if you force it to run :/
# sorry if this is a problem, if anyone actually cares enough to e-mail me about
# it, i'll whip up a fix m'kay?
participants = [
	{ "Name" : "Brile", "E-Mail" : "brile@mint.oh" },
	{ "Name" : "Binni", "E-Mail" : "binni@whoa.yo" },
	{ "Name" : "Boope", "E-Mail" : "boope@neat.qt" },
	{ "Name" : "Boogy", "E-Mail" : "boogy@what.up" },
	{ "Name" : "Brian", "E-Mail" : "brian@cool.og" },
]

bad_pairs = {
	("Santa", "Santee"),

	("Brile", "Boogy"), # Brile got Boogy something last year!

	("Boope", "Binni"), # happily married, we don't need to tell them to get
	("Binni", "Boope"), # each other presents :P
}
# don't worry about people getting paired with themselves, the script already
# knows that's not allowed!



# Don't change anything after this unless you know what you're doing! And most
# important of all: HAPPY HOLIDAYS!! o<(:-D)

from collections import defaultdict
from itertools import product, chain
from random import choice
from smtplib import SMTP
from sys import argv, exit



def bijections_of(collection, relations):
	mapping = defaultdict(list)
	bijections = []

	for lhs, rhs in relations:
		if lhs in set(collection) and rhs in set(collection):
			mapping[lhs].append(rhs)

	if len(mapping) != len(collection) or len(set(chain.from_iterable(mapping.values()))) != len(collection):
		return []

	for rhs_permutation in (list(rhs_values) for rhs_values in product(*mapping.values())):
		if len(set(rhs_permutation)) == len(collection):
			bijections.append(list(zip(mapping.keys(), rhs_permutation)))

	return bijections

def send_email(santa, santee, server):
	santa_details = next(details for details in participants if details["Name"] == santa)

	msg = "\r\n".join([
		"From: Santa <santa@northpole.com>",
		"To: " + santa_details["Name"] + "<" + santa_details["E-Mail"] + ">",
		"Subject: " + email_details["Subject"],
		"",
		email_details["Message"].replace("${SANTEE}", santee)
		])

	server.sendmail("santa@northpole.com", santa_details["E-Mail"], msg)



names = [ person["Name"] for person in participants ]
good_pairs = list( set(product(names, names)) - set(zip(names, names)) - bad_pairs )
potential_matches = bijections_of(names, good_pairs)

if not potential_matches:
	print("the set of `bad_pairs' is too restrictive! No matches are possible!")
	exit()

matches = choice(potential_matches)

if len(argv) > 1 and (argv[1] == "-s" or argv[1] == "--send"):
	server = SMTP(email_details["Host"])
	server.starttls()
	server.login(email_details["Username"], email_details["Password"])

	for santa, santee in sorted(matches):
		print(santa + " is now being sent their e-mail...")
		send_email(santa, santee, server)

	server.quit()
	print("done! happy gift hunting!")

else:
	print(matches)
