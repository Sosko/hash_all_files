from datetime import datetime
from multiprocessing import Process
from multiprocessing import Queue


def time(for_file=False):
    if for_file:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S - ")


class Logger(Process):
    def __init__(self, output):
        super().__init__()
        self.o = output
        self.lq = Queue()

    def run(self):
        while True:
            data = self.lq.get()
            self.log_out(data)

    def log_out(self, *args):
        if not self.o:
            print(time(), " ".join([str(x) for x in args]))
            return
        elif type(self.o) == str:
            self.o = open(self.o, "a")
        self.o.write(time(True))
        self.o.write(": ")
        self.o.write(" ".join([str(x) for x in args]))
        self.o.write("\n")
        self.o.flush()

    def log(self, *args):
        self.lq.put(args)
