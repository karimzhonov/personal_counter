from threading import Thread

from project.logger import logger
from .conf import CAPTURES
from .compare_face import compare_face


def start():
    logger.info('Compare Faces started')
    for cap in CAPTURES:
        Thread(target=compare_face, args=(cap,)).start()