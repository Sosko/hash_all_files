#!/usr/bin/python3
from traceback import print_exc, print_stack
from sys import platform, exc_info
from os import path
from time import sleep
from multiprocessing import Manager, cpu_count, freeze_support
from logging import info, warning, basicConfig
from src.HashFoundFiles import HashFoundFiles
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
    level = args.level * 10
    if level > 50:
        level = 50
    if args.log:
        basicConfig(filename=path.abspath(args.log.name), level=level, format='%(asctime)s %(levelname)s:%(message)s')
    else:
        basicConfig(level=level, format='%(asctime)s %(levelname)s:%(message)s')
    p = path.abspath(args.dir)
    if path.isdir(p):
        g_path = p
    else:
        warning("Invalid folder:", p)
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
        warning("Hash not recognized", args.hash)
        return
    # Prepare output and communication
    manager = Manager()
    q_files = manager.Queue()
    q_output = manager.Queue()
    dir_info = manager.Queue()
    # Prepare process
    info("*" * 50)
    info("Starting with:")
    info("Output file:" + str(path.abspath(args.output_file.name)))
    info("Path: " + str(g_path))
    info("Used hashes:" + ", ".join(hashes_types))
    info("Prepare workers")
    number_of_cpu = cpu_count()
    if 0 < args.w < number_of_cpu:
        number_of_worker = args.w
    else:
        number_of_worker = number_of_cpu
    P_WORKERS = [HashFoundFiles(q_files, q_output, hashes_types) for _ in range(number_of_worker)]
    info("Num of workers: " + str(len(P_WORKERS)))
    P_WRITER = WriterOut(path.abspath(args.output_file.name), q_output, hashes_types)
    P_WALKER = Walker(g_path, q_output, q_files, dir_info)
    info("*" * 50)
    info("Start workers")
    # Start process
    try:
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
        warning("Keyboard interrupt")
        warning("Start killing")
        P_WALKER.kill()
        [x.kill() for x in P_WORKERS]
        while P_WALKER.is_alive():
            sleep(0.1)
        while q_files.qsize() > 0:
            sleep(0.1)
    except Exception as e2:
        warning(str(e2))
        warning(print_stack())
        return
    info("Walker finished")
    P_WALKER.join()
    # Finish walking and send end signals
    sleep(1)
    info("Send end signal to workers")
    [q_files.put(False) for _ in P_WORKERS]
    # Wait for workers

    while True:
        if not any([x.is_alive() for x in P_WORKERS]):
            break
        sleep(1)

    [x.join() for x in P_WORKERS]
    info("Workers ended")
    # Finish rest
    q_output.put(False)
    info("Finish writings")
    P_WRITER.join()
    info("End")


######################################################################################
if __name__ == '__main__':
    if platform.startswith('win'):
        # On Windows calling this function is necessary.
        freeze_support()
    try:
        main()
    except SystemExit:
        pass
    except BaseException as e:
        print("Main error:")
        print(e)
        print_stack()
        print(exc_info())
######################################################################################
