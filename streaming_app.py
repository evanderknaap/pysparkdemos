import findspark
findspark.init()
from google.cloud import bigquery
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from datetime import datetime

# Create the context
sc = SparkContext("local[3]","first streaming app")
ssc = StreamingContext(sc,10) # Micro batch
ssc.checkpoint("./checkpoints/")

# Create a socket to listen
lines = ssc.socketTextStream("localhost",9999)

words = lines.flatMap(lambda x: x.split(" "))
pairs = words.map(lambda word: (1,word))

def send_records(iter):
    try:
        client
    except:
        client = bigquery.Client() # Create client when it does not exist
    recs = list(iter)
    if len(recs) < 1: 
        print "no rows"
        return 

    table = client.get_table(client.dataset("streaming_dataset").table("tableA"))
    rows = [] # Bundle all rows in one write (Max 10K)
    now = datetime.now() # timestamp of partition write
    for record in recs:
        rows.append(
            {
             "id": record[0],
             "text": now.strftime("%H:%M:%S") 
            }
        )
    errors = client.insert_rows(table, rows)
    print(errors)

# For each RDD is called once in the driver, for each RDD. This is hence for each micro batch. 
# For each partition, is called for each partition within the RDD. 
# Since the workers write to BigQuery in paralell, the timestamps can be different
pairs.repartition(3).foreachRDD(lambda rdd: rdd.foreachPartition(send_records)) 

ssc.start()
ssc.awaitTermination()
