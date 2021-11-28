import urllib, base64
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
        subject = body.find('h3',attrs={'class','entry-title'}).text
        # subject = str(body.text.strip().split('\n')[0])
        body = str(body)
        body = re.sub(r'\n\s*\n', '\n\n', body)
        body += "\n\n\nEmail Sent from Portal Project \n Author: Bhaveshkumar Yadav \n More info at : https://github.com/bhaver11/Portal-Project"
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
        handle = urllib.request.urlopen(req)
    except urllib.error.URLError as e:                 
        print("Error")
        print(e)
        time.sleep(300)
        return 0
    thepage = handle.read()
    soup = BeautifulSoup(thepage, 'html.parser')
    posts = soup.find_all('article', attrs={'class',re.compile("post-*")})
    # print(posts)
    newPostCount = 0
    newPosts = []
    for post in posts:
        postId = post['id']
        postH = post.find('h3',attrs={'class','entry-title'}).text
        # postH = post.text.strip().split('\n')[0]
        print(postH)
        if(str(postId+postH) in lastPostIDs):
            pass
        else:
            newPostCount += 1
            newPosts.append(post)
    if(newPostCount > 0):
        lastPostIDs = []    
        for post in posts:
            postId = post['id']
            postH = post.find('h3',attrs={'class','entry-title'}).text
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
urll="https://campus.placements.iitb.ac.in/blog/placement"
# data_string = username+":"+password
# data_bytes = data_string.encode("utf-8")
# base64string = base64.b64encode(data_bytes)
# authheader =  "Basic %s" % base64string
# print(authheader)

# authheader =  "Basic %s" % base64string
# req.add_header("Authorization", authheader)
# create a password manager
password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()

# Add the username and password.
# If we knew the realm, we could use it instead of None.
top_level_url = urll
password_mgr.add_password(None, top_level_url, username, password)

handler = urllib.request.HTTPBasicAuthHandler(password_mgr)

# create "opener" (OpenerDirector instance)
opener = urllib.request.build_opener(handler)

# use the opener to fetch a URL
opener.open(urll)

# Install the opener.
# Now all calls to urllib.request.urlopen use our opener.
urllib.request.install_opener(opener)
req = urllib.request.Request(urll)

while(1):
    print("Checking for new posts")
    if(checkIfNewPost(req)>0):
        print("sending emails")
        sendEmail(newPosts)
        saveLastPosts(lastPostIDs)
    else:
        print("No new posts found")
    print("Sleeping...")
    time.sleep(180)


