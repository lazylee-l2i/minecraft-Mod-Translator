import logging
from pathlib import Path
from datetime import datetime

from DirManager import dirCheck
from JarJsonProcessor import jsonJarManager

def TIME_STAMP():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def run():
    # Logger On
    if Path('./log').exists():
        pass
    else:
        Path('./log').mkdir()
    
    s = TIME_STAMP()
    
    logger = logging.getLogger('mod-translator')
    
    
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        filename=f"./log/{s}.log",
        level=logging.DEBUG,
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )
    logging.info(f'logging start')

    # Directory Check
    logging.info('Directory Checking.')
    rVal = dirCheck(logger)
    if rVal == -1:
        logging.error('Mod Directory Status : Error\nMake sure Mod File in \"mod\" folder!')
    elif rVal == -2:
        logging.warning('Translated Directory Status : Warnning\nSome file already in folder...  please check this bellow list of path.')
    logging.info('Directory Check Done.')

    # Searching Json
    logging.info('Json Searching.')
    jsonJarManager('./mod', logger=logger)


if __name__ == '__main__':
    run()