from sys import argv, platform
from os import walk, path, sep
from time import sleep
import hashlib
from argparse import ArgumentParser, FileType, ArgumentDefaultsHelpFormatter
from multiprocessing import Process, Manager, cpu_count, freeze_support, Queue
from datetime import datetime
from mywalk import mywalk


def time(for_file=False):
    if for_file:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S - ")


######################################################################################
SUPPORTED_HASHES = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256
}
LOG_FILE = False


######################################################################################
class DoHash:
    def __init__(self, types):
        global SUPPORTED_HASHES
        self.T = []
        for x in types:
            if x in SUPPORTED_HASHES:
                self.T.append(SUPPORTED_HASHES[x]())

    def update(self, data):
        [x.update(data) for x in self.T]

    def get(self):
        return [x.hexdigest() for x in self.T]


######################################################################################
def get_hash(q_f: Queue, q_o: Queue, hash_types):
    while True:
        file = q_f.get()
        if not file:
            break
        h = DoHash(hash_types)
        try:
            size = path.getsize(file)
            with open(file, "rb") as f:
                while True:
                    data = f.read(1024 * 1024 * 20)
                    h.update(data)
                    if f.tell() >= size:
                        break
                q_o.put([file, str(size)] + h.get())
        except KeyboardInterrupt:
            return
        except Exception as err:
            q_o.put([file, -1, str(err)])


######################################################################################
def write_out(out_file, q_o: Queue, hash_types):
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(";".join(["file", "size(B)"] + hash_types) + "\n")
        try:
            while True:
                data = q_o.get()
                if not data:
                    break
                f.write(";".join([str(x) for x in data]) + "\n")
        except KeyboardInterrupt:
            f.write("KeyboardInterrupt")
        except Exception as err:
            f.write("e: ")
            f.write(str(err))


######################################################################################
def list_str(values):
    return values.split(',')


######################################################################################
def log(*args):
    global LOG_FILE
    if not LOG_FILE:
        print(time(), " ".join([str(x) for x in args]))
        return
    LOG_FILE.write(time(True))
    LOG_FILE.write(": ")
    LOG_FILE.write(" ".join([str(x) for x in args]))
    LOG_FILE.write("\n")


######################################################################################
def main():
    global SUPPORTED_HASHES, LOG_FILE
    ##########################################
    parser = ArgumentParser(prog='hash_all_files', description='Create hash for all files in specific directory',
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'output_file',
        metavar='output file',
        type=FileType('w', encoding='UTF-8'),
        help='Output file')
    parser.add_argument(
        '--dir',
        metavar='start directory',
        type=str,
        default=path.abspath(sep),
        nargs='?',
        help='Start directory')
    parser.add_argument(
        '--hash',
        type=str,
        default="md5",
        help='Select hash functions [' + ', '.join(SUPPORTED_HASHES) + ']')
    parser.add_argument(
        '--w',
        type=int,
        default=0,
        help='Set maximum of workers 0 = same as number of cores')
    parser.add_argument(
        '--log',
        type=FileType('a', encoding='UTF-8'),
        default=False,
        help='Log file, if not defined, log to stdout')

    args = parser.parse_args()
    ##########################################
    p = path.abspath(args.dir)
    number_of_cpu = cpu_count()
    if path.isdir(p):
        g_path = p
    else:
        log("Invalid folder:", p)
        parser.print_help()
        return
    ##########################################
    change = []
    for x in args.hash.replace(", ", "\n").replace(",", "\n").replace(" ", "\n").split("\n"):
        if x in SUPPORTED_HASHES:
            change.append(x)
    if len(change) > 0:
        hashes_types = change
    else:
        log("Hash not recognized", args.hash)
        return
    ##########################################
    manager = Manager()
    q_files = manager.Queue()
    q_output = manager.Queue()
    LOG_FILE = args.log
    ##########################################
    log("*" * 50)
    log("Starting with:")
    log("Output file:", path.abspath(args.output_file.name))
    log("Path:", g_path)
    log("Used hashes:", ", ".join(hashes_types))
    log("Prepare workers")
    if 0 < args.w < number_of_cpu:
        log("Num of workers:", args.w)
        process = [Process(target=get_hash, args=(q_files, q_output, hashes_types)) for _ in range(args.w)]
    else:
        log("Num of workers:", number_of_cpu)
        process = [Process(target=get_hash, args=(q_files, q_output, hashes_types)) for _ in range(number_of_cpu)]
    log("*" * 50)
    worker = Process(target=write_out, args=(path.abspath(args.output_file.name), q_output, hashes_types))
    log("Init workers")
    worker.start()
    worker.join(0.1)
    [x.start() for x in process]
    [x.join(0.1) for x in process]
    log("Start walking")
    ##########################################
    try:
        for directory, f in mywalk(g_path):
            if type(f) != str:
                q_output.put([directory, -1, str(f)])
                continue
            file = path.join(directory, f)
            while q_files.qsize() > 100:
                sleep(1)
            q_files.put(file)
    except Exception as ee:
        log("*" * 50)
        log(ee)
        log("*" * 50)
        while q_files.qsize() > 100:
            sleep(1)
        [q_files.put(False) for _ in process]
    ##########################################
    log("Walking end")
    sleep(1)
    log("Send end signal to workers")
    [q_files.put(False) for _ in process]
    ##########################################
    while True:
        if not any([x.is_alive() for x in process]):
            break
        sleep(1)
    [x.join() for x in process]
    log("Workers ended")
    ##########################################
    q_output.put(False)
    log("Finish writings")
    worker.join()
    log("End")


######################################################################################
if __name__ == '__main__':
    if platform.startswith('win'):
        # On Windows calling this function is necessary.
        freeze_support()
    try:
        main()
    except BaseException as e:
        log(e)
######################################################################################
