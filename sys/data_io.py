import os
import pickle
import pandas as pd
from datetime import datetime

import aidd.sys.config as cfg
from aidd.sys.utils import Logs


def read_data(fcode=None, **kwargs):
    ftype, fpath = _get_file_path(fcode)
    if ftype == 'pickle':
        with open(fpath, 'rb') as f:
            return pickle.load(f)
    else:
        _, fext = os.path.splitext(fpath)
        if fext.lower() == '.xlsx':
            return pd.read_excel(fpath, **kwargs)
        if fext.lower() == '.csv':
            return pd.read_csv(fpath, **kwargs)
        
def save_data(data=None, fcode=None, **kwargs):
    ftype, fpath = _get_file_path(fcode)
    if ftype == 'pickle':
        with open(fpath, 'wb') as f:
            pickle.dump(data, f)
    else:
        # 데이터프레임 저장 시 인덱스를 저장하지 않음
        if 'index' not in kwargs:
            kwargs['index'] = False
        data.to_csv(fpath, **kwargs)
        
def get_provide_data():
    logs = Logs('GET_PROVIDE_DATA')
    data = {}
    for key in cfg.DATA_SETs:
        start_time = datetime.now()
        df = read_data(f'PROVIDE,{key}')
        df.rename(columns=_get_rename_cols(df.columns), inplace=True)
        data[key] = df
        value = f'크기{df.shape}, 처리시간({datetime.now()-start_time})'
        logs.mid(dcode=key, value=value)
    logs.stop()
    return data

def get_merged_data():
    logs = Logs('GET_MERGED_DATA')
    data = {}
    for key in cfg.DATA_SETs:
        start_time = datetime.now()
        df = read_data(f'MERGE,BATCH,{key}')
        data[key] = df
        value = f'크기{df.shape}, 처리시간({datetime.now()-start_time})'
        logs.mid(dcode=key, value=value)
    logs.stop()
    return data

def _get_file_path(fcode=None):
    fcodes = fcode.split(',')
    ftype = 'pickle' if fcodes[0] == 'DUMP' else 'data'
    fkeys = ''.join([f'["{key}"]' for key in fcodes])
    fname = eval('cfg.FILE_NAMEs'+fkeys)
    plist = [cfg.BASE_PATH, ftype, fname]   # path list
    return ftype, os.path.join(*plist)

# 영문으로 변경할 컬럼을 '한글명':'영문명' 형식의 딕셔너리로 변환
def _get_rename_cols(cols=[]):
    return {
        name: cfg.COLs['RENAME'][name] \
            for name in cfg.COLs['RENAME'] if name in cols
    }


if __name__ == '__main__':
    print(_get_file_path('DUMP,SCALER,N1'))