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
# 	    python secret_santa.py -s
#       python secret_santa.py --send
#
#   finally, as much as i appreciate the sentiment (<3) please don't send me any
# secret santa e-mails, i'm already in enough of 'em!
#

email_details = {
# details needed to connect to an e-mail server (here i use gmail, you can use
# w/e you want!)
"Host"     : "smtp.gmail.com:587",
"Username" : "thatbrod",
"Password" : "****************",

# details sent out to the secret santas
"Subject" : "Secret Santa 2014~",
"Message" : '''HO HO HO! This year, you are ${SANTEE}'s Secret Santa! The \
spending limit is $50, and we plan on exchanging gifts Christmas night! \
Have fun and stay sneaky!!''',
# note: ${SANTEE} will be replaced w/ the santee's name!
}
participants = [
    { "Name" : "Bippo", "E-Mail" : "bippo@neat.za" }, #idx 0
    { "Name" : "Brian", "E-Mail" : "brian@cool.ze" }, #idx 1
    { "Name" : "Binne", "E-Mail" : "binne@mint.zi" }, #idx 2
    { "Name" : "Boogy", "E-Mail" : "boogy@whoa.zo" }, #idx 3
    { "Name" : "Bavin", "E-Mail" : "bavin@word.zu" }, #idx 4
#   {                                              }, #idx ...
]
bad_pairs = {
	("Santa's IDX", "Santee's IDX"),

	(0, 2), # Bippo and Binne are happily married! We don't need to tell them
	(2, 0), # to get each other something!

	(0, 1), # Bippo got Brian something last year!
}
# don't worry about people getting paired with themselves, the script already
# knows that's not allowed!



# Don't change anything after this unless you know what you're doing! And most
# important of all: HAPPY HOLIDAYS!! o<(:-D)
import collections
import itertools
import random
import smtplib
import sys

def bijections_of(collection, relations):
	mapping = collections.defaultdict(list)
	bijections = []

	for lhs, rhs in relations:
		if lhs in set(collection) and rhs in set(collection):
			mapping[lhs].append(rhs)

	if len(mapping) != len(collection) or len(set(itertools.chain.from_iterable(mapping.values()))) != len(collection):
		return []

	for rhs_permutation in (list(rhs_values) for rhs_values in itertools.product(*mapping.values())):
		if len(set(rhs_permutation)) == len(collection):
			bijections.append(list(zip(mapping.keys(), rhs_permutation)))

	return bijections

def id_to_name((santa_id, santee_id)):
	return (participants[santa_id]["Name"], participants[santee_id]["Name"])

def send_email(santa, santee, server):
	santa_details = participants[santa]
	santee_details = participants[santee]

	msg = "\r\n".join([
		"From: Santa <santa@northpole.com>",
		"To: " + santa_details["Name"] + " <" + santa_details["E-Mail"] + ">",
		"Subject: " + email_details["Subject"],
		"",
		email_details["Message"].replace("${SANTEE}", santee_details["Name"])
	])

	server.sendmail("santa@northpole.com", santa_details["E-Mail"], msg)



idx = range(len(participants))
good_pairs = list( set(itertools.product(idx, idx)) - set(zip(idx, idx)) - bad_pairs )
potential_matches = bijections_of(idx, good_pairs)
if not potential_matches:
	print("the set of `bad_pairs' is too restrictive! No matches are possible!")
	sys.exit()
matches = random.choice(potential_matches)

if len(sys.argv) > 1 and (sys.argv[1] == "-s" or sys.argv[1] == "--send"):
	server = smtplib.SMTP(email_details["Host"])
	server.starttls()
	server.login(email_details["Username"], email_details["Password"])
	for santa, santee in sorted(matches):
		print(participants[santa]["Name"] + " is now being sent their e-mail...")
		send_email(santa, santee, server)
	server.quit()
	print("done! happy gift hunting!")
else:
	print(map(id_to_name, matches))
