import json
import random
import pandas as pd

import aidd.sys.config as cfg
from aidd.sys.data_io import get_merged_data

# 웹으로 JSON데이터를 입력받아,
# 리턴용 JSON데이터와 공사비 예측 입력용 데이터프레임 생성
def json_to_df(data):
    d_dict = data if isinstance(data, dict) else json.loads(data)
    # json_dict: 공사비 예측 결과 리턴할 json 데이터
    # df_dict: 공사비 예측 입력용 데이터프레임
    json_dict, df_dict = {}, {}
    
    basic = d_dict['BASIC']
    cons_id = basic['ACC_NO']
    
    for key, value in d_dict['PREDICT'].items():
        df_dict[key] = {}
        json_dict[key], df_dict[key]['CONS'] = \
            _make_cons_df(value, basic)
        for k in cfg.DATA_SETs[1:]:
            df_dict[key][k] = \
                eval(f'_make_{k.lower()}_df(value, cons_id)')
            
    return json.dumps(json_dict, ensure_ascii=False), df_dict

# 병합된 데이터를 이용해 웹에서 공사비 예측을 요청할 수 있는 JSON 데이터 생성
# - 임의의 데이터 3개를 추출해 첫번째 공사번호를 접수번호로 하고,
# - 나머지 두개의 추천번호(총3개) 데이터를 JSON으로 생성함
def get_sample_data(mdict=None):
    mdict = get_merged_data() if mdict is None else mdict
    skey = random.sample(mdict['CONS']['CONS_ID'].tolist(), k=3)
    sdict = {}
    for key in skey:
        sub_dict = {}
        for fkey in mdict.keys():
            df = mdict[fkey]
            df = df[df.CONS_ID==key].copy()
            sub_dict[fkey] = df
        sdict[key] = sub_dict
    return _make_sample_json(sdict)

def _make_sample_json(sdict=None):
    jdict = {}
    acc_no = None
    pred_no = 1
    jdict['BASIC'], jdict['PREDICT'] = {}, {}
    for idx, row in sdict.items():
        # 아래 세 행은 한번만 수행해야 하기 때문에 조건문 지정
        if acc_no is None:
            acc_no = idx
            jdict['BASIC'] = _make_basic(row['CONS'])
    
        jdict['PREDICT'][f'PRED_{pred_no}'] = {
            'BASIC': {
                'PRED_NO': pred_no,
                'PRED_TYPE': pred_no,
                'TOTAL_CONS_COST': int(row['CONS']['TOTAL_CONS_COST'].values[0]),
            },
            'POLE': {},
            'LINE': {},
            'SL': {}
        }
        for key in cfg.DATA_SETs[1:]:
            df = row[key]
            jdict['PREDICT'][f'PRED_{pred_no}'][key], \
                jdict['PREDICT'][f'PRED_{pred_no}']['BASIC'][f'{key}_CNT'] = \
                    eval(f'_make_{key.lower()}(df, key)')
        
        pred_no += 1
            
    jdict = json.dumps(jdict, ensure_ascii=False)
    return jdict
        
def _make_basic(df):
    df = df.rename(columns={
        'CONS_ID': 'ACC_NO', 'LAST_MOD_DATE': 'ACC_DATE',
    })
    df.drop(columns=[
        'CONS_TYPE_CD', 'LAST_MOD_EID', 'TOTAL_CONS_COST'
    ], inplace=True)
    dict = df.to_dict(orient='index')
    return list(dict.values())[0]

def _make_pole(df, key):
    df[['GEO_X', 'GEO_Y', 'TEMP1', 'TEMP2']] = \
        df.COORDINATE.str.split(',', expand=True)
    df = df.drop(columns=([
        'TEMP1', 'TEMP2', 'COORDINATE', 'COMP_ID', 'CONS_ID'
    ]))
    return _make_df_to_json(df, key)

def _make_line(df, key):
    df = df.drop(columns=([
        'COMP_ID', 'CONS_ID', 'COORDINATE', 'FROM_COMP_ID'
    ]))
    return _make_df_to_json(df, key)

def _make_sl(df, key):
    df = df.drop(columns=(['COMP_ID', 'CONS_ID']))
    return _make_df_to_json(df, key)

def _make_df_to_json(df, key):
    dict = {}
    idx = 1
    for _, row in df.iterrows():
        dict[f'{key}_{idx}'] = row.to_dict()
        dict[f'{key}_{idx}'][f'{key}_SEQ'] = idx
        idx += 1
    return dict, idx-1
            
def _make_cons_df(value, super_basic):
    js = value
    # 결과값의 'BASIC' 딕셔너리에 'ACC_NO'와 이후 예측결과를 담을
    # 'PRED_CONS_COST' key 추가
    js['BASIC'].update({
        'ACC_NO': super_basic['ACC_NO'], 
    })
    cdict = js['BASIC']
    cdict.update({
        'LAST_MOD_DATE': super_basic['ACC_DATE'],
        'OFFICE_NAME': super_basic['OFFICE_NAME'],
        'CONT_CAP': super_basic['CONT_CAP'],
        'ACC_TYPE_NAME': super_basic['ACC_TYPE_NAME']
    })
    
    df = pd.DataFrame([cdict])
    df = df.rename(columns={'ACC_NO': 'CONS_ID'})    
    return js, df
    
def _make_pole_df(value, cons_id):
    df = pd.DataFrame(value['POLE']).T.reset_index(drop=True)
    df['CONS_ID'] = cons_id
    df['COORDINATE'] = df.apply(lambda row: f'{row["GEO_X"]},{row["GEO_Y"]},1,1', axis=1)
    df = df.drop(columns=['GEO_X', 'GEO_Y'])
    return df

def _make_line_df(value, cons_id):
    df = pd.DataFrame(value['LINE']).T.reset_index(drop=True)
    df['CONS_ID'] = cons_id
    df = df.drop(columns=['LINE_SEQ'])
    return df

def _make_sl_df(value, cons_id):
    df = pd.DataFrame(value['SL']).T.reset_index(drop=True)
    df['CONS_ID'] = cons_id
    df = df.drop(columns=['SL_SEQ'])
    return df

if __name__ == '__main__':
    data = get_sample_data()
    print(data)