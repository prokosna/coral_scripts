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
                        type=float, default=0.7)
    parser.add_argument('--top_k', help='Class Top K',
                        type=int, default=2)
    args = parser.parse_args()

    engine = ClassificationEngine(args.model)
    labels = load_labels(args.labels)

    led = LED(gpio_r=6, gpio_g=7, gpio_b=8, invert=True)
    led.switch_off_all()

    last_time = time.monotonic()

    def user_callback(image, svg_canvas):
        nonlocal last_time

        start_time = time.monotonic()
        results = engine.ClassifyWithImage(image,
                                           threshold=0.1,
                                           top_k=args.top_k)
        end_time = time.monotonic()

        text_lines = [
         'Inference: %.2f ms' %((end_time - start_time) * 1000),
         'FPS: %.2f fps' %(1.0/(end_time - last_time)),
        ]

        if len(results) == 0:
            led.switch_off_all()
        else:
            results.sort(key=lambda result: result[1], reverse=True)
            for index, score in results:
                text_lines.append('score=%.2f: %s' % (score, labels[index]))
                
            top_label = labels[results[0][0]]
            top_score = results[0][1]
            if top_score >= args.threshold:
                if top_label == 'roadway_green':
                    led.switch_green(duration=0.1)
                elif top_label == 'roadway_red':
                    led.switch_red(duration=0.1)
                elif top_label == 'roadway_yellow':
                    led.switch_yellow(duration=0.1)
                else:
                    led.switch_off_all()

        last_time = end_time
        print(' '.join(text_lines))
        generate_svg(svg_canvas, text_lines)

    gstreamer.run_pipeline(user_callback)


if __name__ == '__main__':
    main()
