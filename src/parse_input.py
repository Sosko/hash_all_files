from multiprocessing import cpu_count
from os import sep, path
from argparse import ArgumentParser, FileType, ArgumentDefaultsHelpFormatter
from src.constants import SUPPORTED_HASHES


def parse_input():
    # noinspection PyTypeChecker
    parser = ArgumentParser(prog='hash_all_files',
                            description='Create hash for all files in specific directory',
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'output_file',
        metavar='output_file',
        type=FileType('w', encoding='UTF-8'),
        help='Output file')
    parser.add_argument(
        '--dir',
        metavar='start_directory',
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
        default=cpu_count(),
        help='Set maximum of workers')
    parser.add_argument(
        '--log',
        type=FileType('a', encoding='UTF-8'),
        default=False,
        help='Log file, if not defined, log to stdout')
    parser.add_argument(
        '--level',
        type=int,
        default=2,
        help='Log level (0-5)')
    return parser
