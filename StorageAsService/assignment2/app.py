import MySQLdb
import os
import swiftclient
import keystoneclient
import pyDes
from flask import Flask, request, render_template
global u_id
SIZE_LIMIT=1048576 #1MB

# Establish database connection
try:
        db=MySQLdb.connect(host="us-cdbr-iron-east-04.cleardb.net",
        user="b529d779cb825d",
        passwd="d7314d62 ",
        port=3306,
        db="ad_282142420d38a7b  ")
        print "Connected to MySQL database"
except Exception as e:
        print(e)

app=Flask(__name__)     
cursor = db.cursor()
userId = None

@app.route('/')
def run():
        return render_template("login.html")

# Login 
@app.route('/login',methods=['GET','POST'])     
def login():
        inputUname = request.form['uname']
        inputPwd = request.form['passwd']
        try:
                cursor.execute("Select * from userdb where uname=%s and pwd=%s",(inputUname,inputPwd))
                result = cursor.fetchall()
                for (uid,uname,pwd) in result:
                        userId = uid
                        username = uname
                        passwd = pwd
                        if (username == inputUname):
                                if (passwd == inputPwd):
                                        return render_template("home.html")
        except:
                print "Error"
        return "Invalid username and password"
        
@app.route('/upload')
def uploadPage():
        return render_template('upload.html')

def checkFileSizeLimit():
        storedFileSize=0        
        query="select size from filedb where uid=%s"
        cursor.execute(sql6,userId)
        result=cursor.fetchall()
        for j in result:
                storedFileSize=storedFileSize+int(j)
        
        #Checking User quota
        if(storedFileSize< SIZE_LIMIT):
                return True
        
        return False
        
@app.route('/upload',methods=['POST'])
def upload():   
        file=request.files['file']      
        fileList=[]     
        size = len(file.read())
        cursor.execute("select filename from filedb where uid=%s",(userId))
        res=cursor.fetchall()
        for files in res:
                fileList.append(files)
        version=0
        for fname in fileList:
                if(file.filename==fname):
                        query="select version from filedb where filename=%s and user_id=%s order by version desc"
                        arg=(file1.filename,str(userId))                        
                        cursor.execute("select version from filedb where filename=%s and user_id=%s order by version desc",(fname,uname))
                        curVersion=cursor.fetchone()
                        version=curVersion+1

        if checkFileSizeLimit():
                desc=request.form['desc']
                content = file.read()
                insertQuery= "INSERT INTO filedb (ud,filename,content,desc,size,version) values (%s,%s,%s,%s,%s,%s)"
                args=(userId,file.filename,content,desc,size,version)
                cursor.execute(insertQuery,args)
                db.commit()
        else:
                return "User has exceeded the file size quota"
                
        
        return "File uploaded"
        
port = os.getenv('PORT', 8000)
if __name__=="__main__":
        app.run(host='0.0.0.0', port=int(port))
