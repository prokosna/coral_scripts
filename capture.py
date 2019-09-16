import argparse
import time

import gstreamer
import upload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bucket', help='GCS bucket name')
    parser.add_argument('--path', help='GCS path prefix for uploading images')
    parser.add_argument('--fps', help='Capturing frames per second',
                        type=int, default=1)
    args = parser.parse_args()

    print('FPS is {}'.format(args.fps))
    duration = 1.0 / args.fps
    last_time = time.monotonic()

    def user_callback(image, svg_canvas):
        nonlocal last_time
        start_time = time.monotonic()
        if start_time - last_time > duration:
            upload.upload(args.bucket, args.path, image)
            last_time = time.monotonic()

    result = gstreamer.run_pipeline(user_callback)


if __name__ == '__main__':
    main()
