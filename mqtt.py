#!/usr/bin/env python

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import random
import ssl
import time
import threading

import jwt
import paho.mqtt.client as mqtt


minimum_backoff_time = 1
MAXIMUM_BACKOFF_TIME = 32
should_backoff = False
lock = threading.Lock()
message_callbacks = []


def create_jwt(project_id, private_key_file, algorithm):
    token = {
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        'aud': project_id
    }

    # Read the private key file.
    with open(private_key_file, 'r') as f:
        private_key = f.read()

    print('Creating JWT using {} from private key file {}'.format(
        algorithm, private_key_file))

    return jwt.encode(token, private_key, algorithm=algorithm)


def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


def on_connect(unused_client, unused_userdata, unused_flags, rc):
    """Callback for when a device connects."""
    print('on_connect', mqtt.connack_string(rc))

    # After a successful connect, reset backoff time and stop backing off.
    global should_backoff
    global minimum_backoff_time
    should_backoff = False
    minimum_backoff_time = 1


def on_disconnect(unused_client, unused_userdata, rc):
    """Paho callback for when a device disconnects."""
    print('on_disconnect', error_str(rc))

    # Since a disconnect occurred, the next loop iteration will wait with
    # exponential backoff.
    global should_backoff
    should_backoff = True


def on_message(unused_client, unused_userdata, message):
    """Callback when the device receives a message on a subscription."""
    payload = str(message.payload.decode('utf-8'))
    lock.acquire()
    for callback in message_callbacks:
        callback(payload)
    lock.release()


def get_client(project_id, cloud_region, registry_id, device_id,
               private_key_file, algorithm, ca_certs, mqtt_bridge_hostname,
               mqtt_bridge_port):
    client_id = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(
        project_id, cloud_region, registry_id, device_id)
    print('Device client_id is \'{}\''.format(client_id))

    client = mqtt.Client(client_id=client_id)

    # With Google Cloud IoT Core, the username field is ignored, and the
    # password field is used to transmit a JWT to authorize the device.
    client.username_pw_set(
        username='unused',
        password=create_jwt(
            project_id, private_key_file, algorithm))

    # Enable SSL/TLS support.
    client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

    # Register message callbacks. https://eclipse.org/paho/clients/python/docs/
    # describes additional callbacks that Paho supports. In this example, the
    # callbacks just print to standard out.
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Connect to the Google MQTT bridge.
    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    # This is the topic that the device will receive configuration updates on.
    mqtt_config_topic = '/devices/{}/config'.format(device_id)

    # Subscribe to the config topic.
    client.subscribe(mqtt_config_topic, qos=1)

    # The topic that the device will receive commands on.
    mqtt_command_topic = '/devices/{}/commands/#'.format(device_id)

    # Subscribe to the commands topic, QoS 1 enables message acknowledgement.
    print('Subscribing to {}'.format(mqtt_command_topic))
    client.subscribe(mqtt_command_topic, qos=0)

    return client


def setup_mqtt_client(project_id,
                      registry_id,
                      private_key_file,
                      device_id,
                      cloud_region='us-central1',
                      alg='RS256',
                      ca_certs='roots.pem',
                      mqtt_hostname='mqtt.googleapis.com',
                      mqtt_port=443):
    global minimum_backoff_time
    global MAXIMUM_BACKOFF_TIME

    client = get_client(
        project_id,
        cloud_region,
        registry_id,
        device_id,
        private_key_file,
        alg,
        ca_certs,
        mqtt_hostname,
        mqtt_port
    )

    def check_connection():
        global minimum_backoff_time
        global MAXIMUM_BACKOFF_TIME
        while True:
            client.loop()
            if should_backoff:
                if minimum_backoff_time > MAXIMUM_BACKOFF_TIME:
                    print('Exceeded maximum backoff time')
                    break

                delay = minimum_backoff_time + random.randint(0, 1000) / 1000.0
                time.sleep(delay)
                minimum_backoff_time *= 2
                client.connect(mqtt_hostname, mqtt_port)
            time.sleep(1)

    th = threading.Thread(target=check_connection)
    th.daemon = True
    th.start()


def add_message_callback(callback):
    lock.acquire()
    message_callbacks.append(callback)
    lock.release()
