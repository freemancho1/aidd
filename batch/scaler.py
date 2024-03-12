import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

import aidd.sys.config as cfg
from aidd.sys.utils import Logs, AiddException
from aidd.batch.data_manager import save_data

class Scaling:
    def __init__(self, pdf):
        self._logs = Logs('BATCH_SCALING')
        self.pdf = pdf
        self.data = {}
        self.sdata = {}
        self.scaler = {}
        self.dmode = cfg.DMODE
        self._run()
        
    def _run(self):
        self._split_Xy()
        self._scaling()
        self._logs.stop()
    
    def _split_Xy(self):
        logs = Logs('SPLIT_DATA')
        # 스케일링 대상 데이터(전처리 데이터) 불러오기
        df = self.pdf
        logs.mid('SOC', df.shape)
        
        # TARGET 컬럼 지정
        target_column = 'TOTAL_CONS_COST'
        # 학습에 사용할 컬럼 지정
        training_columns = df.columns[6:].tolist()
        # X, y값 분리
        X = df[training_columns+[target_column]].copy()
        X.drop(columns=[c for c in X.columns if c.endswith('_COMP_ID')], inplace=True)
        y = X.pop(target_column)
        logs.mid('NORMAL_X', X.shape)
        
        self.data['X'] = X
        self.data['y'] = y

        # 데이터 저장
        if cfg.IS_SAVE_TEMPFILE:
            save_data(X, pmode='SCALING', file_code='X')
            save_data(y, pmode='SCALING', file_code='y')
            
        for dm in self.dmode:
            self._split_dmode(logs, dmode=dm)
        
        logs.stop()
        
    def _split_dmode(self, logs, dmode='ALL'):
        _X = self.data['X']
        _y = self.data['y']
        if dmode=='ALL':
            X = _X
            y = _y
        elif dmode=='1':
            X = _X[_X.REAL_POLE_CNTS==1]
            y = _y[_X.REAL_POLE_CNTS==1]
        else:
            X = _X[_X.REAL_POLE_CNTS!=1]
            y = _y[_X.REAL_POLE_CNTS!=1]
            
        # 훈련/시험 데이터 분리
        train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.2)
        value = f'전체{X.shape}, 훈련{train_X.shape}, 시험{test_X.shape}'
        logs.mid(dmode, value)
        
        # 데이터 저장
        if cfg.IS_SAVE_TEMPFILE:
            save_data(X, pmode='SCALING', file_code=f'X_{dmode}')
            save_data(y, pmode='SCALING', file_code=f'y_{dmode}')
        ## 클래스에 저장
        self.data[f'TRAIN_X_{dmode}'] = train_X
        self.data[f'TRAIN_y_{dmode}'] = train_y 
        self.data[f'TEST_X_{dmode}'] = test_X 
        self.data[f'TEST_y_{dmode}'] = test_y
        
    def _scaling(self):
        logs = Logs('SCALING_DATA')
        for dm in self.dmode:
            self._scaling_main(dmode=dm)
        logs.stop()
    
    def _scaling_main(self, dmode='ALL'):
        # 스케일링 데이터 불러오기
        train_X = self.data[f'TRAIN_X_{dmode}']
        test_X = self.data[f'TEST_X_{dmode}']
        
        # 데이터 스케일링
        self._scaling_process(train_X, test_X, mode='ALL', dmode=dmode)
        
        # 특수 컬럼으로 스케일링 할 경우
        special_columns = cfg.SPECIAL_COLUMNS
        train_X = train_X[special_columns].copy()
        test_X = test_X[special_columns].copy()
        
        # 데이터 스케일링
        self._scaling_process(train_X, test_X, mode='SPC', dmode=dmode)
        
    def _scaling_process(self, train_X, test_X, mode='ALL', dmode='ALL'):
        columns = train_X.columns.tolist()
        scaler = StandardScaler()
        scaling_train_X = scaler.fit_transform(train_X)
        scaling_test_X = scaler.transform(test_X)
        scaling_train_X_df = pd.DataFrame(scaling_train_X, columns=columns)
        scaling_test_X_df = pd.DataFrame(scaling_test_X, columns=columns)
        # 저장
        if cfg.IS_SAVE_TEMPFILE:
            save_data(scaling_train_X_df, 'SCALING', f'{mode}_TRAIN_{dmode}')
            save_data(scaling_test_X_df, 'SCALING', f'{mode}_TEST_{dmode}')
        # 클래스에 저장
        self.scaler[f'{mode}_{dmode}'] = scaler
        self.sdata[f'{mode}_TRAIN_X_{dmode}'] = scaling_train_X_df
        self.sdata[f'{mode}_TEST_X_{dmode}'] = scaling_test_X_df
        
    
        