import os
import pickle
import pandas as pd
from datetime import datetime

import aidd.sys.config as cfg

# is_dump=True: Data file
# is_dump=False: Memory Data(pickle, model)
def _get_file_path(file_code=None, is_dump=False):
    file_key = ''.join([f"['{key}']" for key in file_code.split(',')])
    file_name = eval('cfg.FILE_NAMEs' + file_key)
    file_type = 'dump' if is_dump else 'data'
    path_list = [cfg.BASE_PATH, file_type, file_name]
    return os.path.join(*path_list)

def read_data(file_code=None, **kwargs):
    file_path = _get_file_path(file_code)
    _, file_ext = os.path.splitext(file_path)
    if file_ext.lower() == '.xlsx':
        return pd.read_excel(file_path, **kwargs)
    if file_ext.lower() == '.csv':
        return pd.read_csv(file_path, **kwargs)
    
def save_data(df, file_code=None, **kwargs):
    file_path = _get_file_path(file_code)
    # 데이터프레임 저장 시 인덱스 저장을 강제로 막음
    if 'index' not in kwargs:
        kwargs['index'] = False
    df.to_csv(file_path, **kwargs)
    
def read_pickle(file_code=None):
    file_path = _get_file_path(file_code, is_dump=True)
    with open(file_path, 'rb') as f:
        return pickle.load(f)
    
def save_pickle(mem_data=None, file_code=None):
    file_path = _get_file_path(file_code, is_dump=True)
    with open(file_path, 'wb') as f:
        pickle.dump(mem_data, f)
        
# 영문으로 변경할 컬럼의 영문명 추출
def _get_rename_cols(cols=[]):
    return {
        name: cfg.COLS['RENAME'][name] \
            for name in cfg.COLS['RENAME'] if name in cols
    }
    
def get_provide_data():
    df_dict = {}
    for key in cfg.DATA_SETs:
        s_time = datetime.now()
        df = read_data(f'PROVIDE,{key}') 
        df.rename(columns=_get_rename_cols(df.columns), inplace=True)
        df_dict[key] = df
        msg = f'Data Type: {key}, Size: {df.shape}, pTime: {datetime.now()-s_time}'
        print(msg)
    return df_dict 

def get_merged_data(mode='BATCH', **kwargs):
    df_dict = {}
    for key in cfg.DATA_SETs:
        s_time = datetime.now()
        df = read_data(f'MERGE,{mode},{key}', **kwargs)
        df_dict[key] = df
        msg = f'Data Type: {key}, Size: {df.shape}, pTime: {datetime.now()-s_time}'
        print(msg)
    return df_dict

def get_modeling_data():
    mdata_dict = {}
    for key in cfg.DATA_PC_TYPE:
        mdata_dict[key] = {}
        for mkey in cfg.DATA_MD_TYPE:
            mdata_dict[key][mkey] = read_data(f'SCALING,{mkey},{key}')
    return mdata_dict

if __name__ == '__main__':
    _get_file_path('PROVIDE,SL')
    _get_file_path('MERGE,ONLINE,POLE')
    _get_file_path('PP,LINE')