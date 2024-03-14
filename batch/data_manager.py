import os
import pickle
import pandas as pd
from datetime import datetime

import aidd.sys.config as cfg
from aidd.sys.utils import Logs, AiddException


def _get_file_path(pmode=None, file_code=None, is_temp=False):
    try:
        file_name = cfg.FILE_NAME[pmode][file_code]
        if pmode != 'PROVIDE':
            file_name += cfg.TEMP_FILE_EXT if is_temp else cfg.FILE_EXT
        path_list = [cfg.BASE_DATA_PATH, file_name]
        return os.path.join(*path_list)
    except Exception as e:
        raise AiddException('GET_FILE_PATH_ERR')
    
def read_data(pmode=None, file_code=None, is_temp=False, **kwargs):
    if pmode is None:
        raise AiddException('NO_PROCESS_MODE')
    if file_code is None:
        raise AiddException('NO_FILE_CODE')
    try:
        file_path = _get_file_path(pmode, file_code, is_temp)
    except AiddException as ae:
        raise AiddException('READ_DATA_ERR', super_err=ae)
    
    try:
        _, file_ext = os.path.splitext(file_path)
        if file_ext.lower() == '.xlsx':
            return pd.read_excel(file_path, **kwargs)
        if file_ext.lower() == '.csv':
            return pd.read_csv(file_path, **kwargs)
    except Exception as e:
        raise AiddException('NONEXISTENT_FILE_PATH', file_path, e)
    
def get_rename_columns(columns):
    return {
        name: cfg.COMMON_COLUMNS[name] \
            for name in cfg.COMMON_COLUMNS if name in columns
    }
    
def save_data(df, pmode=None, file_code=None, is_temp=False, **kwargs):
    if pmode is None:
        raise AiddException('NO_PROCESS_MODE')
    if file_code is None:
        raise AiddException('NO_FILE_CODE')
    try:
        file_path = _get_file_path(pmode, file_code, is_temp)
    except AiddException as ae:
        raise AiddException('SAVE_DATA_ERR', super_err=ae)
    
    if 'index' not in kwargs:
        kwargs['index'] = False
    try:
        df.to_csv(file_path, **kwargs)
    except Exception as e:
        raise AiddException('SAVE_DATA_ERR2', super_err=e)
    
def get_provide_data():
    logs = Logs('GET_PROVIDE_DATA')
    provide_data = {}
    try:
        for dtype in cfg.DATA_TYPE:
            start_time = datetime.now()
            pdata = read_data('PROVIDE', dtype)
            pdata.rename(columns=get_rename_columns(pdata.columns), inplace=True)
            provide_data[dtype] = pdata
            value = f'읽은 데이터: {dtype}, 데이터 크기: {pdata.shape}, ' \
                    f'처리시간: {datetime.now()-start_time}'
            logs.mid(value=value)
    except AiddException as ae:
        raise AiddException('GET_PROVIDED_DATA_ERR', dtype, ae)
    except Exception as e:
        raise AiddException('GET_PROVIDED_DATA_ERR', super_err=e)
    finally:
        logs.stop()
    return provide_data

def get_merged_data(pmode='MB'):
    logs = Logs('GET_MERGED_DATA')
    merged_data = {}
    try:
        for key in cfg.DATA_TYPE:
            start_time = datetime.now()
            mdata = read_data(pmode, key)
            merged_data[key] = mdata
            value = f'읽은 데이터: {key}, 데이터 크기: {mdata.shape}, ' \
                    f'처리시간: {datetime.now()-start_time}'
            logs.mid(value=value)
    except AiddException as ae:
        raise AiddException('GET_MERGED_DATA_ERR', key, ae)
    except Exception as e:
        raise AiddException('GET_MERGED_DATA_ERR', super_err=e)
    finally:
        logs.stop()
    return merged_data

def _get_pickle_path(pmode=None, fcode=None):
    file_name = cfg.FILE_NAME[pmode][fcode]
    path_list = [cfg.BASE_DATA_PATH, 'pkl', file_name]
    return os.path.join(*path_list)
    
def load_pickle(pmode=None, fcode=None):
    file_path = _get_pickle_path(pmode, fcode)
    with open(file_path, 'rb') as f:
        loaded_data = pickle.load(f)
    return loaded_data

def save_pickle(pkl=None, pmode=None, fcode=None):
    file_path = _get_pickle_path(pmode, fcode)
    with open(file_path, 'wb') as f:
        pickle.dump(pkl, f)