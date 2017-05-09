#submitted by ShyamGopalRajanna ID - 1001248518

from flask import Flask
from flask import render_template
import numpy as np
from sklearn.cluster import KMeans
import json

app = Flask(__name__)


@app.route('/')
def hello_world():
    vector = []

    try:
        f = open("C:/Shyam_UTA/MapRed/examples.csv", "r")
        infile = f
        next(infile)
        for line in infile:
            if not line:
                continue
            fields = line.split(',')
            latitude = fields[1].strip()
            depth = fields[3].strip()
            vector_element = []
            try:
                vector_element.append(float(depth))
                print "depth", depth
                vector_element.append(float(latitude))
                print "latitude", latitude
            except:
                continue
            vector.append(vector_element)
        print vector
        data = np.array(vector)
        clusters = 4
        kmean = KMeans(n_clusters=clusters)
        kmean.fit(data)

        centroids = []

        for v in kmean.cluster_centers_:
            centroids.append([v[0], v[1]])
            data1 = {'numclusters': clusters, 'centroids': centroids}

        print "Centroids: "
        print centroids
        for i in range(0, clusters):
            ds = data[np.where(kmean.labels_ == i)]
            dsarray = []
            # print ds
        for d1 in ds:
            dsarray.append([d1[0], d1[1]])
            data1['cluster' + str(i)] = dsarray
        print json.dumps(data1)

        chartdata = json.dumps(centroids)
        return render_template("chart.html", chartdata=chartdata)


    except Exception as e:
        print "exeption is"
        print e
    return 'Error!'


if __name__ == '__main__':
    app.run()
