from flask import Flask
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import render_template
from flask import sessions
from flask import request, redirect, url_for
import base64
import os
import sys
import uuid
import json

app = Flask(__name__)
SIZE_LIMIT = 5000000 #5MB
NUM_FILE_LIMIT = 10

@app.route("/")
def homePage():
    return render_template("hello.html", methods=['POST'])


@app.route("/", methods=['POST'])
def loginPage():
    try:
        client = MongoClient('mongodb://104.197.196.166:27017/')
        db = client['test']  # test is the DB name
        collection = db.mycollection  # mycolledtion is table name
        
        inputusername = request.form['username']
        inputpassword = request.form['password']
        
        mongousername = collection.find_one({"name": inputusername})
        mongopassword = collection.find_one({"password": inputpassword})
        client.close()
        
        if str(inputusername) == str(mongousername['name']):
            
            if str(mongousername) == str(mongopassword):
                userpage = str(mongousername['name']).upper() + "  " + "LOGGED IN"
                uname = str(mongousername['name'])
                
                return render_template("user.html", userpagename=userpage, uname=uname)
            else:
                msg = "Password does not match"
                return render_template("error.html", msg=msg)
        else:
            msg = "User record not present"
            return render_template("error.html", msg=msg)
        
    except Exception as e:
        print e


def insert_img(username, size, image_data, filename, comments):
    client = MongoClient('mongodb://104.197.196.166:27017/')
    img_coll = client.imgupd.images
    post_dict = {}
    post_dict['filename'] = filename
    post_dict['username'] = username
    post_dict['size'] = size
    encoded_string = base64.b64encode(image_data)
    post_dict['image_data'] = encoded_string
    output = img_coll.save(post_dict)
    client.imgupd.comments.insert({"username":username,"filename":filename,"comment":comments})
    client.close()
    return encoded_string


@app.route("/upload/", methods=['POST'])
def goToUploadPage():
    uname = request.form['uname']
    return render_template("imageUpload.html", uname=uname)

#Code to limit file size and number of files allowed for user
def canUploadFile(username, fileSize):
    client = MongoClient('mongodb://104.197.196.166:27017/')
    img_coll = client.imgupd.images
    images1 = img_coll.find({"username": username})
    size = fileSize
    count = 0
    for images2 in images1:
        count = count + 1
        size += images2['size']
    client.close()
    
    if size < SIZE_LIMIT and count < NUM_FILE_LIMIT:
        return True

    return False

@app.route("/upload/file/", methods=['POST'])
def uploadFile():
    print "Here"
    username = request.form['uname']
    if 'file' not in request.files:
        print 'No file part'
        # redirect(request.url)
    file = request.files['file']
    comments = request.form['comments']
    if file.filename == '':
        print 'No file chosen'
        # redirect(request.url)
    if file:
        filename = file.filename
        print "Username:" + username
        image_data = file.read()
        size = len(image_data)
        print size       
        
        #post_id = str(uuid.uuid1())
        if canUploadFile(username, size):
            encoded_image = insert_img(username, size, image_data, str(file.filename), comments)
            return render_template("view_uploadedimage.html", inserted_image=encoded_image)
        else:
            return "File size exceeds limit. Cannot upload file"


#Display images and their comments of the user logged in
@app.route('/display', methods=['POST'])
def display():
    client = MongoClient('mongodb://104.197.196.166:27017/')
    imgs = []
    allcomment = []
    username = request.form['uname']
    img_coll = client.imgupd.images
    images1 = img_coll.find({"username": username})
	
    for images2 in images1:
        fname1 = images2['filename']
        print "fname:"+ fname1
        id = str(images2['_id'])
        comments1=client.imgupd.comments.find({"filename":fname1,"username":username})
        commentData = []
        for comments2 in comments1:
	    commentData.append(comments2['comment'])
	allcomment.append(commentData)
        
        imgs.append({'image': images2['image_data'], 'comments': allcomment, 'uname': images2['username'], 'filename': fname1, '_id':id})
    client.close()
    return render_template('fulldisplay.html', data=imgs)

#display images and their comments of all users
@app.route('/displayAll/')
def displayAll():
    client = MongoClient('mongodb://104.197.196.166:27017/')
    imgs = []
    allcomment = []
    img_coll = client.imgupd.images
    images1 = img_coll.find()
	
    for images2 in images1:
        fname1 = images2['filename']
        username = images2['username']
        id = str(images2['_id'])
	print "Well ths id is: "+id
        print "fname:"+ fname1
        comments1=client.imgupd.comments.find({"filename":fname1,"username":username})
        commentData = []
        for comments2 in comments1:
	    commentData.append(comments2['comment'])
	allcomment.append(commentData)
        
        imgs.append({'image': images2['image_data'], 'comments': allcomment, 'uname': images2['username'], 'filename': fname1, '_id':id})
    client.close()
    return render_template('fulldisplay.html', data=imgs)

#Add comments 
@app.route('/addcomment/',methods =['GET','POST'])
def comments():
    client = MongoClient('mongodb://104.197.196.166:27017/')
    print "in comments"
    comment_coll = client.imgupd.comments
    cc1=request.form['comment']
    fname=request.form['fname']
    uname=request.form['uname']
    print fname
    print uname
    images1=comment_coll.insert({"username":uname,"filename":fname,"comment":cc1})
    client.close()
    return redirect(url_for('display'), code=307)


#Delte an image
@app.route('/removeimage/',methods =['GET','POST'])
def removeImage():
    client = MongoClient('mongodb://104.197.196.166:27017/')
    print "in remove image"
    comment_coll = client.imgupd.images
    id=request.form['id']
    result=comment_coll.remove( {"_id": ObjectId(id)});
    print result
    client.close()
    return "Image successfully deleted"


#Display all images
@app.route('/displayonlyimages', methods=['GET', 'POST'])
def displayonlyimages():
    client = MongoClient('mongodb://104.197.196.166:27017/')
    imgs = []
    img_coll = client.imgupd.images
    images1 = img_coll.find()

    for images2 in images1:
        imgs.append({'image': images2['image_data']})
    client.close()

    return render_template('displayonlyimages.html', allimages=imgs)

