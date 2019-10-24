import threading
import time

from periphery import GPIO


class LED:
    def __init__(self, gpio_r=1, gpio_b=2, gpio_g=3, invert=False):
        self._lock = threading.Lock()
        self._gpio_g = GPIO(gpio_g, "out")
        self._gpio_r = GPIO(gpio_r, "out")
        self._gpio_b = GPIO(gpio_b, "out")
        self._latest_call_time = None
        self._latest_call_duration = None
        self._latest_call_color = None
        self._written_value = True if invert is False else False
        th = threading.Thread(target=self._switch_off_timer)
        th.daemon = True
        th.start()

    def switch_green(self, duration=-1):
        self._lock.acquire()
        if self._latest_call_color == 'green':
            self._latest_call_time = time.monotonic()
            self._latest_call_duration = duration
            self._lock.release()
            return

        self._latest_call_color = 'green'
        self._switch_on([self._gpio_g], duration)
        self._lock.release()

    def switch_red(self, duration=-1):
        self._lock.acquire()
        if self._latest_call_color == 'red':
            self._latest_call_time = time.monotonic()
            self._latest_call_duration = duration
            self._lock.release()
            return

        self._latest_call_color = 'red'
        self._switch_on([self._gpio_r], duration)
        self._lock.release()

    def switch_blue(self, duration=-1):
        self._lock.acquire()
        if self._latest_call_color == 'blue':
            self._latest_call_time = time.monotonic()
            self._latest_call_duration = duration
            self._lock.release()
            return

        self._latest_call_color = 'blue'
        self._switch_on([self._gpio_b], duration)
        self._lock.release()

    def switch_yellow(self, duration=-1):
        self._lock.acquire()
        if self._latest_call_color == 'yellow':
            self._latest_call_time = time.monotonic()
            self._latest_call_duration = duration
            self._lock.release()
            return

        self._latest_call_color = 'yellow'
        self._switch_on([self._gpio_g, self._gpio_r], duration)
        self._lock.release()

    def switch_off_all(self):
        self._lock.acquire()
        self._switch_off()
        self._lock.release()

    def _switch_on(self, gpios, duration):
        self._latest_call_time = time.monotonic()
        self._latest_call_duration = duration
        self._switch_off()
        for gpio in gpios:
            gpio.write(self._written_value)

    def _switch_off(self):
        self._gpio_r.write(not self._written_value)
        self._gpio_g.write(not self._written_value)
        self._gpio_b.write(not self._written_value)

    def _switch_off_timer(self):
        while True:
            time.sleep(1)
            self._lock.acquire()
            if self._latest_call_duration is not None and \
               self._latest_call_time is not None and \
               self._latest_call_duration > 0:
                now = time.monotonic()
                diff = now - self._latest_call_time
                if diff >= self._latest_call_duration:
                    self._switch_off()
                    self._latest_call_color = None
                    self._latest_call_time = None
                    self._latest_call_duration = None
            self._lock.release()

    def dispose(self):
        self._lock.acquire()
        self._gpio_g.close()
        self._gpio_b.close()
        self._gpio_r.close()
        self._lock.release()
