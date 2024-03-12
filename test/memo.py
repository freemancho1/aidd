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
        self.all_train_X = None
        self.all_test_X = None
        self.spc_train_X = None
        self.spc_test_X = None
        self.train_y = None
        self.test_y = None
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
        
        # 훈련/시험 데이터 분리
        train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.2)
        logs.mid('TRAIN_X', train_X.shape)
        logs.mid('TEST_X', test_X.shape)
        
        # 데이터 저장
        if cfg.IS_SAVE_TEMPFILE:
            save_data(train_X, pmode='SCALING', file_code='TRAIN_X')
            save_data(train_y, pmode='SCALING', file_code='TRAIN_y')
            save_data(test_X, pmode='SCALING', file_code='TEST_X')
            save_data(test_y, pmode='SCALING', file_code='TEST_y')
        ## 클래스에 저장
        self.all_train_X = train_X
        self.train_y = train_y
        self.all_test_X = test_X
        self.test_y = test_y
        
        logs.stop()
        
    def _scaling(self):
        self._scaling_main()
        self._scaling_main(mode='SPC')
    
    def _scaling_main(self, mode='ALL'):
        # 스케일링 데이터 불러오기
        train_X = self.all_train_X
        test_X = self.all_test_X
        
        # 특수 컬럼으로 스케일링 할 경우
        if mode == 'SPC':   
            special_columns = cfg.SPECIAL_COLUMNS
            train_X = train_X[special_columns].copy()
            test_X = test_X[special_columns].copy()
            # 데이터 저장
            if cfg.IS_SAVE_TEMPFILE:
                save_data(train_X, pmode='SCALING', file_code='SPC_TRAIN_X')
                save_data(test_X, pmode='SCALING', file_code='SPC_TEST_X')
            self.spc_train_X = train_X
            self.spc_test_X = test_X
        
        # 전체 데이터 스케일링
        self._scaling_process(train_X, test_X, mode=mode, dmode='ALL')
        # 전주 갯 수가 1인 데이터 스케일
        # train_X_1 = train_X[]
            
        # 전주 갯 수가 1개인 데이터 스케일링
        
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
        self.sdata[f'{mode}_TRAIN_{dmode}'] = scaling_train_X_df
        self.sdata[f'{mode}_TEST_{dmode}'] = scaling_test_X_df
        
    
        