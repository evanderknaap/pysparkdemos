from google.cloud import bigquery
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark import SparkContext, SparkConf

sc = SparkContext(appName="Sensor stream to BigQuery")
ssc = StreamingContext(sc, 5) # The number denotes the minibatch 

directKafkaStream = KafkaUtils.createDirectStream(
        ssc, 
        ["test"], 
        {"metadata.broker.list": "demo-w-0:9092"})
lines = directKafkaStream.map(lambda x: x[1])

def send_records(iter):
    try:
        client
    except:
        client = bigquery.Client() # Create client when it does not exist
    recs = list(iter)
    if len(recs) < 1: 
        print("no rows")
        return 

    table = client.get_table(client.dataset("streaming_dataset").table("tableA"))
    rows = [] # Bundle all rows in one write (Max 10K)
    for record in recs:
        rows.append(
            {
             "id": 1,
             "text": record # Just a dump
            }
        )
    errors = client.insert_rows(table, rows)
    print(errors)

errors = lines.repartition(2).foreachRDD(lambda rdd: rdd.foreachPartition(send_records))

ssc.start()
ssc.awaitTermination()