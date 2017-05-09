#submitted by ShyamGopalRajanna ID - 1001248518

import os
import sys
import boto
import timeit
import MySQLdb
import memcache
import hashlib
from boto.s3.key import Key


AWS_ACCESS_KEY = 'AKIAJKFBJ2WLWO2G5YCA'
AWS_ACCESS_SECRET_KEY = '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'

UPLOAD_FOLDER = 'C:/Shyam_UTA'
FILE_PATH = 'C:\\Shyam_UTA'

def uploadFile():
    filename = raw_input("Enter the file name")
    if filename :
        file_path = os.path.join(FILE_PATH,filename)

    name, file_extension = os.path.splitext(filename)
    bucket = 'newawsproj3'

    if file_extension == '.txt' :
        start_time = timeit.default_timer()
        result = upload_textfile(file_path, bucket)
        if result == True:
            duration = timeit.default_timer() - start_time
            print "Time taken to upload the text file: " + str(duration)
    elif file_extension == '.csv' :
        start_time = timeit.default_timer()
        result = upload_csv(bucket, file_path)
        if result == True:
            duration = timeit.default_timer() - start_time
            print "Time taken to upload the csv file: "+ str(duration)

    print "File uploading failed"

def upload_textfile(file, bucket, callback=None, md5=None,
                 reduced_redundancy=False, content_type=None):
    try:
        fileobject = open(file)
        key = fileobject.name
        size = os.fstat(fileobject.fileno()).st_size
        conn = boto.connect_s3(AWS_ACCESS_KEY, AWS_ACCESS_SECRET_KEY)
        bucket = conn.get_bucket(bucket, validate=True)
        k = Key(bucket)
        k.key = key
        if content_type:
           k.set_metadata('Content-Type', content_type)
        sent = k.set_contents_from_file(fileobject, cb=callback, md5=md5, reduced_redundancy=reduced_redundancy,
                                    rewind=True)
        fileobject.close()

        if sent == size:
            return True
        else:
            return False

    except Exception, e:
        print('Failed to upload to ftp: ' + str(e))



def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()


def upload_csv(bucket, testfile):
    conn = boto.connect_s3(AWS_ACCESS_KEY, AWS_ACCESS_SECRET_KEY)
    bucket = conn.get_bucket(bucket, validate=True)
    k = Key(bucket)
    k.key = testfile
    k.set_contents_from_filename(testfile, cb=percent_cb, num_cb=10)
    return True



###Importing csv data file

def import_data():
    rds_host = "flasktest.cebszmevfomz.us-west-1.rds.amazonaws.com"
    username = "flask"
    password = "gowriraj"
    dbname = "flaskdb"
    port = 3306

    connection = MySQLdb.Connect(host=rds_host, user=username, passwd=password, db=dbname)
    cursor = connection.cursor()
    start_time = timeit.default_timer()

    cursor.execute(
        """LOAD DATA LOCAL INFILE 'C:/Shyam_UTA/all_month.csv' INTO TABLE all_months_new FIELDS TERMINATED BY ','  OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES""")
    duration = timeit.default_timer() - start_time
    print "Time taken to import data: " + str(duration)

    connection.commit()
    return print "import_success.html"

###Executing randome query

def executeQuery():
    query = raw_input("Enter query to execute")
    n = raw_input("Enter number of times to execute query")
    n =  (int)n
    

    rds_host = "flasktest.cebszmevfomz.us-west-1.rds.amazonaws.com"
    username = "flask"
    password = "gowriraj"
    dbname = "flaskdb"

    conn = MySQLdb.Connect(host=rds_host, user=username, passwd=password, db=dbname)
    cur = conn.cursor()
    count = 1

    print "Executing query"
    
    start_time = timeit.default_timer()
    for x in range(1, n)
        cur.execute(query)
    duration = timeit.default_timer() - start_time
    
    print "Time taken to execute query: " + str(duration)
    conn.commit()
    conn.close()


def executeQueryForRangeOfTuples():
    query = raw_input("Enter query to execute")
    n = raw_input("Enter number of times to execute query")
    n =  (int)n
    

    rds_host = "flasktest.cebszmevfomz.us-west-1.rds.amazonaws.com"
    username = "flask"
    password = "gowriraj"
    dbname = "flaskdb"

    conn = MySQLdb.Connect(host=rds_host, user=username, passwd=password, db=dbname)
    cur = conn.cursor()
    count = 1

    print "Executing query"
    query = query +" limit 200,600" # Execute the query on tuples 200 to 800
    start_time = timeit.default_timer()
    for x in range(1, n)
        cur.execute(query)
    duration = timeit.default_timer() - start_time
    
    print "Time taken to execute query: " + str(duration)
    conn.commit()
    conn.close()
    

def executeQueryMemcache():
    query = raw_input("Enter query to execute")
    n = raw_input("Enter number of times to execute query")
    n =  (int)n
    
    rds_host = "flasktest.cebszmevfomz.us-west-1.rds.amazonaws.com"
    username = "flask"
    password = "gowriraj"
    dbname = "flaskdb"

    conn = MySQLdb.Connect(host=rds_host, user=username, passwd=password, db=dbname)
    cursor = conn.cursor()

    try:
        memc = memcache.Client(['mycachecluster.d9ga6x.cfg.usw1.cache.amazonaws.com:11211'])
        result = "Result+ "
        while num_of_rep > 0:
            h = hashlib.sha224(query).hexdigest()

            starttime = timeit.default_timer()
            cachedvalues = memc.get(h)
            endtime = timeit.default_timer()
            ftime = endtime - starttime

            result = result + "Memcached values: " + str(cachedvalues) +"\n\n"
            print "Memcached values: " + str(cachedvalues)
            if not cachedvalues:
                starttime = timeit.default_timer()
                num = cursor.execute(query)
                endtime = timeit.default_timer()
                ftime = endtime - starttime
                result = result + "Number of rows: " + str(num)+ "\n\n"
                print "Number of rows: " + str(num)
                result = result + "Time taken to fetch data from database: " + str(ftime)+ "\n\n"
                print "Time taken to fetch data from database: " + str(ftime)

                # Update memcache with the result
                if num != 0:
                    rows = cursor.fetchall()
                    memc.set(h, rows)
            else:
                result = result + "Time taken to fetch data from memcache: " + str(ftime)+ "\n\n"
                print "Time taken to fetch data from memcache: " + str(ftime)
            num_of_rep = num_of_rep - 1
        conn.close()


    except Exception as e:
        print "Error: " + str(e)

    print result



