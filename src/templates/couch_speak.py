from couchbase import Couchbase
from couchbase.exceptions import CouchbaseError

c = Couchbase.connect(bucket='beer-sample', host='54.85.199.152', port="8091")

try:
    beer = c.get("alaskan_brewing-alaskan_stout")

except CouchbaseError as e:
    print "Couldn't retrieve value for key", e
    # Rethrow the exception, making the application exit
    

print(beer.geo)
