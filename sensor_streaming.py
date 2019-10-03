from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark import SparkContext, SparkConf

sc = SparkContext(appName="Kafka streaming app")
ssc = StreamingContext(sc, 5) # The number denotes the minibatch 

directKafkaStream = KafkaUtils.createDirectStream(
        ssc, 
        ["test"], 
        {"metadata.broker.list": "demo-w-0:9092"})
lines = directKafkaStream.map(lambda x: x[1]).pprint()

ssc.start()
ssc.awaitTermination()