import pandas as pd
from sklearn.exceptions import ConvergenceWarning

import aidd.sys.config as cfg
from aidd.sys.utils import Logs
from aidd.sys.data_io import save_data
from aidd.modeling.evaluations import regression_evals


class Learning:
    def __init__(self, mdata=None):
        self._logs = Logs('LEARNING')
        self.mdata = mdata
        self.best = {
            pckey: {'MODEL': None, 'SCORE': 0, 'MODEL_KEY': ''} \
                for pckey in cfg.PC_TYPEs
        }
        self.history = {}
        self._run()
        
    def _run(self):
        for mkey in cfg.MODEL_KEYs:
            for pckey in cfg.PC_TYPEs:
                self._ml_model_fit_evals(mkey=mkey, pckey=pckey)
        # 최고 모델 저장
        for pckey in cfg.PC_TYPEs:
            save_data(self.best[pckey]['MODEL'], f'DUMP,MODELS,{pckey},BEST')
        save_data(self.history, fcode='DUMP,MODELING_HISTORY')
        self._logs.stop()
        
    def _ml_model_fit_evals(self, mkey=None, pckey=None):
        model = cfg.MODELs['ML'][mkey]
        data = {key: self.mdata[f'{key}_{pckey}'] for key in cfg.DATA_TYPEs}
        train_y = data['TRAIN_y'].to_numpy().reshape(-1)
        try:
            # model.fit(data['TRAIN_X'], data['TRAIN_y'])
            model.fit(data['TRAIN_X'], train_y)
        except ConvergenceWarning as ce:
            # 모델이 정상적으로 수렴되지 않을 때 발생하는 오류로,
            # LASSO 알고리즘으로 메델 생성시 발생함(무시해도 됨)
            pass
        pred = model.predict(data['TEST_X'])
        evals = regression_evals(y=data['TEST_y'].to_numpy(), p=pred, verbose=0)
        self._save_history(mkey, pckey, evals, model)
        
    def _save_history(self, mkey=None, pckey=None, evals=None, model=None):
        # msg = f'MODEL[{mkey}], PC KEY[{pckey}], EVALS{evals}'
        # self._logs.mid('RESULT', msg)
        # 알고리즘별, 전주 숫자별 모델 저장
        save_data(model, fcode=f'DUMP,MODELS,{pckey},{mkey}')
        # 학습결과 저장
        self.history[f'({mkey}, {pckey})'] = evals
        # 전주 숫자별 최고 모델 선별(r2score가 가장 높은 모델)
        if self.best[pckey]['SCORE'] < evals[2]:
            self.best[pckey].update({
                'SCORE': evals[2], 'MODEL': model, 'MODEL_KEY': mkey
            })