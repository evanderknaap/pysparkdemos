from google.cloud import bigquery
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark import SparkContext, SparkConf

def line_to_kv(record):
    arguments = record.split(",")
    key = arguments[0]
    reading_1 = float(arguments[2])

    return (key, reading_1)

def line_to_dict(record):
    arguments = record.split(",")
    row = {
        "device": arguments[0],
        "timestamp": arguments[1],
        "reading_1": arguments[2],
        "reading_2": arguments[3]
    }
    return row

def send_records(iter):
    try:
        client
    except:
        client = bigquery.Client() # Create client when it does not exist
    recs = list(iter)
    if len(recs) < 1: 
        print("no rows")
        return 

    table = client.get_table(client.dataset("streaming_dataset").table("tableB"))
    rows = [] # Bundle all rows in one write (Max 10K)
    for record in recs:
        rows.append(record)
           
    errors = client.insert_rows(table, rows)
    print(errors)

sc = SparkContext(appName="Sensor stream to BigQuery")
ssc = StreamingContext(sc, 5) # The number denotes the minibatch 
ssc.checkpoint('gs://rabobqml/checkpoints/')

directKafkaStream = KafkaUtils.createDirectStream(
        ssc, 
        ["test"], 
        {"metadata.broker.list": "demo-w-0:9092"})
lines = directKafkaStream.map(lambda x: x[1])
records = lines.map(line_to_dict)
errors = records.foreachRDD(lambda rdd: rdd.foreachPartition(send_records))

# Compute average of past 20 seconds, every 5 seconds
kv = lines.map(line_to_kv)
mapped_kv = kv.mapValues(lambda v: (v,1))
sums = mapped_kv.reduceByKeyAndWindow(lambda x, y: (x[0] + y[0], x[1] + y[1]), 20, 5)
avg = sums.mapValues(lambda x: x[0]/x[1])
avg.pprint()

ssc.start()
ssc.awaitTermination()