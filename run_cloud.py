import argparse
import time

import gstreamer
import upload
import mqtt
from input import InputMonitor
from led import LED


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', help='GCP Project')
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
    parser.add_argument('--fps', help='Capturing frames per second',
                        type=float, default=1)
    parser.add_argument('--manual', help='Take a picture when key pressed',
                        action='store_true')
    args = parser.parse_args()

    if args.manual:
        print('Press enter when you want to take a picture')
    else:
        print('FPS is {}'.format(args.fps))

    duration = 1.0 / args.fps
    last_time = time.monotonic()

    input_monitor = InputMonitor()

    def user_callback(image, svg_canvas):
        nonlocal input_monitor
        nonlocal last_time

        start_time = time.monotonic()
        if args.manual:
            if input_monitor.is_key_pressed():
                upload.upload(args.bucket, args.path, image)
        else:
            if start_time - last_time > duration:
                upload.upload(args.bucket, args.path, image)
                last_time = time.monotonic()

    if args.manual:
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
        print('Message received: {}'.format(payload))

    mqtt.add_message_callback(message_callback)

    gstreamer.run_pipeline(user_callback)


if __name__ == '__main__':
    main()
