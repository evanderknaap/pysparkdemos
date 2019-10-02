from data_generator import generate_log_lines
import logging
from google.cloud import pubsub_v1
import random
import time

PROJECT_ID="project-cb-demo"
TOPIC = "sensors"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC)
sleep_time = 1 # seconds

def publish(publisher, topic, message):
    data = message.encode('utf-8')
    return publisher.publish(topic_path, data = data)

def callback(message_future):
    # When timeout is unspecified, the exception method waits indefinitely.
    if message_future.exception(timeout=30):
        print('Publishing message on {} threw an Exception {}.'.format(
            topic_name, message_future.exception()))
    else:
        print(message_future.result())

def get_callback(f, data):
    def callback(f):
        try:
            print(f.result())
            futures.pop(data)
        except:  # noqa
            print('Please handle {} for {}.'.format(f.exception(), data))

    return callback


if __name__ == '__main__':

    while True:
        lines = generate_log_lines()
        for line in lines:
            print(line)
            message_future = publish(publisher, topic_path, line)
            message_future.add_done_callback(get_callback(message_future, line))
        time.sleep(sleep_time)