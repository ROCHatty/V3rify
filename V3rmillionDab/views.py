"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, abort, request, session
from V3rmillionDab import app
import cloudscraper
from bs4 import BeautifulSoup
from lxml import html
import json
import random
import string
from datetime import date

app.secret_key = b'\x97\xd6\x7f[a\x01\xd3\x0bF%\x130\xb3\xff\x9f\xe9'

scraper = cloudscraper.create_scraper(allow_brotli=False)
sitedata = []
savefile = 'V3rmillionDab/info.json'
currentlink = 'http://localhost:8080'
secretkey = '6LduYeEUAAAAAGSY71aBZb158Q6T7NEMSm9F8rbq'

def savedata():
    global sitedata
    global savefile
    with open(savefile, 'w') as filehandle:
        json.dump(sitedata, filehandle)
def loaddata():
    global sitedata
    global savefile
    with open(savefile, 'r') as filehandle:
        sitedata = json.load(filehandle)

loaddata()

@app.route('/', methods=["GET"])
@app.route('/home', methods=["GET"])
def home():
    global currentlink
    return render_template('index.html', currentlink=currentlink)

@app.route('/share/<int:id>')
def share(id):
    dab = "ol"

@app.route('/vermillion/profile/<int:id>', methods=["POST"])
def getprofile(id):
    global scraper
    dab = scraper.get("https://v3rmillion.net/member.php?action=profile&uid="+str(id)).text
    if "You are either not logged in or do not have permission to view this page" in dab:
        # Not logged in
        dab = scraper.post("https://v3rmillion.net/member.php", data = {"action": "do_login", "url": "/member.php?action=profile&uid="+str(id), "username": "hattorius", "password": "22Augustus2002!", "code": "", "remember": "yes", "_challenge": ""}).text
    dab = scraper.get("https://v3rmillion.net/member.php?action=profile&uid="+str(id)).text
    tree = html.fromstring(dab)
    joined = dab.split('Joined:</strong></td>')[1].split('>')[1].split('<')[0]
    posts = int(dab.split('Total Posts:</strong></td>')[1].split('>')[1].split('<')[0].split(' ')[0])
    threads = int(dab.split('Total Threads:</strong></td>')[1].split('>')[1].split('<')[0].split(' ')[0])
    reputation = int(dab.split('Reputation:</strong></td>')[1].split('<td class="trow1">')[1].split('>')[1].split('<')[0])
    bio = dab.split('Bio:</strong></td>')[1].split('>',1)[1].split('</td>')[0]
    return {"joined": joined, "posts": posts, "threads": threads, "reputation": reputation, "bio": bio}

@app.route('/api/profile/<int:id>/<int:pid>', methods=["POST"])
def checkaccess(id, pid):
    global sitedata
    if pid == session['post'] and session['state'] == 1:
        postdata = sitedata[pid]
        memberdata = getprofile(id)
        if session['verify'] not in memberdata['bio']:
            return {"success":False, "message": "The verification code hasnt been added to your bio!"}
        regdate = memberdata['joined'].split('-')
        delta = date.today() - date(int(regdate[2]), int(regdate[0]), int(regdate[1]))
        if postdata['days'] == 0 or postdata['days'] <= delta.days:
            if postdata['posts'] == 0 or postdata['posts'] <= memberdata['posts']:
                if postdata['threads'] == 0 or postdata['threads'] <= memberdata['threads']:
                    if postdata['reputation'] == 0 or postdata['reputation'] <= memberdata['reputation']:
                        session['state'] = 2
                        return {"success": True}
                    else:
                        return {"success": False, "message": "You need atleast "+str(postdata['reputation'])+" reputation to see this post!"}
                else:
                    return {"success": False, "message": "You need atleast "+str(postdata['threads'])+" threads to see this post!"}
            else:
                return {"success": False, "message": "You need atleast "+str(postdata['posts'])+" posts to see this post!"}
        else:
            return {"success": False, "message": "your account has to be atleast "+str(postdata['days'])+" days old!"}
    session.pop('post', None)
    session.pop('state', None)
    session.pop('verify', None)
    return {"success": False, "message": "Something went wrong!"}

@app.route('/api/new', methods=["POST"])
def create():
    global sitedata
    postdata = json.loads(request.data.decode('utf-8'))
    print(postdata)
    message = postdata['message']
    days = int(postdata['days'])
    posts = int(postdata['posts'])
    threads = int(postdata['threads'])
    reputation = int(postdata['reputation'])
    sitedata.append({
        "message": message,
        "days": days,
        "posts": posts,
        "threads": threads,
        "reputation": reputation
        })
    savedata()
    for i in range(0, len(sitedata)):
        if i == (len(sitedata)-1):
            return {'id': i}

@app.route('/view/<int:id>', methods=["GET"])
def show(id):
    global sitedata
    global currentlink
    postdata = sitedata[id]
    try:
        if session['post'] != id:
            session.pop('post', None)
            session.pop('state', None)
            session.pop('verify', None)
    except:
        dab = 'lol'
    try:
        session['state']
        if session['state'] == 0 and session['post'] == id:
            session['state'] = 1
    except:
        session['state'] = 0
        session['post'] = id
    veri = ""
    post = postdata['message']
    if session['state'] == 1:
        veri += currentlink+"_VERIFICATION_"+str(id)+"_"
        veri += ''.join(random.choices(string.ascii_uppercase + string.digits, k=45))
        session['verify'] = veri
    return render_template('view.html', currentlink=currentlink, session=session, request=request, verify=veri, id=id, post=post, postdata = postdata)
    #return postdata

@app.route('/vermillion/profile/<int:id>', methods=["GET"])
@app.route('/api/new', methods=["GET"])
def bruh(id):
    abort(404)
