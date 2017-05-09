from flask import Flask
import logging
import base64
import unittest
import json
import os.path
import os
import sys
from flask import request, redirect, url_for
import pydocumentdb.documents as documents
import pydocumentdb.document_client as document_client
import pydocumentdb.errors as errors
import pydocumentdb.http_constants as http_constants
import pydocumentdb.hash_partition_resolver as hash_partition_resolver
import pydocumentdb.range_partition_resolver as range_partition_resolver
import pydocumentdb.murmur_hash as murmur_hash
import pydocumentdb.consistent_hash_ring as consistent_hash_ring
import pydocumentdb.range as partition_range
import pydocumentdb.base as base
from flask import render_template
from flask import session

app = Flask(__name__)
app.secret_key = 'Rock ur life'

masterKey = 'HqBfFZxHTwI9Lmd6O2Ahqn6wyNcKlCPqnbqaWBrMjqrUF2OxFCWnElcZyYknQhxQmu66NAoaiWf8TvNCTLJnVA=='
host = 'https://shyamdocumentdb.documents.azure.com:443/;AccountKey=HqBfFZxHTwI9Lmd6O2Ahqn6wyNcKlCPqnbqaWBrMjqrUF2OxFCWnElcZyYknQhxQmu66NAoaiWf8TvNCTLJnVA==;'
testDbName = 'shyamdocumentdb'
resource_link = 'https://shyamdocumentdb.documents.azure.com:443/'



def logout():
    session.pop('username',None)



@app.route("/")
def homepage():
    return render_template("login.html")



@app.route("/",  methods=['POST'])
def check_connection_to_database():
    try:
        client = document_client.DocumentClient(host,{'masterKey': masterKey})
        list_of_databases = list(client.ReadDatabases())
        firstDB = list_of_databases[0]
        firstDB_link = firstDB['_self']
        query_collection = list(client.QueryCollections(firstDB_link,{'query':'SELECT * FROM  usercredentials'}))

        if len(query_collection) >0:
            print len(query_collection)
            print type(query_collection)

        qc = query_collection[0]
        qc_collection_link = qc['_self']

        executing_query = 'SELECT c.username,c.password FROM c '
        documents = list(client.QueryDocuments(qc_collection_link, {'query': executing_query}))
        print "documents" + str(documents)
        inputusername = request.form['username']
        inputpassword = request.form['password']
        for dict in documents:
            if dict:
                print "username --->" + str(dict['username'])
                print "password --->" + str(dict['password'])
                if ((dict['username'] == inputusername) and (dict['password'] == inputpassword)):
                    print "correct credentails"
                    session['username'] = str(inputusername)
                    #logout()
                    return render_template("post_login_new.html")
                else:
                    print "wrong credentials"

    except Exception as e:
        print "exception is --->"+str(e)

def checkFileSizeLimit(size,type):
    if 'username' in session:
        PIC_SIZE_LIMIT = 500000  # 500KB
        NOTE_SIZE_LIMIT = 1000 #1KB
        client = document_client.DocumentClient(host, {'masterKey': masterKey})
        query_database = list(client.QueryDatabases('SELECT * FROM  mydatabase'))
        firstDB = query_database[0]
        firstDB_link = firstDB['_self']
        query_collection = list(client.QueryCollections(firstDB_link, {'query': 'SELECT * FROM  usercredentials'}))
        qc = query_collection[0]
        qc_collection_link = qc['_self']
        executing_query = 'SELECT * FROM c where c.username = \'' + session['username'] + '\''


        try:
            userdetails = list(client.QueryDocuments(qc_collection_link, {'query': executing_query}))

            for records in userdetails:
                picsize = records['uploadedpicsize']
                picsize = int(picsize)
                notesize = records['uploadednotesize']
                notesize = int(notesize)

            if (picsize == 0 and str(type) == "pic"):

                picsize = size
                for i in userdetails:
                    i['uploadedpicsize'] = picsize
                    client.UpsertDocument(qc_collection_link, i)

                return True
            elif (str(type) == "pic"):
                newpicsize = picsize+size
                if (newpicsize > PIC_SIZE_LIMIT):
                    return False
                else:
                    for i in userdetails:
                        i['uploadedpicsize'] = newpicsize
                        client.UpsertDocument(qc_collection_link, i)

                    return True
            if (notesize == 0 and str(type) == 'note'):
                notesize = size

                for i in userdetails:
                    i['uploadednotesize'] = notesize
                    client.UpsertDocument(qc_collection_link, i)

                return True
            elif (str(type) == "note"):
                notesize = notesize + size
                if (notesize > NOTE_SIZE_LIMIT):
                    return False
                else:
                    for i in userdetails:

                        i['uploadednotesize'] = notesize
                        client.UpsertDocument(qc_collection_link,i)

                    return True
        except Exception as e:
            print "exception is check file size method"+str(e)


