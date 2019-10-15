import argparse
import time

import gstreamer
import upload
from input import InputMonitor


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bucket', help='GCS bucket name')
    parser.add_argument('--path', help='GCS path prefix for uploading images')
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

    gstreamer.run_pipeline(user_callback)


if __name__ == '__main__':
    main()
