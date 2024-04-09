import queue
import threading


def consume(q: queue.Queue):
    while True:
        func, arg, kwarg = q.get()
        func(arg, kwarg)


class XYZThreading:

    def __init__(self, n_thread):
        self.n_thread = n_thread
        self.threads = []
        self.queue = queue.Queue()

    def add_task(self, func, *arg, **kwarg):
        self.queue.put((func, arg, kwarg))

    def start(self):
        for i in range(self.n_thread):
            t = threading.Thread(target=consume, args=(self.queue,), name=f'consumer{i}')
            t.start()
            self.threads.append(t)

    def join(self):
        for t in self.threads:
            t.join()
