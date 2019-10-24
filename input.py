import threading
import time

from periphery import GPIO


class InputMonitor(threading.Thread):
    def __init__(self, gpio_pin=None):
        threading.Thread.__init__(self)
        self._is_gpio = gpio_pin is not None
        if self._is_gpio:
            self._gpio = GPIO(gpio_pin, 'in')
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
            if self._is_gpio:
                v = self._gpio.read()
                if v and not self._is_key_pressed:
                    self._lock.acquire()
                    self._is_key_pressed = True
                    self._lock.release()
                time.sleep(0.1)
            else:
                input()
                self._lock.acquire()
                self._is_key_pressed = True
                self._lock.release()
