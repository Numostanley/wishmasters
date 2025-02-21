import threading


class CustomThread(threading.Thread):
    def __init__(self, _callable, parameters):
        self._callable = _callable
        self.parameters: dict = parameters
        threading.Thread.__init__(self)

    def run(self):
        # print(self.parameters)
        self._callable(**self.parameters)
