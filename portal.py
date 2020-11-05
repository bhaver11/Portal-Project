import urllib2, base64
from bs4 import BeautifulSoup
import re
import time
import os
import sys
import yagmail
import csv


def sendEmail(newPosts):
    csvfile = open('mails.csv')
    receivers = list(csv.reader(csvfile))
    csvfile.close()
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
    for newPost in newPosts:
        body = newPost
        subject = body.split("\n")[0]
        body += "\n\n\nEmail Sent from Portal Project \n Developed by Bhaveshkumar Yadav \n More info at : https://github.com/bhaver11/Portal-Project"
        try:
            yag.send(
                to=receivers[0],
                subject=subject,
                contents=body, 
            )
        except:
            try:
                print("Failed to send email, sending only subject")
                print(subject)
                newsubject = "New update on placement blog"
                yag.send(
                    to=receivers[0],
                    subject=newsubject,
                    contents=body, 
                )
            except:
                print("Failed to send email with subject:")
                print(subject)
                yag.send(
                    to="bhaveshy11@gmail.com",
                    subject="Failed to send email",
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
        print ("It looks like the username or password is wrong, or the site is down")
        time.sleep(300)
        return 0
    thepage = handle.read()
    soup = BeautifulSoup(thepage, 'html.parser')
    posts = soup.find_all('div', attrs={'class',re.compile("post-*")})
    newPostCount = 0
    newPosts = []
    for post in posts:
        postId = post['id'].encode('utf-8')
        postH = post.text.encode('utf-8').strip().split('\n')[0]
        if(postId+postH in lastPostIDs):
            pass
        else:
            newPostCount += 1
            newPosts.append(str(post.text.encode('utf-8').strip()))
    if(newPostCount > 0):
        lastPostIDs = []    
        for post in posts:
            postId = post['id'].encode('utf-8')
            postH = post.text.encode('utf-8').strip().split('\n')[0]
            lastPostIDs.append(str(postId+postH))

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
    csvfile.close()

getLastPosts()
print("Running the portal blog sniffer")
urll="http://placements.iitb.ac.in/blog/"
base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
req = urllib2.Request(urll)
authheader =  "Basic %s" % base64string
req.add_header("Authorization", authheader)

while(1):
    print("Checking for new posts")
    if(checkIfNewPost(req)>0):
        print("sending emails")
        sendEmail(newPosts)
        saveLastPosts(lastPostIDs)
    else:
        print("NO new posts found")
    print("Sleeping...")
    time.sleep(180)


