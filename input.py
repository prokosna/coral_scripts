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
