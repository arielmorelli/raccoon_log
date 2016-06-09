from datetime import datetime
import logging
import tarfile
from os import path
from os import makedirs
from os import listdir
from os import remove
from os.path import isfile, join

IMPORTANT_LEVEL = 25

logging.addLevelName(IMPORTANT_LEVEL, "IMPORTANT")


def _to_path(value):
    """
    Return the value stripped.

    Args:
        value: string to strip;
    Return:
        string: stripped string;
    """
    value = value.lstrip()
    value = value.rstrip(' /')
    value += '/'
    return value


def config_log(directory, log_name, max_files_uncompressed=1, max_level=25, compress=True):
    """
    Configure log using a default pattern and create a new level (important).

    Args:
        directory: folder to save logs;
        log_name: first part of the log name;
        max_files_uncompressed: max number of remaining not compressed files;
        max_level: max level of log;
        compress: indicates if compress the logs or no;
    """
    end_with = '.log'
    directory = _to_path(directory)

    if not path.exists(directory):
        makedirs(directory)

    set_logger(directory, log_name, max_level)

    if compress:
        clean_up_logs(directory, log_name, end_with, max_files_uncompressed)


def _important(message, *args, **kwargs):
    """
    Function to log in the new level (important)

    Args:
        message: message to log;
    """
    logging.log(IMPORTANT_LEVEL, message, args, **kwargs)


def set_logger(directory, name, level=25):
    """
    Set the log pattern using default configs.

    Args:
        directory: folder to save the log;
        name: name of the software;
        level: log level;
    """
    now = datetime.now().strftime('%Y_%m_%d')
    log_path = '{}/{}_{}.log'.format(directory, name, now)

    format_pattern = '[%(asctime)s.%(msecs)d] - %(levelname)s: %(message)s'
    logging.basicConfig(filename=log_path, filemode='a', format=format_pattern,
                        datefmt='%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger()
    logger.setLevel(level)
    logging.important = _important


def clean_up_logs(directory, starts_with, ends_with, max_files_uncompressed):
    """
    Compress old logs as a '.tar' file.

    Args:
        directory: folder to save the log;
        starts_with: first part of the name used at log files;
        ends_with: extension of log files;
        max_files_uncompressed: max number of remaining not compressed files;
    """
    log_files = [log_file for log_file in listdir(directory) if isfile(join(directory, log_file)) and
                 log_file.startswith(starts_with) and log_file.endswith(ends_with)]

    if max_files_uncompressed < 1:
        return

    if log_files and len(log_files) > max_files_uncompressed:
        log_files.sort()
        [log_files.pop() for _ in range(max_files_uncompressed)]

        compressed_name = '{}_logs'.format(starts_with)
        tar_path = '{}/{}.tar'.format(directory, compressed_name)

        tar_stream = tarfile.open(tar_path, mode='a')
        try:
            for log_file in log_files:
                log_file_path = '{}/{}'.format(directory, log_file)
                tar_stream.add(log_file_path, arcname=log_file)
                remove(log_file_path)
        except Exception as err:
            logging.important('Error compressing logs. (Error: {0})'.format(err))
        tar_stream.close()