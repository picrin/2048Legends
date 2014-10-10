#encoding: UTF-8
import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WC2048.settings")
from website import queries

message = "\
These links are super-important, so pay attention!\r\n\
\r\n\
1) All the hackathon challenges (along with descriptions and video) can be accessed at:\r\n\
https://drive.google.com/folderview?id=0BxOgqlGwvS44TTV3WkJJT291bUE&usp=sharing\r\n\
\r\n\
2) MLH will reimburse travel expenses up to £40 for all of you who are coming to the hack from outside of Glasgow. You just need to fill in this google form:\r\n\
https://docs.google.com/forms/d/1iCGf98GHqotr3onPxINjllZ78gCcBNFpdnwW8yQcgKY/viewform\r\n\
\r\n\
3) 100$ Amazon Web Services credit is up for grabs for the first 120 people! Go to\r\n\
https://aws.amazon.com/activate/event/gutshackathon/\r\n\
and register in the right pane for your 100$ credit.\r\n\
\r\n\
4) 2048wc.com is a mini-challenge, which can make any of you 25 GBP richer. Just go to 2048wc.com and see yourself!\n\
Your individual login and password are:\r\n\
"


import smtplib
import random
with open("emails.txt") as emails:
    for line in emails.readlines():
        if line[-1] == "\n":
            line = line[0:-1]
        if line[-1] == ",":
            line = line[0:-1]
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.ehlo()
        session.starttls()
        session.login("gutechsoc@gmail.com", "europeansoyuz")

        headers = "\r\n".join(["from: " + "gutechsoc@gmail.com",
                               "subject: " + "GUTS Hackathon Pack",
                               "to: " + line,
                               "mime-version: 1.0",
                               "content-type: text/plain"])
        login = line.split("@")[0] + str(random.randint(0,1000))
        password = "".join(random.sample("abcdefghijklmnoprstuwxyz1234567890", 10))
        content = headers + "\r\n\r\n" + message + "login: " + login  + "\r\n" + "password: " + password
        content += "\r\n\r\nHave a good hack,\r\nGUTS team"
        session.sendmail("gutechsoc@gmail.com", line, content)
        queries.create_user_simple(login, password)