@app.route("/uploadnotes/", methods=['POST'])
def uploadnotes():
    return render_template("uploadnotes.html")

@app.route("/uploadnotes/form", methods=['POST'])
def create_document_note():
    try:
        if 'username' in session:
            client = document_client.DocumentClient(host, {'masterKey': masterKey})
            query_database = list(client.QueryDatabases('SELECT * FROM  mydatabase'))
            firstDB = query_database[0]
            firstDB_link = firstDB['_self']
            query_collection = list(client.QueryCollections(firstDB_link, {'query': 'SELECT * FROM  usercredentials'}))
            qc = query_collection[0]
            qc_collection_link = qc['_self']

            newdoc = {}
            newdoc['owner'] = session['username']
            newdoc['subject'] = request.form['subject']
            newdoc['notes'] = str(request.form['notes'])
            newdoc['priority'] = request.form['priority']
            newdoc['type'] = "note"
            newdoc['notesize'] = len(newdoc['notes'])

            print "type of newdoc['notesize']"+str(type(newdoc['notesize']))

            print "dictionary contents entered"
            condition = checkFileSizeLimit(newdoc['notesize'],newdoc['type'])
            print "condition"+str(condition)
            if (condition == True):
                try:
                    client.CreateDocument(qc_collection_link, newdoc)
                    print "document created"
                    logout()
                    return render_template("document_upload_status.html")
                except Exception as e:
                    print "error in document creation --->"+str(e)
            else:
                return render_template("exceeds_upload_quota_for_note.html")

    except Exception as e:
        print "there is an exception in upload notes method ---> "+str(e)

@app.route("/uploadpics/", methods=['POST'])
def uploadpic():
    return render_template("uploadpics.html")

def insert_img(image_data):
    encoded_string = base64.b64encode(image_data)
    return encoded_string

@app.route("/uploadpics/form", methods=['POST'])
def uploadpic_form():
    try:
        if 'username' in session:
            client = document_client.DocumentClient(host, {'masterKey': masterKey})
            query_database = list(client.QueryDatabases('SELECT * FROM  mydatabase'))
            firstDB = query_database[0]
            firstDB_link = firstDB['_self']
            query_collection = list(client.QueryCollections(firstDB_link, {'query': 'SELECT * FROM  usercredentials'}))
            qc = query_collection[0]
            qc_collection_link = qc['_self']
            # uploading image code
            if 'file' not in request.files:
                print 'No file part'
            file = request.files['file']
            if file.filename == '':
                print 'No file chosen'
            if file:
                filename = file.filename
                image_data = file.read()
            encoded_image = insert_img(image_data)
            picdoc = {}
            picdoc['pic'] = encoded_image
            picdoc['owner'] = session['username']
            picdoc['comment'] = request.form['comment']
            picdoc['priority'] = request.form['priority']
            picdoc['filename'] = filename
            picdoc['filesize'] = len(image_data)
            picdoc['type'] = "pic"

            print "picture dictionary contents entered"

            condition = checkFileSizeLimit(picdoc['filesize'], picdoc['type'])
            print "condition" + str(condition)
            if (condition == True):
                try:
                    client.CreateDocument(qc_collection_link, picdoc)
                    print "document created"
                    logout()
                    return render_template("image_upload_status.html")
                except Exception as e:
                    print "error in document creation --->" + str(e)
            else:
                return render_template("exceeds_upload_quota_for_note.html")

    except Exception as e:
        print "there is an exception in upload notes method ---> " + str(e)


@app.route("/singleimage/", methods=['POST'])
def singleimage():
    try:
        if 'username' in session:
            client = document_client.DocumentClient(host, {'masterKey': masterKey})
            list_of_databases = list(client.ReadDatabases())
            firstDB = list_of_databases[0]
            firstDB_link = firstDB['_self']
            query_collection = list(client.QueryCollections(firstDB_link, {'query': 'SELECT * FROM  usercredentials'}))
            qc = query_collection[0]
            qc_collection_link = qc['_self']
            try:
                documents = list(client.QueryDocuments(qc_collection_link, {
                    'query': 'SELECT r.pic FROM  root r where r.type = "pic"'}))
                image = documents[0]
                print "image" + str(image['pic'])
                logout()
                return render_template("displaysingleimage.html", singleimage=image['pic'])
            except Exception as e:
                print"there is an issue in query retrival" + str(e)

    except Exception as e:
        print "exception is --->" + str(e)

