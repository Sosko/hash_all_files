#!/usr/bin/python3
from traceback import print_exc, print_stack
from sys import platform, exc_info
from os import path
from time import sleep
from multiprocessing import Manager, cpu_count, freeze_support

from src.HashFoundFiles import HashFoundFiles
from src.Logger import Logger
from src.Walker import Walker
from src.WriterOut import WriterOut
from src.constants import SUPPORTED_HASHES
from src.parse_input import parse_input


def main():
    parser = parse_input()
    # Parse inputs
    args = parser.parse_args()
    # Test inputs
    # Logger
    P_LOG = Logger(path.abspath(args.log.name))
    p = path.abspath(args.dir)
    if path.isdir(p):
        g_path = p
    else:
        P_LOG.log("Invalid folder:", p)
        parser.print_help()
        return
    # Set hashes
    users_set_hashes = []
    for x in args.hash.replace(", ", "\n").replace(",", "\n").replace(" ", "\n").split("\n"):
        if x in SUPPORTED_HASHES:
            users_set_hashes.append(x)
    if len(users_set_hashes) > 0:
        hashes_types = users_set_hashes
    else:
        P_LOG.log("Hash not recognized", args.hash)
        return
    # Prepare output and communication
    manager = Manager()
    q_files = manager.Queue()
    q_output = manager.Queue()
    dir_info = manager.Queue()
    # Prepare process
    P_LOG.log("*" * 50)
    P_LOG.log("Starting with:")
    P_LOG.log("Output file:", path.abspath(args.output_file.name))
    P_LOG.log("Path:", g_path)
    P_LOG.log("Used hashes:", ", ".join(hashes_types))
    P_LOG.log("Prepare workers")
    number_of_cpu = cpu_count()
    if 0 < args.w < number_of_cpu:
        number_of_worker = args.w
    else:
        number_of_worker = number_of_cpu
    P_WORKERS = [HashFoundFiles(q_files, q_output, hashes_types) for _ in range(number_of_worker)]
    P_LOG.log("Num of workers:", len(P_WORKERS))
    P_WRITER = WriterOut(path.abspath(args.output_file.name), q_output, hashes_types, P_LOG.lq)
    P_WALKER = Walker(g_path, q_output, q_files, dir_info, P_LOG.lq)
    P_LOG.log("*" * 50)
    P_LOG.log("Start workers")
    # Start process
    try:
        P_LOG.start()
        P_LOG.join(0.1)
        P_WRITER.start()
        P_WRITER.join(0.1)
        P_WALKER.start()
        [x.start() for x in P_WORKERS]
        [x.join(0.1) for x in P_WORKERS]
    except BaseException as e3:
        print("Start Workers error:")
        print(e3)
        print(exc_info())
        print(print_exc())
    # Start walking
    try:
        while P_WALKER.is_alive():
            sleep(0.1)
    except KeyboardInterrupt:
        P_LOG.log("Keyboard interrupt")
        P_LOG.log("Start killing")
        P_WALKER.kill()
        [x.kill() for x in P_WORKERS]
        while P_WALKER.is_alive():
            sleep(0.1)
        while q_files.qsize() > 0:
            sleep(0.1)
    except Exception as e2:
        P_LOG.log(e2)
        P_LOG.log(print_stack())
        P_LOG.kill()
        return
    P_LOG.log("Walker finished")
    P_WALKER.join()
    # Finish walking and send end signals
    sleep(1)
    P_LOG.log("Send end signal to workers")
    [q_files.put(False) for _ in P_WORKERS]
    # Wait for workers

    while True:
        if not any([x.is_alive() for x in P_WORKERS]):
            break
        sleep(1)

    [x.join() for x in P_WORKERS]
    P_LOG.log("Workers ended")
    # Finish rest
    q_output.put(False)
    P_LOG.log("Finish writings")
    P_WRITER.join()
    P_LOG.log("End")
    P_LOG.kill()


######################################################################################
if __name__ == '__main__':
    if platform.startswith('win'):
        # On Windows calling this function is necessary.
        freeze_support()
    try:
        main()
    except BaseException as e:
        print("Main error:")
        print(e)
        print(print_stack())
        print(exc_info())
######################################################################################
