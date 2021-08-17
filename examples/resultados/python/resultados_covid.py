# coding=utf-8
from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
from inspect import getmembers, isfunction
import json

# This is the callback function from the topic listener. Each received message will call this method.
# Here you and do some work with the messages' content and ack the message.
# Remember that when you ack a message, pub/sub will remove it from the topic.
def do_something_with_message(message):
    print(f"Received message: {message}.")
    print(json.loads(message.data.decode("utf-8")))

    message.ack()


def get_messages(project_id, subscription_id):
    timeout = 5.0

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    topic_listener = subscriber.subscribe(subscription_path, callback=do_something_with_message)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            x = topic_listener.result(timeout=5.0)
        except TimeoutError:
            topic_listener.cancel()  # Trigger the shutdown.
            topic_listener.result()  # Block until the shutdown is complete.


# When in production, use values sent by Mendelics.
project_id = "api-mendelics-dev"
subscription_id = "homolog-result-sub"

# To run this script you must have an environment varible called GOOGLE_APPLICATION_CREDENTIALS.
# Its value is the path to "key.json" file.
get_messages(project_id, subscription_id)