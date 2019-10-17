import argparse
import time
import re

import gstreamer
from led import LED
from edgetpu.classification.engine import ClassificationEngine


def load_labels(path):
    p = re.compile(r'\s*(\d+)(.+)')
    with open(path, 'r', encoding='utf-8') as f:
        lines = (p.match(line).groups() for line in f.readlines())
        return {int(num): text.strip() for num, text in lines}


def generate_svg(dwg, text_lines):
    for y, line in enumerate(text_lines):
        dwg.add(dwg.text(line, insert=(11, y*20+1), fill='black', font_size='20'))
        dwg.add(dwg.text(line, insert=(10, y*20), fill='white', font_size='20'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help='.tflite model file')
    parser.add_argument('--labels', help='.txt label file')
    parser.add_argument('--threshold', help='Class Score Threshold',
                        type=float, default=0.1)
    args = parser.parse_args()

    if args.manual:
        print('Press enter when you want to take a picture')
    else:
        print('FPS is {}'.format(args.fps))

    engine = ClassificationEngine(args.model)
    labels = load_labels(args.labels)

    led = LED(gpio_b=6, gpio_g=7, gpio_r=8, invert=True)

    last_time = time.monotonic()

    def user_callback(image, svg_canvas):
        nonlocal last_time

        start_time = time.monotonic()
        results = engine.ClassifyWithImage(image,
                                           threshold=args.threshold,
                                           top_k=2)
        end_time = time.monotonic()

        text_lines = [
         'Inference: %.2f ms' %((end_time - start_time) * 1000),
         'FPS: %.2f fps' %(1.0/(end_time - last_time)),
        ]
        for index, score in results:
            text_lines.append('score=%.2f: %s' % (score, labels[index]))
        print(' '.join(text_lines))
        last_time = end_time
        generate_svg(svg_canvas, text_lines)

    gstreamer.run_pipeline(user_callback)


if __name__ == '__main__':
    main()
