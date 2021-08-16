# coding=utf-8

from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
from inspect import getmembers, isfunction
import json

# Para rodar este script é necessário ter uma variável de ambiente chamada GOOGLE_APPLICATION_CREDENTIALS
# Esta variável de ambiente deve ter como valor a localização do arquivo `key.json`

# Trocar para api-mendelics para acessar produção
project_id = "api-mendelics-dev"

# Fornecer subscription id repassado aqui
subscription_id = "dummy_id"

timeout = 5.0

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def callback(message):
    # Esta função recebe a mensagem repassada pela API
    print(f"Received {message}.")

    print(json.loads(message.data.decode("utf-8")))
    # A função abaixo realiza o ack da mensagem, apagando ela da queue de mensagens
    # Verificar que a mensagem foi realmente salva localmente antes de dar ack
    message.ack()

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..\n")

# Wrap subscriber in a 'with' block to automatically call close() when done.
with subscriber:
    try:
        # When `timeout` is not set, result() will block indefinitely,
        # unless an exception is encountered first.
        x = streaming_pull_future.result(timeout=timeout)
    except TimeoutError:
        streaming_pull_future.cancel()  # Trigger the shutdown.
        streaming_pull_future.result()  # Block until the shutdown is complete.