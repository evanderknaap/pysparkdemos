# README 

Demos of streaming data with pySpark.
- The first demo is running locally on a textSocketStream, and stream Data to BigQuery
- The second demo runs on Dataproc, reads kafka data and dumps to output
- The third demo runs on a second Dataporc cluster, reads kafka data, streams to BigQuery and computes a moving average in a window.

## Demo 1

### Setup 
Create a dataset, to hold your data
```bash
bq --location=eu mk streaming_dataset
```
Next go, to the cloud console and create a table, called "tableA" which
has a column "id" of type integer, and "text" forof type String.

Create a virtual environment and install the required libraries.
```bash
virtualenv env 
source env/bin/activate
pip install -r requirements.txt
```

### Running the demo
Open a terminal window and start a stream on TCP socket 9999, using netcat server.
```bash
$ nc -lk 9999
```
Next, we are going to stream to BigQuery, using the *client.insertall* method.
This uses the [tabledata.insertall](https://cloud.google.com/bigquery/docs/
reference/rest/v2/tabledata/insertAll) API. This is limited to 10K rows, per 
client. We can play with the number of partitions, to manage the amount
of rows written by each executor.

Run the pyspark locally 
```bash
$ python streaming_app.py
```
Alternatively, we can do a spark submit.
```bash
spark-submit streaming_app.py
```
Each microbatch, a client is created (or reused) for each partition of the RDD
and the results written to BigQuery. You can play with
- The *microbatch* in the stream context, to see that every microbatch data is sent
- The *repartition* method, to change the amount of threads writing to BigQuery

## Demo 2 - Kafka stream to BigQuery 

In this demo, we create a Kafka cluster on DataProc and generate fake sensor 
data that is submitted to the topic. 
On the same cluster we deploy a simple pyspark application that reads the data
line by line, and dump it to the same table we created before.

### Setup 
Set environment variables
```
PROJECT=<your-project>
BUCKET=<your-bucket-name>
CLUSTER=<your-cluster-name>
```

Create a regional bucket. This will hold checkpointing data to reply the steam
if it fails. This is required for the *reduceByKeyAndWindow* transformations.
```bash
gsutil mb -l europe-west1 gs://$BUCKET
```

Create a DataProc Cluster with 3 master nodes, running Kafka. Note the initialization script that is passed to install Kafka on the nodes.
```bash
gcloud beta dataproc clusters create $CLUSTER \
    --enable-component-gateway --region europe-west1 --subnet default --zone "" --num-masters 3 \
    --master-machine-type n1-standard-2 --master-boot-disk-size 500 --num-workers 2 \
    --worker-machine-type n1-standard-2 --worker-boot-disk-size 500 --image-version 1.4-debian9 \
    --optional-components ANACONDA,JUPYTER --scopes 'https://www.googleapis.com/auth/cloud-platform' \
    --project $PROJECT --initialization-actions 'gs://dataproc-initialization-actions/kafka/kafka.sh'
```

From your local terminal, list the names of the worker nodes and note the name
of one of your worker nodes. We need it later.
``` bash
gcloud dataproc clusters describe $CLUSTER --region europe-west1 | grep w-
```

In the Google Cloud Console, navigate to **dataproc > cluster > vm-instances**. Click the SSH button next to any master node. In the terminal, paste the following code to create a topic. 
```bash
kafka-topics.sh --zookeeper localhost:2181 --create --replication-factor 1 --partitions 1 --topic test 
```
From within the same window, create an environment variable for one of the worker node names.
```bash
WORKER=<worker-name>
```
Generate random data and add it to the topic. We create a comma seperate string of a device_id, event_time timestamp, and two random numbers that mimic a sensor reading. 

```bash
  for i in {1..10000}; 
          do for i in {1..3}; 
                  do timestamp=$(date +%s);
                  echo "device_${i},${timestamp},$(($RANDOM%40+1)),$(($RANDOM%10+1))";
          done;
          sleep 1s; 
   done | /usr/lib/kafka/bin/kafka-console-producer.sh --broker-list $WORKER:9092 --topic test
```
Navigate **dataproc > cluster > vm-instances** in the console again. Create a second SSH tunnel on any of the nodes.
Store the name of a worker again in an environment variable.
```bash
WORKER=<your-worker-name>
```
Check if the messages exist. If all goes well, you should see messages flowing in.
```bash
/usr/lib/kafka/bin/kafka-console-consumer.sh \
    --bootstrap-server $WORKER:9092 \
    --topic test --from-beginning
```
### Run the demo: Spark on Dataproc
Next, lets's see if we can get messages incoming into our pyspark application. We are going to deploy a pyspark application, that prints 10 records, every 5 seconds in the output.
``` Bash
gcloud dataproc jobs submit pyspark --cluster=$CLUSTER\
    --region europe-west1\
    --properties spark.jars.packages=org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.1\
    sensor_streaming.py     
```
Grab the Job_id of the running spark job, and copy it. 
```bash
gcloud dataproc jobs list --region=europe-west1
```
Paste the Job_ID in the follow command to kill it
```bash
gcloud dataproc jobs kill <JOB_ID> --region=europe-west1
```
## Demo 3 streaming to BigQuery
Next, let's deploy a second cluster to run our pyspark job, called **spark**. Since we are using the Python SDK wrapper around the BigQuery **table.Insertall** API, we will add the bigquery library and intall it using Pip.
One can also use conda to install packages. However, the channels used in the startup script do not include the google cloud SDK, so we'll use Pip instead.

### Setup
Create thesecond cluster.
```bash
gcloud dataproc clusters create spark\
    --optional-components ANACONDA\
    --metadata 'PIP_PACKAGES=google-cloud-bigquery'\
    --region europe-west1\
    --initialization-actions gs://dataproc-initialization-actions/python/pip-install.sh
```
### Running the demo: kafka to BigQuery
Finally, we'll create a slightly more exotic stream to BigQuery. The stream will be parsed, and send to a second table, called *TableB*. We will also compute the average of *reading_1* in the stream over a sliding window, and
pprint the result to output.

First we create a new table in BigQuery, called *tableB*, with the following schema:
- device: string
- timestamp: timestamp
- reading_1: int
- reading_2: int

Next, it is time to run our job.

```bash
gcloud dataproc jobs submit pyspark --cluster=spark\
    --region europe-west1\
    --properties spark.jars.packages=org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.1\
    windowed_sensor_stream.py  
```

If all goes well, you should see the data stream into BigQuery. Your terminal window should look like this:


## Clean up 
```bash
gsutil rm -r gs://$PROJECT
bq rm streaming_dataset
gcloud dataproc clusters delete $CLUSTER --region europe-west1
gcloud dataproc clusters delete spark --region europe-west1
```
