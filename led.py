import threading
import time

from periphery import GPIO


class LED:
    def __init__(self, gpio_g=1, gpio_r=2, gpio_b=3, invert=False):
        self._lock = threading.Lock()
        self._gpio_g = GPIO(gpio_g, "out")
        self._gpio_r = GPIO(gpio_r, "out")
        self._gpio_b = GPIO(gpio_b, "out")
        self._latest_call = None
        self._written_value = True if invert is False else False

    def switch_green(self, duration=-1):
        self._switch_on([self._gpio_g], duration)

    def switch_red(self, duration=-1):
        self._switch_on([self._gpio_r], duration)

    def switch_yellow(self, duration=-1):
        self._switch_on([self._gpio_g, self._gpio_r], duration)

    def switch_off_all(self):
        self._lock.acquire()
        self._gpio_r.write(not self._written_value)
        self._gpio_g.write(not self._written_value)
        self._gpio_b.write(not self._written_value)
        self._lock.release()

    def _switch_on(self, gpios, duration):
        self.switch_off_all()
        self._lock.acquire()
        call_id = time.monotonic()
        for gpio in gpios:
            gpio.write(self._written_value)
        self._latest_call = call_id
        if duration > 0:
            self._start_switch_off_timer(call_id, duration)
        self._lock.release()

    def _start_switch_off_timer(self, call_id, duration):
        th = threading.Thread(target=self._switch_off_delay, args=(call_id, duration))
        th.start()

    def _switch_off_delay(self, call_id, duration):
        time.sleep(duration)
        self._lock.acquire()
        if call_id == self._latest_call:
            self._latest_call = None
            self._lock.release()
            self.switch_off_all()
        else:
            self._lock.release()

    def dispose(self):
        self._lock.acquire()
        self._gpio_g.close()
        self._gpio_b.close()
        self._gpio_r.close()
        self._lock.release()
