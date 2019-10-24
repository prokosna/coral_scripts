import argparse
import time
import json

import gstreamer
import upload
import mqtt
from input import InputMonitor
from led import LED


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', help='GCP Project')
    parser.add_argument('--bucket', help='GCS bucket name')
    parser.add_argument('--path', help='GCS path prefix for uploading images')
    parser.add_argument('--region', help='GCP Region')
    parser.add_argument('--registry_id', help='IoT Core Registry ID')
    parser.add_argument('--device_id', help='IoT Core Device ID')
    parser.add_argument('--private_key', help='IoT Core Private Key File')
    parser.add_argument('--algorithm', help='IoT Core JWT Algorithm',
                        default='RS256')
    parser.add_argument('--ca_certs', help='IoT Core roots.pem',
                        default='roots.pem')
    parser.add_argument('--mqtt_host', help='IoT Core hostname',
                        default='mqtt.googleapis.com')
    parser.add_argument('--mqtt_port', help='IoT Core port',
                        type=int,
                        default=443)
    args = parser.parse_args()

    input_monitor = InputMonitor()
    led = LED(gpio_r=6, gpio_g=7, gpio_b=8, invert=True)
    led.switch_off_all()

    def user_callback(image, svg_canvas):
        nonlocal input_monitor

        if input_monitor.is_key_pressed():
            upload.upload(args.bucket, args.path, image)

    input_monitor.daemon = True
    input_monitor.start()
    print('monitoring keyboard input...')

    mqtt.setup_mqtt_client(
        args.project,
        args.registry_id,
        args.private_key,
        args.device_id,
        args.region,
        args.algorithm,
        args.ca_certs,
        args.mqtt_host,
        args.mqtt_port)

    def message_callback(payload):
        try:
            preds = json.loads(payload)
            preds.sort(key=lambda pred: pred['class_score'], reverse=True)
            top = preds[0]['class_name']
            if top == 'roadway_green':
                led.switch_green(duration=3)
            elif top == 'roadway_red':
                led.switch_red(duration=3)
            elif top == 'roadway_yellow':
                led.switch_yellow(duration=3)
            else:
                led.switch_off_all()
        except Exception as ex:
            print(ex)

    mqtt.add_message_callback(message_callback)

    gstreamer.run_pipeline(user_callback)


if __name__ == '__main__':
    main()
