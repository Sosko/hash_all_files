from multiprocessing import Process, Queue
from os import path, listdir, readlink
from time import sleep

from constants import MAX_LENGTH_QUEUE


class Walker(Process):
    def __init__(self, directory: str, output: Queue, file_output: Queue, logger: Queue, log_out: Queue):
        super().__init__()
        self.directory = directory
        self.o = output
        self.f = file_output
        self.log = logger
        self.visited = []
        self.log_out = log_out

    def run(self):
        try:
            for directory, f in self.walk(self.directory):
                if directory not in self.visited:
                    self.visited.append(directory)
                    self.log.put(directory)
                if type(f) != str:
                    self.o.put([directory, -1, str(f)])
                    continue
                file = path.join(directory, f)
                while self.f.qsize() > MAX_LENGTH_QUEUE:
                    sleep(0.1)
                self.f.put(file)
        except Exception as e:
            self.log_out.put(("walker->run", e))

    def walk(self, start_path):
        if not path.isdir(start_path):
            raise Exception("Not a dir")
        next_dirs = [path.abspath(start_path)]
        while True:
            if len(next_dirs) == 0:
                break
            d = next_dirs.pop(0)
            try:
                for file in listdir(d):
                    file_with_path = path.join(d, file)
                    if path.isfile(file_with_path):
                        yield d, file
                    elif path.isdir(file_with_path) and not self.is_junction(file_with_path):
                        next_dirs.append(file_with_path)
            except PermissionError as err:
                # self.log_out.put(("walker->walk->PermissionError", err, d))
                yield d, err
            except Exception as e:
                self.log_out.put(("walker->walk->Exception", e, d))
                continue

    def is_junction(self, test_path: str) -> bool:
        try:
            return bool(readlink(test_path))
        except OSError:
            return False
        except:
            return True
