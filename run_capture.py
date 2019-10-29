import argparse

import gstreamer
import upload
from input import InputMonitor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bucket', help='GCS bucket name')
    parser.add_argument('--path', help='GCS path prefix for uploading images')
    args = parser.parse_args()

    print('Press enter or button when you want to take a picture')

    input_monitor = InputMonitor()

    def user_callback(image, svg_canvas):
        nonlocal input_monitor

        if input_monitor.is_key_pressed():
            upload.upload(args.bucket, args.path, image)

    input_monitor.daemon = True
    input_monitor.start()
    print('monitoring keyboard input...')

    gstreamer.run_pipeline(user_callback)


if __name__ == '__main__':
    main()
