from multiprocessing import Process, Queue
from os import path

from src.DoHash import DoHash


class HashFoundFiles(Process):
    def __init__(self, files: Queue, output: Queue, hash_types: list):
        super().__init__()
        self.i = files
        self.o = output
        self.hl = hash_types

    def run(self):
        while True:
            file = self.i.get()
            if not file:
                break
            h = DoHash(self.hl)
            try:
                size = path.getsize(file)
                if not path.isfile(file):
                    continue
                with open(file, "rb") as f:
                    while True:
                        data = f.read(1024 * 1024 * 20)
                        h.update(data)
                        if f.tell() >= size:
                            break
                    self.o.put([file, str(size)] + h.get())
            except KeyboardInterrupt:
                return
            except Exception as err:
                self.o.put([file, -1, str(err)])
