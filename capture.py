import argparse
import time

import gstreamer
import upload
import threading


class InputMonitor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._lock = threading.Lock()
        self._is_key_pressed = False

    def is_key_pressed(self):
        self._lock.acquire()

        if self._is_key_pressed:
            self._is_key_pressed = False
            self._lock.release()
            return True

        self._lock.release()

        return False

    def run(self):
        while True:
            input()
            self._lock.acquire()
            self._is_key_pressed = True
            self._lock.release()


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

    def user_callback(image):
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