@app.route("/deletedocument/", methods=['POST'])
def deletedocument():
    try:
        if 'username' in session:
            client = document_client.DocumentClient(host, {'masterKey': masterKey})
            list_of_databases = list(client.ReadDatabases())
            firstDB = list_of_databases[0]
            firstDB_link = firstDB['_self']
            query_collection = list(client.QueryCollections(firstDB_link, {'query': 'SELECT * FROM  usercredentials'}))
            qc = query_collection[0]
            qc_collection_link = qc['_self']
            documents = list(client.QueryDocuments(qc_collection_link, {'query': 'SELECT * FROM  root r where r.comment = "cloud"'}))
            deldoc = documents[0]
            print "image" + str(deldoc['_self'])

            try:
                client.DeleteDocument(deldoc['_self'])
                logout()
                return render_template("deleted_document_confirmation.html", deleteddocid=deldoc['_self'])
            except Exception as e:
                print"there is an issue in deleting document" + str(e)

    except Exception as e:
        print "exception is --->" + str(e)

@app.route("/displayallnotes/", methods=['POST'])
def displayallnotes():
    try:
        if 'username' in session:
            client = document_client.DocumentClient(host, {'masterKey': masterKey})
            list_of_databases = list(client.ReadDatabases())
            firstDB = list_of_databases[0]
            firstDB_link = firstDB['_self']
            query_collection = list(client.QueryCollections(firstDB_link, {'query': 'SELECT * FROM  usercredentials'}))
            qc = query_collection[0]
            qc_collection_link = qc['_self']
            try:
                allnotes = list(client.QueryDocuments(qc_collection_link, {
                    'query': 'SELECT * FROM  root r where r.type = "note"'}))
                logout()
                return render_template("displayallnotes.html", allnotesdisplayed=allnotes)
            except Exception as e:
                print"there is an issue in query retrival" + str(e)

    except Exception as e:
        print "exception is --->" + str(e)

@app.route("/displayallimages/", methods=['POST'])
def displayallimages():
    try:
        if 'username' in session:
            client = document_client.DocumentClient(host, {'masterKey': masterKey})
            list_of_databases = list(client.ReadDatabases())
            firstDB = list_of_databases[0]
            firstDB_link = firstDB['_self']
            query_collection = list(client.QueryCollections(firstDB_link, {'query': 'SELECT * FROM  usercredentials'}))
            qc = query_collection[0]
            qc_collection_link = qc['_self']
            try:
                allpics = list(client.QueryDocuments(qc_collection_link, {
                    'query': 'SELECT * FROM  root r where r.type = "pic"'}))
                logout()
                return render_template("displayallpics.html", allpicsdisplayed=allpics)
            except Exception as e:
                print"there is an issue in query retrival" + str(e)

    except Exception as e:
        print "exception is --->" + str(e)

@app.route("/prioritysortingnotes/", methods=['POST'])
def prioritysortingnotes():
    try:
        if 'username' in session:
            client = document_client.DocumentClient(host, {'masterKey': masterKey})
            list_of_databases = list(client.ReadDatabases())
            firstDB = list_of_databases[0]
            firstDB_link = firstDB['_self']
            query_collection = list(client.QueryCollections(firstDB_link, {'query': 'SELECT * FROM  usercredentials'}))
            qc = query_collection[0]
            qc_collection_link = qc['_self']
            try:
                allnotes = list(client.QueryDocuments(qc_collection_link, {
                    'query': 'SELECT * FROM c where c.type = "note" order by c.priority'}))
                logout()
                return render_template("prioritysortingnotes.html", notessorting=allnotes)
            except Exception as e:
                print"there is an issue in query retrival" + str(e)

    except Exception as e:
        print "exception is --->" + str(e)

@app.route("/priorityquerysearch/", methods=['POST'])
def priorityquerysearch():
    return render_template("prioritysearch.html")

@app.route("/priorityquerysearch/form", methods=['POST'])
def priorityquerysearchform():
    try:
        if 'username' in session:
            client = document_client.DocumentClient(host, {'masterKey': masterKey})
            list_of_databases = list(client.ReadDatabases())
            firstDB = list_of_databases[0]
            firstDB_link = firstDB['_self']
            query_collection = list(client.QueryCollections(firstDB_link, {'query': 'SELECT * FROM  usercredentials'}))
            qc = query_collection[0]
            qc_collection_link = qc['_self']
            userinput_priority = request.form['priority']
            userinput_priority = str(userinput_priority)
            print "userinput_priority type is"+str(type(userinput_priority))
            print "userinput_priority -->"+userinput_priority
            executing_query = 'SELECT * FROM  root r where r.priority = \'' + userinput_priority + '\''
            print executing_query
            print qc_collection_link
            #return render_template("success.html")
            try:
                prioritysearch = list(client.QueryDocuments(qc_collection_link,{'query':executing_query}))
                logout()
                return render_template("displayallmatchingdocs.html", searchresults=prioritysearch)
            except Exception as e:
                print"there is an issue in priorityquerysearch retrival" + str(e)

    except Exception as e:
        print "exception is --->" + str(e)

