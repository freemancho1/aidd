import sys

from aidd.batch.data_manager import get_provide_data
from aidd.batch.preprocessing import Preprocessing
from aidd.batch.scaler import Scaling
from aidd.sys.utils import AiddInit, Logs, AiddException


def batch_main():
    logs = Logs('BATCH_MAIN')
    try:
        pdata = get_provide_data()
        pp = Preprocessing(provide_data=pdata)
        sc = Scaling(pp.pdf)
    except AiddException as ae:
        logs.mid(value=f'Error:\n{ae}')
        sys.exit()
    finally:
        logs.stop()
        
def main():
    AiddInit()
    batch_main()
    
if __name__ == '__main__':
    main()