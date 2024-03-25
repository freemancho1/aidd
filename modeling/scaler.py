import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

import aidd.sys.config as cfg
from aidd.sys.utils import Logs
from aidd.sys.data_io import read_data, save_data


# 이 클래스는 'Modeling'부분과 'Serving'부분을 구분해서 구현
class Scaling:
    def __init__(self, ppdf=None):
        self._logs = Logs('SCALING')
        self.ppdf = ppdf
        self.data = {}
        self.sdata = {}
        self._run()
        
    def _run(self):
        self._split_Xy()
        for pckey in cfg.PC_TYPEs[1:]:
            self._split_pckey(pckey=pckey)
        for pckey in cfg.PC_TYPEs:
            self._split_train_test(pckey=pckey)
        for pckey in cfg.PC_TYPEs:
            self._scaling(pckey=pckey)
        self._logs.stop()
        
    def _split_Xy(self):
        df = self.ppdf
        
        # TARGET 컬럼 지정
        target_col = cfg.COLs['TARGET']
        # 학습 컬럼 지정
        training_cols = df.columns[4:].tolist()
        # 모델링 컬럼정보 저장
        save_data(training_cols, fcode='DUMP,MODELING_COLS')
        
        # X, y값 분리
        X = df[training_cols].copy()
        y = df[target_col].copy()
        self._logs.mid('SOURCE_X', X.shape)
        
        self.data['X_ALL'] = X
        self.data['y_ALL'] = y
        
        # 학습 데이터 저장
        save_data(X, fcode='SCALING,X,ALL')
        save_data(y, fcode='SCALING,y,ALL')
        
    def _split_pckey(self, pckey=None):
        _X = self.data['X_ALL']
        _y = self.data['y_ALL']
        
        if pckey == '1':
            conditions = _X.POLE_CNT == 1
            X, y = _X[conditions], _y[conditions]
        else:
            conditions = _X.POLE_CNT != 1
            X, y = _X[conditions], _y[conditions]
        self._logs.mid('PC_TYPE_X', f'[{pckey}]의 속성 데이터 크기 {X.shape}')
        
        self.data[f'X_{pckey}'] = X
        self.data[f'y_{pckey}'] = y
        
        # 학습 데이터 저장
        save_data(X, fcode=f'SCALING,X,{pckey}')
        save_data(y, fcode=f'SCALING,y,{pckey}')
        
    def _split_train_test(self, pckey=None):
        X = self.data[f'X_{pckey}']
        y = self.data[f'y_{pckey}']
        
        train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.2)
        msg = f'PC_TYPE[{pckey}] Total{X.shape}, Train{train_X.shape}, ' \
              f'Test{test_X.shape}'
        self._logs.mid('PC_TYPE_TT', value=msg)
        
        self.data[f'TRAIN_X_{pckey}'] = train_X
        self.data[f'TRAIN_y_{pckey}'] = train_y
        self.data[f'TEST_X_{pckey}'] = test_X
        self.data[f'TEST_y_{pckey}'] = test_y
        
    def _scaling(self, pckey=None):
        train_X = self.data[f'TRAIN_X_{pckey}']
        test_X = self.data[f'TEST_X_{pckey}']
        
        cols = train_X.columns.tolist()
        scaler = StandardScaler()
        train_sX = scaler.fit_transform(train_X)
        test_sX = scaler.transform(test_X)

        train_sX_df = pd.DataFrame(train_sX, columns=cols)
        test_sX_df = pd.DataFrame(test_sX, columns=cols)
        
        # 클래스에 저장
        self.sdata[f'TRAIN_X_{pckey}'] = train_sX_df
        self.sdata[f'TRAIN_y_{pckey}'] = self.data[f'TRAIN_y_{pckey}']
        self.sdata[f'TEST_X_{pckey}'] = test_sX_df
        self.sdata[f'TEST_y_{pckey}'] = self.data[f'TEST_y_{pckey}']
        
        # 이 부분은 굳이 저장할 필요가 있나 싶음
        save_data(train_sX_df, fcode=f'SCALING,TRAIN_X,{pckey}')
        save_data(self.data[f'TRAIN_y_{pckey}'], f'SCALING,TRAIN_y,{pckey}')
        save_data(test_sX_df, fcode=f'SCALING,TEST_X,{pckey}')
        save_data(self.data[f'TEST_y_{pckey}'], f'SCALING,TEST_y,{pckey}')
        
        # 스케일러 저장
        save_data(scaler, fcode=f'DUMP,SCALER,{pckey}')
