from multiprocessing import Process, Queue


class WriterOut(Process):
    def __init__(self, out_file, q_o: Queue, hash_types: list, log_out: Queue):
        super().__init__()
        self.out = out_file
        self.qo = q_o
        self.h = hash_types

    def run(self):
        with open(self.out, "w", encoding="utf-8") as f:
            f.write(";".join(["file", "size(B)"] + self.h) + "\n")
            try:
                while True:
                    data = self.qo.get()
                    if not data:
                        break
                    f.write(";".join([str(x) for x in data]) + "\n")
            except KeyboardInterrupt:
                f.write("KeyboardInterrupt")
            except Exception as err:
                f.write("e: ")
                f.write(str(err))
