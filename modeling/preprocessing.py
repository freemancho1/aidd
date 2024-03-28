import re
import pandas as pd
from io import StringIO

import aidd.sys.config as cfg
from aidd.sys.utils import Logs
from aidd.sys.data_io import read_data, save_data


class Preprocessing:
    def __init__(self, data, is_modeling=True, is_preparation=True):
        self._logs = Logs('PP', is_disp=is_modeling)
        # 제공받은 데이터(서비스에도 동일하게 들어옴)
        self.pdict = data   # provided data dictionary
        self.is_modeling = is_modeling
        self.is_preparation = is_preparation
        # 제약조건을 충족한 데이터(서비스에서도 체크 필요)
        self.ppdict = {}    # preprocessing data dictionary
        # 모델링을 위한 최종 전처리 데이터프레임
        self.ppdf = None    # preprocessing dataframe(최종 전처리 데이터)
        self._run()
        
    def _run(self):
        if self.is_preparation:
            self._preparation_data()
        else:
            self.ppdict = self.pdict
        self._cons()
        self._compute_and_check_facilities_count()
        self._pole()
        self._line()
        self._sl()
        self._pp_to_organize()
        self._logs.stop()
        
    def _preparation_data(self):
        logs = Logs('PREPARATION', is_disp=self.is_modeling)
        # 공사비 데이터 학습대상 레코드 추출
        key = cfg.DATA_SETs[0]
        df = self.pdict[key]
        # (전주/전선 수를 제외한) 공사비 데이터 부분에서 학습 대상 레코드 조건
        # * 접수종류명(ACC_TYPE_NAME), 계약전력(CONT_CAP), 총공사비(TOTAL_CONS_COST)
        modeling_recs = \
            (df.ACC_TYPE_NAME  == cfg.CONSTRAINTs['ACC_TYPE_NAME']) & \
            (df.CONT_CAP        < cfg.CONSTRAINTs['MAX_CONT_CAP']) & \
            (df.TOTAL_CONS_COST < cfg.CONSTRAINTs['MAX_TOTAL_CONS_COST'])
            # (df.CONS_TYPE_CD   == cfg.CONSTRAINTs['CONS_TYPE_CD']) & \
        df = df[modeling_recs].reset_index(drop=True)
        cons_df = df[cfg.COLs['PP'][key]['SOURCE']]
        self.ppdict[key] = cons_df
        logs.mid('CONS', cons_df.shape)
        
        # 전주/전선/인입선 데이터 제약조건 처리
        # 공사비에 있는 공사번호별로 필요 컬럼만 남기고 정리
        for key in cfg.DATA_SETs[1:]:
            df = self.pdict[key]
            df = df[df.CONS_ID.isin(cons_df.CONS_ID)]
            self.ppdict[key] = df[cfg.COLs['PP'][key]['SOURCE']]
            logs.mid(key, self.ppdict[key].shape)
        
        if self.is_modeling:
            # 데이터 저장
            logs.mid('SAVE')
            for key in cfg.DATA_SETs:
                save_data(self.ppdict[key], f'MERGE,BATCH,{key}')
        
        logs.stop()

    def _cons(self):
        dt = 'CONS'     # 처리할 데이터 타입(dt)
        logs = Logs(f'PP_{dt}', is_disp=self.is_modeling)
        df = self.ppdict[dt].copy()
        logs.mid('SOURCE', df.shape)
        
        # 결측치 처리
        df.fillna(0, inplace=True)
            
        # 일자정보 처리
        # * '최종변경일시'를 이용해 다양한 일자정보 컬럼 추가
        # * 참고로 일자정보가 날자형식이 아니면 날자형식으로 변환
        if df.LAST_MOD_DATE.dtype != '<M8[ns]':
            df.LAST_MOD_DATE = pd.to_datetime(df.LAST_MOD_DATE)
        df['YEAR'] = df.LAST_MOD_DATE.dt.year
        df['MONTH'] = df.LAST_MOD_DATE.dt.month
        df['DAY'] = df.LAST_MOD_DATE.dt.day
        df['DAYOFWEEK'] = df.LAST_MOD_DATE.dt.dayofweek
        df['DAYOFYEAR'] = df.LAST_MOD_DATE.dt.dayofyear
        df['YEAR_MONTH'] = df.LAST_MOD_DATE.dt.strftime("%Y%m").astype(int)
        
        # 접수시점에 설계자 정보를 알 수 없기 때문에 모델링에서 제거
        # # 사번정보 처리
        # # '최종변경자사번(LAST_MOD_EID)'만 사용(최초등록자==최종변경자사번)
        # df['EID_NUMBER'] = df.LAST_MOD_EID.apply(
        #     lambda x: re.findall(r'\d+', x)[0]
        # ).astype(int)
        
        # 사업소명 숫자로 변환
        # 모델학습 만을 생각하면 rank()함수를 사용할 수 있지만, 
        # rank를 사용하면 서비스시에 같은 값 다른 ranking을 제공하기 때문에 문제 발생
        # 이를 해결하기 위해 학습시 사업소명을 저장하고 
        # 서비스시 해당 사업소명리스트를 이용해 숫자로 변경해줘야 함.
        if self.is_modeling:
            offc_list = df.OFFICE_NAME.unique().tolist()
            save_data(offc_list, fcode='DUMP,OFFICE_LIST')
        else:
            offc_list = read_data('DUMP,OFFICE_LIST')
        offc_idxs = []
        for oname in df.OFFICE_NAME:
            offc_idxs.append(offc_list.index(oname))
        df['OFFICE_NUMBER'] = offc_idxs
        
        # 필요 컬럼 추출
        # 'CONT_CAP', 'EID_CODE_NUMBER' 추가 필요
        df = df[cfg.COLs['PP'][dt]['PP']]
        logs.mid('RESULT', df.shape)
        
        self.ppdf = df
        print(f'+++ CONS: {[x for x in self.ppdf.columns]}')
        logs.stop()

    def _compute_and_check_facilities_count(self):
        logs = Logs('PP_COMPUTE', is_disp=self.is_modeling)
        ppdf = self.ppdf.copy()
        # 공사비까지 전처리된 데이터 셋에 설비 갯 수 컬럼 추가(3개)
        # 공사비 데이터 셋은 처리하지 않아도 됨
        for key in cfg.DATA_SETs[1:]:
            df = self.ppdict[key].copy()
            cons_ids_cnt = df.CONS_ID.value_counts()
            col_name = f'{key}_CNT'
            ppdf = pd.merge(
                ppdf, cons_ids_cnt.rename(col_name),
                left_on='CONS_ID', right_on=cons_ids_cnt.index, how='left'
            )
            # 해당 공사번호가 없는 설비는 NaN처리되기 때문에 이 값을 0으로 변경
            ppdf[col_name] = ppdf[col_name].fillna(0)
        logs.mid('COMPUTE', ppdf.shape)
        
        # 모델 학습에 사용할 레코드 추출
        # * 전주/전선 갯 수가 10개 이상인 경우 
        # * 인입선 갯 수가 1개 인 경우 ++++++++++++++++++++
        modeling_recs = \
            (ppdf.POLE_CNT >= cfg.CONSTRAINTs['MIN_POLE_CNT']) & \
            (ppdf.POLE_CNT <= cfg.CONSTRAINTs['MAX_POLE_CNT']) & \
            (ppdf.LINE_CNT >= cfg.CONSTRAINTs['MIN_LINE_CNT']) & \
            (ppdf.LINE_CNT <= cfg.CONSTRAINTs['MAX_LINE_CNT'])    
        ppdf = ppdf[modeling_recs].reset_index(drop=True)    
        logs.mid('RESULT', ppdf.shape)
        
        self.ppdf = ppdf
        print(f'+++ CNTS: {[x for x in self.ppdf.columns]}')
        logs.stop()
        
    def _pole(self):
        dt = 'POLE'     # 처리할 데이터 타입(dt)
        logs = Logs(f'PP_{dt}', is_disp=self.is_modeling)
        df = self.ppdict[dt].copy()
        logs.mid('SOURCE', df.shape)
        
        # 결측치 처리
        df.fillna(0, inplace=True)        
        
        # 코드형 컬럼 One-Hot Encoding
        prefix = ['POLE_SHAPE', 'POLE_TYPE', 'POLE_SPEC']
        cols = [x+'_CD' for x in prefix]
        # 숫자형 값 통일(실수형이 아닌 값을 실수형으로 변환)
        # (One-Hot Encoding시 동일한 컬럼값을 만들기 위해 실행)
        if df.POLE_SPEC_CD.dtype != 'float64':
            df['POLE_SPEC_CD'] = df['POLE_SPEC_CD'].astype(float)
        df = pd.get_dummies(df, columns=cols, prefix=prefix)
        # True, False값을 1, 0으로 변환
        df = df.apply(lambda x: int(x) if isinstance(x, bool) else x)
        
        # 실시간 처리에서 동일 컬럼을 추가하기 위해 학습에서 나온 컬럼 리스트 저장
        df_cols = df.columns.tolist()
        if self.is_modeling:
            save_data(df_cols, fcode='DUMP,POLE_ONE_HOT_COLS')
        else:
            # 학습 당시 컬럼 불러오기
            modeling_cols = read_data(fcode='DUMP,POLE_ONE_HOT_COLS')
            # 실시간 처리에서 만들어 지지 않는 컬럼 추출
            append_cols = [x for x in modeling_cols if x not in df_cols]
            # 0으로 컬럼값 추가
            df.loc[:, append_cols] = 0
        logs.mid('ONE_HOT', df.shape)
        
        # 공사비별 전주 데이터 합산
        unique_cons_ids = df.CONS_ID.unique()
        cons_id_pole_sums = []
        # 합산대상 컬럼 리스트 추출
        sum_cols = [col for col in df.columns if col.startswith('POLE_')]
        # 공사번호별 합산(시간이 좀 걸림, 14700건 처리에 약 40초 소요)
        for cid in unique_cons_ids:
            cons_id_pole_sums.append(
                [cid]+df[df.CONS_ID==cid][sum_cols].sum().values.tolist())
        # 공사번호별로 합산된 전주 정보를 데이터프레임으로 변환
        pole_sums_df = pd.DataFrame(
            cons_id_pole_sums, columns=['CONS_ID'] + sum_cols)
        
        # 공사비 데이터와 전주정보 그룹 데이터 병합
        ppdf = pd.merge(
            self.ppdf, pole_sums_df,
            left_on='CONS_ID', right_on='CONS_ID', how='left')
        logs.mid('RESULT', ppdf.shape)
        
        self.ppdf = ppdf
        print(f'+++ POLE: {[x for x in self.ppdf.columns]}')
        logs.stop()
        
    def _line(self):
        dt = 'LINE'     # 처리할 데이터 타입(dt)
        logs = Logs(f'PP_{dt}', is_disp=self.is_modeling)
        df = self.ppdict[dt].copy()
        logs.mid('SOURCE', df.shape)        
        
        # 숫자형 값 통일(실수형이 아닌 값을 실수형으로 변환)
        # (One-Hot Encoding시 동일한 컬럼값을 만들기 위해 실행)
        if df.LINE_SPEC_CD.dtype != 'float64':
            df['LINE_SPEC_CD'] = df['LINE_SPEC_CD'].astype(float)
        if df.NEUTRAL_SPEC_CD.dtype != 'float64':
            df['NEUTRAL_SPEC_CD'] = df['NEUTRAL_SPEC_CD'].astype(float)   
        # 중성선규격코드(NEUTRAL_SPEC_CD)에 0.0과 NaN이 존재(NaN=>999.0 변환)
        df['NEUTRAL_SPEC_CD'] = df['NEUTRAL_SPEC_CD'].fillna(999.0)
        # 중성선종류코드(NEUTRAL_TYPE_CD)의 NaN값을 문자열 'NaN'으로 치환
        df.NEUTRAL_TYPE_CD = df.NEUTRAL_TYPE_CD.fillna('NaN')
        # 결선방식이 41인 값이 1개만 존재하기 때문에 많이 있는 43으로 치환
        df.WIRING_SCHEME = df.WIRING_SCHEME.replace(41, 43)
        # 전선 전체길이 추가: = 선로길이(SPAN) * 전선 갯 수(PHASE)
        df.loc[:, 'LINE_LENGTH'] = df.SPAN * df.LINE_PHASE_CD

        # 결측치 처리
        df.fillna(0, inplace=True)
        
        # 코드형 컬럼 One-Hot Encoding
        # WIRING_SCHEME은 마지막에 '_CD'가 붙지 않음
        prefix = ['WIRING_SCHEME', 'LINE_TYPE', 'LINE_SPEC', 'LINE_PHASE',
                'NEUTRAL_TYPE', 'NEUTRAL_SPEC']
        columns = [x+'_CD' for x in prefix if x != 'WIRING_SCHEME']
        columns += ['WIRING_SCHEME']
        df = pd.get_dummies(df, columns=columns, prefix=prefix)
        # True, False를 1, 0으로 변환
        df = df.apply(lambda x: int(x) if isinstance(x, bool) else x)
        # 실시간 처리에서 동일 컬럼을 추가하기 위해 학습에서 나올 컬럼리스트 저장
        df_cols = df.columns.tolist()
        if self.is_modeling:
            save_data(df_cols, fcode='DUMP,LINE_ONE_HOT_COLS')
        else:
            modeling_cols = read_data(fcode='DUMP,LINE_ONE_HOT_COLS')
            append_cols = [col for col in modeling_cols if col not in df_cols]
            df.loc[:, append_cols] = 0
        logs.mid('ONE_HOT', df.shape)
        
        # 공사비별 전선 데이터 합산
        unique_cons_ids = df.CONS_ID.unique()
        cons_id_line_sums = []
        # 서비스시에는 1 컬럼부터 'SPAN'임, 모델링시 체크 필요
        sum_cols = df.columns.tolist()[1:]
        # sum_cols = ['SPAN'] + df.columns.tolist()[5:]
        for cid in unique_cons_ids:
            cons_id_line_sums.append(
                [cid]+df[df.CONS_ID==cid][sum_cols].sum().values.tolist())
        # 공사번호별로 합산된 전주 정보를 데이터프레임으로 변환
        line_sums_df = pd.DataFrame(
            cons_id_line_sums, columns=['CONS_ID']+sum_cols)
        
        # 공사비 데이터와 전주 그룹 데이터 병합
        ppdf = pd.merge(
            self.ppdf, line_sums_df,
            left_on='CONS_ID', right_on='CONS_ID', how='left')
        logs.mid('RESULT', ppdf.shape)
        
        self.ppdf = ppdf
        print(f'+++ LINE: {[x for x in self.ppdf.columns]}')
        logs.stop()

    def _sl(self):
        dt = 'SL'     # 처리할 데이터 타입(dt)
        logs = Logs(f'PP_{dt}', is_disp=self.is_modeling)
        df = self.ppdict[dt].copy()
        logs.mid('SOURCE', df.shape)    
        
        # 숫자형 값 통일(실수형이 아닌 값을 실수형으로 변환)
        # (One-Hot Encoding시 동일한 컬럼값을 만들기 위해 실행)
        if df.SL_SPEC_CD.dtype != 'float64':
            df['SL_SPEC_CD'] = df['SL_SPEC_CD'].astype(float)
        # 결측치 처리
        df.fillna(0, inplace=True)
        
        # 코드형 컬럼 One-Hot Encoding
        prefix = ['SL_TYPE', 'SL_SPEC']
        columns = [col+'_CD' for col in prefix]
        df = pd.get_dummies(df, columns=columns, prefix=prefix)
        df = df.apply(lambda x: int(x) if isinstance(x, bool) else x)
        # 실시간 처리에서 동일 컬럼을 추가하기 위해 학습에서 나올 컬럼리스트 저장
        df_cols = df.columns.tolist()
        if self.is_modeling:
            save_data(df_cols, fcode='DUMP,SL_ONE_HOT_COLS')
        else:
            modeling_cols = read_data('DUMP,SL_ONE_HOT_COLS')
            append_cols = [col for col in modeling_cols if col not in df_cols]
            df.loc[:, append_cols] = 0
        logs.mid('ONE_HOT', df.shape)
        
        # 공사비별 인입선 데이터 합산
        unique_cons_ids = df.CONS_ID.unique()
        cons_id_sl_sums = []
        # Service시 1 컬럼부터 'SPAN'임 (모델링시 체크 필요)
        sum_cols = df.columns.tolist()[1:]
        # sum_cols = df.columns.tolist()[2:]
        for cid in unique_cons_ids:
            _df = df[df.CONS_ID==cid]
            sl_sums = _df[sum_cols].sum().values.tolist()
            # sl_comp_id_cnt = _df.COMP_ID.nunique()
            cons_id_sl_sums.append(
                [cid, _df.shape[0]] + sl_sums)
                # [cid, sl_comp_id_cnt, _df.shape[0]] + sl_sums)
        # 데이터프레임 만들기
        sl_sums_df = pd.DataFrame(
            cons_id_sl_sums, 
            columns=['CONS_ID', 'REAL_SL_CNT', 'SL_SPAN_SUM'] \
                + sum_cols[1:]
        )
        
        # 공사비 데이터와 인입선 그룹 데이터 병합
        ppdf = pd.merge(
            self.ppdf, sl_sums_df,
            left_on='CONS_ID', right_on='CONS_ID', how='left'
        )
        logs.mid('RESULT', ppdf.shape)
        
        self.ppdf = ppdf
        print(f'+++ SL: {[x for x in self.ppdf.columns]}')
        logs.stop()

    def _pp_to_organize(self):
        # 최종 완료시점에서 NaN값을 0으로 처리
        # 온라인 작업 시 인입선이 없거나 전주가 없는 작업 등에서 NaN가 올 수 있음
        self.ppdf.fillna(0, inplace=True)
        # 모델링 시점과 서비스 시점의 데이터프레임 컬럼 순서를 동일하게 하기 위해
        # 모델링 시점의 컬럼 순서를 저장해 서비스 시점에서 컬럼 순서를 재배치
        # One-Hot Encoding시점에 데이터 컬럼의 순서가 변경될 수 있음.
        if self.is_modeling:
            last_pp_cols = self.ppdf.columns
            save_data(last_pp_cols, fcode='DUMP,LAST_PP_COLS')
        else:
            last_pp_cols = read_data('DUMP,LAST_PP_COLS')
            self.ppdf = self.ppdf.reindex(columns=last_pp_cols)
            
        print(f'+++ LAST: {[x for x in self.ppdf.columns]}')


