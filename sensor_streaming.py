import findspark
findspark.init()

from pyspark.streaming import StreamingContext
from signifai.pubsub import PubsubUtils
from pyspark import SparkContext
from pyspark import SparkConf

SUBSCRIPTION = "projects/rabobqml/subscriptions/sub"

sc = SparkContext("local[3]","first streaming app")
ssc = StreamingContext(sc, 10)
pubsubStream = PubsubUtils.createStream(ssc, SUBSCRIPTION, 5, True)
pubsubStream.pprint()
ssc.start()
ssc.awaitTermination()