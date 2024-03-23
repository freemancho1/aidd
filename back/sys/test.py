import pandas as pd

import aidd.sys.config as cfg
from aidd.sys.utils import Logs
from aidd.sys.data_io import read_data

class Service:
    def __init__(self):
        self.mr_pkl = {     # modeling result pickle[scaler, model]
            pckey: {
                'SCALER': read_data(f'DUMP,SCALER,{pckey}'),
                'MODEL': read_data(f'DUMP,MODELS,{pckey},BEST'),
            } for pckey in cfg.DATA_PC_TYPE
        }
        # t_cols : training columns
        self.t_cols = read_data(fcode='DUMP,MODELING_COLS')
        print('예측서비스 준비 완료')
      
    def predict(self):  
        print('예측서비스 수행')
        return 'Okkkkkkkkk'
    
def ymd(fmt):
    def trans(date_str):
        return datetime.strptime(date_str, fmt)
    return trans
와
def ymd(fmt, date_str):
    return datetime.strptime(date_str, fmt)
