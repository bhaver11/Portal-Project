import urllib2, base64
from bs4 import BeautifulSoup
import re
import time
import os
import sys
import yagmail
import csv
import csv

# with open('testfile.csv', newline='') as csvfile:
#     data = list(csv.reader(csvfile))

# print(data)




def sendEmail(newPosts):
    csvfile = open('mails.csv')
    receivers = list(csv.reader(csvfile))
    csvfile.close()
    body = "\n".join(newPosts)
    body = body.strip()
    subject = body.split("\n")[0]
    body += "\n\n\n Email Sent from Portal Project Developed by Bhaveshkumar Yadav"
    try:
        email = os.environ['EMAIL']
    except:
        print("Email not exported")
        print("Export using : 'export EMAIL=youremail'")
        sys.exit(1)
    try:
        emailPass = os.environ['EMAIL_PASS']
    except:
        print("Email Password not exported")
        print("Export using : 'export EMAIL_PASS=yourpass'")
        sys.exit(1)
    yag = yagmail.SMTP(email,emailPass)
    print(receivers)
    yag.send(
        to=receivers[0],
        subject=subject,
        contents=body, 
    )

lastPostIDs = []
newPosts = []
newPostCount = 0

def checkIfNewPost(req):
    global lastPostIDs
    global newPostCount
    global newPosts
    try:
        handle = urllib2.urlopen(req)
    except IOError:                 
        print ("It looks like the username or password is wrong.")
        sys.exit(1)
    thepage = handle.read()
    soup = BeautifulSoup(thepage, 'html.parser')
    posts = soup.find_all('div', attrs={'class',re.compile("post-*")})
    newPostCount = 0
    newPosts = []
    for post in posts:
        if(post['id'] in lastPostIDs):
            pass
        else:
            newPostCount += 1
            newPosts.append(post.text)
    if(newPostCount > 0):
        lastPostIDs = []    
        for post in posts:
            lastPostIDs.append(post['id'])

    return newPostCount

username = 'dummy'
password = 'dummy'
try:
    username = os.environ['LDAP']
except:
    print("Username not exported in environment")
    print("Export using : 'export LDAP=ldapusername'")
    sys.exit(1)
try:
    password = os.environ['LPASS']
except:
    print("Password not exported in environment")
    print("Export using : 'export LPASS=ldappassword'")
    sys.exit(1)

def getLastPosts():
    global lastPostIDs
    csvfile = open('posts.csv')
    
    lastPostIDs = list(csv.reader(csvfile))
    if(len(lastPostIDs)>0):
        lastPostIDs = lastPostIDs[0]
    csvfile.close()

def saveLastPosts(lastPostIDs):
    csvfile = open('posts.csv','w+')
    csvw = csv.writer(csvfile,delimiter=',')    
    csvw.writerow(lastPostIDs)

getLastPosts()


while(1):
    urll="http://placements.iitb.ac.in/blog/"

    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    req = urllib2.Request(urll)
    authheader =  "Basic %s" % base64string
    req.add_header("Authorization", authheader)

    if(checkIfNewPost(req)>0):
        print("sending emails")
        sendEmail(newPosts)
        saveLastPosts(lastPostIDs)
        # for posts in newPosts:
            # print(posts)
    time.sleep(300)