@app.route("/ownerquerysearch/", methods=['POST'])
def ownerquerysearch():
    return render_template("ownersearch.html")

@app.route("/ownerquerysearch/form", methods=['POST'])
def ownerquerysearchform():
    try:
        if 'username' in session:
            client = document_client.DocumentClient(host, {'masterKey': masterKey})
            list_of_databases = list(client.ReadDatabases())
            firstDB = list_of_databases[0]
            firstDB_link = firstDB['_self']
            query_collection = list(client.QueryCollections(firstDB_link, {'query': 'SELECT * FROM  usercredentials'}))
            qc = query_collection[0]
            qc_collection_link = qc['_self']
            userinput_owner = request.form['owner']
            userinput_owner = str(userinput_owner)
            print "userinput_priority type is"+str(type(userinput_owner))
            print "userinput_priority -->"+userinput_owner
            executing_query = 'SELECT * FROM  root r where r.owner = \'' + userinput_owner + '\''
            #print executing_query
            #print qc_collection_link
            #return render_template("success.html")
            try:
                ownersearch = list(client.QueryDocuments(qc_collection_link,{'query':executing_query}))
                logout()
                return render_template("displayallmatchingdocs.html", searchresults=ownersearch)
            except Exception as e:
                print"there is an issue in priorityquerysearch retrival" + str(e)

    except Exception as e:
        print "exception is --->" + str(e)

@app.route("/notesubjectquerysearch/", methods=['POST'])
def notesubjectquerysearch():
    return render_template("subjectsearch.html")

@app.route("/notesubjectquerysearch/form", methods=['POST'])
def notesubjectquerysearchform():
    try:
        if 'username' in session:
            client = document_client.DocumentClient(host, {'masterKey': masterKey})
            list_of_databases = list(client.ReadDatabases())
            firstDB = list_of_databases[0]
            firstDB_link = firstDB['_self']
            query_collection = list(client.QueryCollections(firstDB_link, {'query': 'SELECT * FROM  usercredentials'}))
            qc = query_collection[0]
            qc_collection_link = qc['_self']
            userinput_subject = request.form['subject']
            userinput_subject = str(userinput_subject)
            print "userinput_priority type is"+str(type(userinput_subject))
            print "userinput_priority -->"+userinput_subject
            executing_query = 'SELECT * FROM  root r where r.subject = \'' + userinput_subject + '\''
            #print executing_query
            #print qc_collection_link
            #return render_template("success.html")
            try:
                subjectsearch = list(client.QueryDocuments(qc_collection_link,{'query':executing_query}))
                logout()
                return render_template("displayallmatchingdocs.html", searchresults=subjectsearch)
            except Exception as e:
                print"there is an issue in priorityquerysearch retrival" + str(e)

    except Exception as e:
        print "exception is --->" + str(e)

@app.route("/notestringquerysearch/", methods=['POST'])
def notestringquerysearch():
    return render_template("notestringquerysearch.html")

@app.route("/notestringquerysearch/form", methods=['POST'])
def notestringquerysearchform():
    try:
        if 'username' in session:
            client = document_client.DocumentClient(host, {'masterKey': masterKey})
            list_of_databases = list(client.ReadDatabases())
            firstDB = list_of_databases[0]
            firstDB_link = firstDB['_self']
            query_collection = list(client.QueryCollections(firstDB_link, {'query': 'SELECT * FROM  usercredentials'}))
            qc = query_collection[0]
            qc_collection_link = qc['_self']
            userinput_string = request.form['userstring']
            userinput_string = str(userinput_string)
            print "userinput_priority type is"+str(type(userinput_string))
            print "userinput_priority -->"+userinput_string
            executing_query = 'SELECT * FROM  root r where contains (r["notes"],\'' + userinput_string + '\')'
            #print executing_query
            #print qc_collection_link
            #return render_template("success.html")
            try:
                stringsearch = list(client.QueryDocuments(qc_collection_link,{'query':executing_query}))
                logout()
                return render_template("displayallmatchingdocs.html", searchresults=stringsearch)
            except Exception as e:
                print"there is an issue in priorityquerysearch retrival" + str(e)

    except Exception as e:
        print "exception is --->" + str(e)



if __name__ == '__main__':
    app.run()


###########################################################################





