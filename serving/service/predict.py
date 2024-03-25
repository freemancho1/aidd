import aidd.sys.config as cfg
import aidd.sys.messages as msg
from aidd.sys.data_io import read_data


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
        
    def predict(self):
    # def predict(self, service_df):
        # df = service_df
        # r_df = df[['CONS_ID', 'TOTAL_CONS_COST']].copy()
        # r_tcc = []  # r_tcc: result total cons cost
        # X = df[self.t_cols]
        
        # for _, row in X.iterrows():
        #     row_df = pd.DataFrame(row).transpose()
        #     # 인덱스 초기화: row_df의 첫 row의 인덱스를 '0'으로 통일
        #     row_df.reset_index(drop=True, inplace=True)
        #     # 각 row별로 pckey 저장
        #     pckey = row_df.loc[0, cfg.PC_COL].astype(int)
        #     # 각 전주 갯 수 별 스케일러와 해당 갯 수의 최고 메델 가져오기
        #     if pckey == 1:
        #         scaler = self.mr_pkl['1']['SCALER']
        #         model = self.mr_pkl['1']['MODEL']
        #     else:
        #         scaler = self.mr_pkl['N1']['SCALER']
        #         model = self.mr_pkl['N1']['MODEL']
        #     # 전체 데이터에 대한 스케일러와 최고 모델 가져오기
        #     a_scaler = self.mr_pkl['ALL']['SCALER']
        #     a_model = self.mr_pkl['ALL']['MODEL']
            
        #     pred = model.predict(scaler.transform(row_df))[0]
        #     a_pred = a_model.predict(a_scaler.transform(row_df))[0]
        #     r_tcc.append([pred, a_pred])
        # r_df.loc[:, ['PCKEY_TCC', 'ALL_TCC']] = r_tcc
        # return r_df
        return 'Okkkkkkkkk'