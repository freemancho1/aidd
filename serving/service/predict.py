import pandas as pd

import aidd.sys.config as cfg
import aidd.sys.messages as msg
from aidd.sys.data_io import read_data
from aidd.modeling.preprocessing import Preprocessing


class Predict: 
    def __init__(self):
        self.model = {
            pckey: read_data(f'DUMP,MODELS,{pckey},BEST') \
                for pckey in cfg.PC_TYPEs
        }
        self.scaler = {
            pckey: read_data(f'DUMP,SCALER,{pckey}') \
                for pckey in cfg.PC_TYPEs
        }
        self.training_cols = read_data('DUMP,MODELING_COLS')
        print(msg.SYS['PREDICTION_SERVICE_READY'])
        
    def predict(self, service_dict):
        data_dict = self._online_preprocessing(service_dict)
        r_dict = {}
        for dkey in data_dict.keys():
            print(f'== {data_dict[dkey].loc[:, ["WIRING_SCHEME_OW", "LINE_TYPE_22.0"]]}')
            s_df = data_dict[dkey].copy()
            X = s_df[self.training_cols].reset_index(drop=True)
            r_dict[dkey] = { 
                'CONS_ID': s_df.loc[0, 'CONS_ID'],
                'TOTAL_CONS_COST': s_df.loc[0, 'TOTAL_CONS_COST'],
            }
            pckey = X.loc[0, cfg.PC_COL].astype(int)
            scaler = self.scaler['1'] if pckey==1 else self.scaler['N1']
            model = self.model['1'] if pckey==1 else self.model['N1']
            # 전주 수에 따라 분할된 모델로 예측한 결과
            print(X.shape, X)
            # 컬럼에 NaN이 있는 컬럼 출력
            print('++ service/predict')
            # print(f'-- service/predict: {X.loc[0, ["WIRING_SCHEME_OW", "LINE_TYPE_22.0"]]}')
            print(X.columns[X.isnull().any()].tolist())
            x_scaler = scaler.transform(X)
            pred1 = model.predict(x_scaler)[0]
            # pred1 = model.predict(scaler.transform(X))[0]
            # 전체 데이터로 모델 예측한 결과
            pred2 = self.model['ALL'].predict(self.scaler['ALL'].transform(X))[0]
            r_dict[dkey].update({'PRED1': pred1, 'PRED2': pred2})
        return r_dict
    
    def _online_preprocessing(self, s_dict):
        # 공사비 예측을 위한 입력데이터에서 모델 예측에 필요한 컬럼만 추출
        d_dict = {} # 모델링에 필요한 컬럼만 추출한 각 설비 데이터
        p_dict = {} # 모델링에 사용할 전처리 데이터
        for pn_key in s_dict.keys():
            d_dict[pn_key] = {}
            for f_key in s_dict[pn_key].keys():
                d_dict[pn_key][f_key] = \
                    s_dict[pn_key][f_key][cfg.COLs['PP'][f_key]['SOURCE']]
            pp = Preprocessing(
                d_dict[pn_key], is_modeling=False, is_preparation=False
            )
            p_dict[pn_key] = pp.ppdf
        return p_dict
