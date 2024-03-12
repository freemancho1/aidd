import re
import pandas as pd

import aidd.sys.config as cfg
from aidd.batch.data_manager import save_data
from aidd.sys.utils import Logs, AiddException

class Preprocessing:
    def __init__(self, provide_data=None):
        self._logs = Logs('BATCH_PREPROCESSING')
        if provide_data is None:
            raise AiddException('NO_PROVIDE_DATA')
        self.pdata = provide_data               # provided data
        self.pdf = None                         # preprocessing dataframe
        self._ppoledf = None                    # 전주 순번 정하는데 사용(전주 전처리 결과 데이터)
        self._plinedf = None                    # 전선 순번 정하는데 사용(전선 전처리 결과 데이터)
        self._run()
        
    def _run(self):
        try:
            self._cons()                        # 공사비 데이터 전처리
            self._compute_facilities_count()    # 공사비별 설비 갯 수 계산
            self._pole()                        # 전주 데이터 전처리(공사비별 병합 포함)
            self._line()                        # 전선 데이터 전처리(공사비별 병합 포함)
            self._compute_seq()                 # 전주/전선 순번 지정 및 전선 갯 수 계산
            self._sl()                          # 인입선 데이터 전처리
            self._logs.stop()
        except AiddException as ae:
            raise AiddException('BATCH_PREPROCESSING_ERR', super_err=ae)
        except Exception as e:
            raise AiddException('BATCH_PREPROCESSING_SERR', super_err=e)
        
    def _cons(self):
        logs = Logs('PP_CONS')
        df = self.pdata['CONS']
        
        # 결측치 처리
        df.fillna(0, inplace=True)
        
        # 학습대상 레코드 추출
        training_conditions = \
            (df.ACC_TYPE_NAME == cfg.COND_ACC_TYPE_NAME) & \
            (df.CONT_CAP < cfg.COND_MAX_CONT_CAP) & \
            (df.CONS_TYPE_CD == cfg.COND_CONS_TYPE_CD) & \
            (df.TOTAL_CONS_COST < cfg.COND_MAX_TOTAL_CONS_COST)
        df = df[training_conditions].reset_index(drop=True)
        
        # 일자정보 처리
        # - '최종변경일시'를 이용해 다양한 일자정보 컬럼 추가
        df['YEAR'] = df.LAST_MOD_DATE.dt.year
        df['MONTH'] = df.LAST_MOD_DATE.dt.month
        df['DAY'] = df.LAST_MOD_DATE.dt.day
        df['DAYOFWEEK'] = df.LAST_MOD_DATE.dt.dayofweek
        df['DAYOFYEAR'] = df.LAST_MOD_DATE.dt.dayofyear
        df['YEAR_MONTH'] = df.LAST_MOD_DATE.dt.strftime("%Y%m").astype(int)
        
        # 사번 전처리
        # '최종변경자사번'만 사용(모든 데이터의 최초등록자와 최종변경자사번이 동일)
        # - 사번앞에 있는 영문자를 추출해 새로운 컬럼 추가(영문자가 없으면 'AAA'추가)
        df['EID_CODE'] = \
            df.LAST_MOD_EID.str.extract('([a-zA-Z]+)', expand=False)
        df.EID_CODE.fillna('AAA', inplace=True)
        # - 사번앞에 있는 영문자를 학습에 사용하기 위해 숫자로 변경(일련번호)
        df['EID_CODE_NUMBER'] = df.EID_CODE.rank(method='dense').astype(int)
        # - 사번에서 숫자만 추출해 별도 보관
        df['EID_NUMBER'] = df.LAST_MOD_EID \
            .apply(lambda x: re.findall(r'\d+', x)[0]) \
            .astype(int)
            
        # 사업소명 전처리: 한글 사업소명을 숫자 일련번호로 변경
        df['OFFICE_NUMBER'] = df.OFFICE_NAME.rank(method='dense').astype(int)
        
        # 학습 임시데이터 저장
        if cfg.IS_SAVE_TEMPFILE:
            save_data(df, pmode='PP', file_code='CONS', is_temp=True)
        
        # 학습에 필요한 컬럼 추출
        training_columns = [
            # 학습에는 사용되지 않고 데이터의 연결 또는 개발자가 참고하기 위한 데이터
            'CONS_ID', 'TOTAL_CONS_COST', 'LAST_MOD_DATE', 'LAST_MOD_EID',
            'OFFICE_NAME', 'EID_CODE', 
            # 학습에 사용되는 데이터
            'CONT_CAP',
            'YEAR', 'MONTH', 'DAY', 'DAYOFWEEK', 'DAYOFYEAR', 'YEAR_MONTH',
            'EID_CODE_NUMBER', 'EID_NUMBER',
            'OFFICE_NUMBER'
        ]
        df = df[training_columns]
        logs.mid('RESULT', df.shape)
        
        # 전처리 데이터 저장
        save_data(df, pmode='PP', file_code='CONS')
        self.pdf = df
        logs.stop()
        
    def _compute_facilities_count(self):
        logs = Logs('PP_FACILITES_COUNT')
        
        # 전처리된 공사비 데이터를 기준으로 나머지 3개의 데이터 갯 수 계산
        df = self.pdf
        for dtype in cfg.DATA_TYPE[1:]:
            temp_df = self.pdata[dtype]
            cons_ids = temp_df.CONS_ID.value_counts()
            column_name = f'{dtype}_CNT'
            df = pd.merge(df, cons_ids.rename(column_name),
                          left_on='CONS_ID', right_on=cons_ids.index, how='left')
            # 해당 공사번호에 없는 설비의 경우 'NaN'값 처리 => 이 값을 0으로 변경
            df[column_name].fillna(0, inplace=True)
            
        # 학습 임시데이터 저장
        if cfg.IS_SAVE_TEMPFILE:
            save_data(df, pmode='PP', file_code='CONS_FC', is_temp=True)
            
        # 모델링에 사용할 레코드 추출
        # 여기서는 설비 갯 수를 비교해 학습 데이터를 추출함
        training_conditions = \
            (df.POLE_CNT >= cfg.COND_MIN_POLE_COUNT) & \
            (df.POLE_CNT <= cfg.COND_MAX_POLE_COUNT) & \
            (df.LINE_CNT >= cfg.COND_MIN_LINE_COUNT) & \
            (df.LINE_CNT <= cfg.COND_MAX_LINE_COUNT)
        df = df[training_conditions]
        logs.mid('RESULT', df.shape)
        
        # 전처리 데이터 저장
        save_data(df, pmode='PP', file_code='CONS_FC')
        self.pdf = df
        logs.stop()
        
    def _pole(self):
        logs = Logs('PP_POLE')
        
        # 전처리용 전주 데이터
        df = self.pdata['POLE']
        # 학습대상 컬럼 추출
        select_columns = [
            'CONS_ID', 'COMP_ID', 
            'POLE_SHAPE_CD', 'POLE_TYPE_CD', 'POLE_SPEC_CD', 
            'COORDINATE'
        ]
        df = df[select_columns]
        
        # 전처리된 공사비 데이터에 있는 공사번호를 포함한 레코드 추출
        df = df[df.CONS_ID.isin(self.pdf.CONS_ID)]
        
        # 좌표정보(COORDINATE) 컬럼을 이용해 좌표정보 컬럼 추가
        df[['X', 'Y', 'TEMP1', 'TEMP2']] = df.COORDINATE.str.split(',', expand=True)
        df.drop(columns=['TEMP1', 'TEMP2', 'COORDINATE'], inplace=True)
        df.X, df.Y = df.X.astype(float), df.Y.astype(float)
        
        # Code형 데이터 One-Hot Encoding
        df = pd.get_dummies(
            df,
            columns=['POLE_SHAPE_CD', 'POLE_TYPE_CD', 'POLE_SPEC_CD'],
            prefix=['POLE_SHAPE', 'POLE_TYPE', 'POLE_SPEC']
        )
        # One-Hot Encoding시 bool형으로 변경되기 때문에 0, 1로 변환
        df = df.applymap(lambda x: int(x) if isinstance(x, bool) else x)
        
        # 향후 전주 데이터 순서를 정하는데 사용하기 위해 임시 저장
        self._ppoledf = df
        logs.mid('PP_POLE_ONLY', df.shape)
        
        # 공사번호별 전주 데이터 합산
        
        ## 공사번호 리스트 생성
        unique_consids = df.CONS_ID.unique()
        ## 공사번호별 전주 합산 데이터 저장
        consid_info = []
        ## 합산할 컬럼 리스트(16개 컬럼이 나옴)
        summation_columns = [col for col in df.columns if col.startswith('POLE_')]
        
        ## 공사번호별 전주 합산 데이터 계산
        for id in unique_consids:
            temp_df = df[df.CONS_ID == id]
            id_info = temp_df[summation_columns].sum().values.tolist()
            consid_info.append([id]+id_info)
        ## 공사번호별로 합산된 전주 정보를 데이터프레임으로 변환
        consid_info_df = pd.DataFrame(
            consid_info,
            columns=['CONS_ID'] + summation_columns
        )
        logs.mid('PP_POLE_SUM', consid_info_df.shape)
        
        ## 공사비 데이터와 전주 그룹데이터 병합
        pdf = pd.merge(
            self.pdf, consid_info_df,
            left_on='CONS_ID', right_on='CONS_ID', how='left'
        )
        logs.mid('PP_POLE_MERGE', pdf.shape)
        
        # 데이터 저장
        ## 임시 데이터 저장
        if cfg.IS_SAVE_TEMPFILE:
            save_data(df, pmode='PP', file_code='POLE', is_temp=True)
        ## 전처리 데이터 저장
        save_data(pdf, pmode='PP', file_code='POLE')
        ## 클래스에 저장
        self.pdf = pdf
        
        logs.stop()
        
    def _line(self):
        logs = Logs('PP_LINE')
        
        # 전처리 데이터 준비
        ## 전선 데이터 불러오기
        df = self.pdata['LINE']
        ## 학습대상 컬럼만 추출
        select_columns = [
            'CONS_ID', 'COMP_ID', 'FROM_COMP_ID',
            'WIRING_SCHEME', 'LINE_TYPE_CD', 'LINE_SPEC_CD', 'LINE_PHASE_CD',
            'SPAN', 'NEUTRAL_TYPE_CD', 'NEUTRAL_SPEC_CD', 'COORDINATE'
        ]
        df = df[select_columns].copy()
        logs.mid('PP_LINE_SOC', df.shape)
        ## 학습대상 레코드 추출
        df = df[df.CONS_ID.isin(self.pdf.CONS_ID)]
        logs.mid('PP_LINE_REC', df.shape)
        
        # 각 컬럼의 데이터 전처리
        
        ## 중성선규격코드(NEUTRAL_SPEC_CD)에 0.0과 NaN이 존재(NaN->999.0으로 치환)
        df['NEUTRAL_SPEC_CD'] = df['NEUTRAL_SPEC_CD'].fillna(999.0)
        ## 중성선종류코드(NEUTRAL_TYPE_CD)의 NaN값을 문자열 'NaN'으로 치환(다른 방법)
        df.NEUTRAL_TYPE_CD.fillna('NaN', inplace=True)
        ## 결선방식이 41인 값이 1개만 존재하기 때문에 많이 있는 43으로 치환
        df.WIRING_SCHEME = df.WIRING_SCHEME.replace(41, 43)
        
        ## 전선 전체 길이 추가
        ### 전선 전체 길이 = 선로길이(긍장, SPAN) * 전선의 갯 수(조수, PHASE)
        df.loc[:, 'LINE_LENGTH'] = df.SPAN * df.LINE_PHASE_CD
        
        ## 코드형 데이터 One-Hoe Encoding
        df = pd.get_dummies(
            df, 
            columns=[
                'WIRING_SCHEME', 'LINE_TYPE_CD', 'LINE_SPEC_CD', 'LINE_PHASE_CD',
                'NEUTRAL_TYPE_CD', 'NEUTRAL_SPEC_CD'
            ],
            prefix=[
                'WIRING_SCHEME', 'LINE_TYPE', 'LINE_SPEC', 'LINE_PHASE',
                'NEUTRAL_TYPE', 'NEUTRAL_SPEC'
            ]
        )
        ### One-Hot Encoding 결과 bool형을 int형으로 치환
        df = df.applymap(lambda x: int(x) if isinstance(x, bool) else x)
        
        logs.mid('PP_LINE_ONLY', df.shape)
        
        # 나중에 전주 순서별 전선정보 계산에 활용하기 위해 클래스에 저장
        self._plinedf = df
        
        # 공사번호별 전선 데이터 합산
        
        ## 공사번호 리스트 생성
        unique_consids = df.CONS_ID.unique()
        ## 공사번호별 전선 합산 데이터 저장 공간
        consid_info = []
        ## 합산할 컬럼 리스트(One-Hot Encoding되면서 컬럼 순서가 변경됨)
        summation_columns = ['SPAN'] + df.columns.tolist()[5:]
        ## 공사번호별 전선 합산 데이터 계산
        for id in unique_consids:
            temp_df = df[df.CONS_ID==id]
            id_info = temp_df[summation_columns].sum().values.tolist()
            consid_info.append([id]+id_info)
        ## 공사번호별로 합산된 전선 정보를 데이터프레임으로 변환
        consid_info_df = pd.DataFrame(
            consid_info,
            columns=['CONS_ID']+summation_columns
        )
        logs.mid('PP_LINE_SUM', consid_info_df.shape)
        
        # 공사비 데이터와 전선 그룹 데이터 병합
        pdf = pd.merge(
            self.pdf, consid_info_df,
            left_on='CONS_ID', right_on='CONS_ID', how='left'
        )
        logs.mid('RESULT', pdf.shape)
        
        # 데이터 저장
        ## 임시 데이터 저장
        if cfg.IS_SAVE_TEMPFILE:
            save_data(df, pmode='PP', file_code='LINE', is_temp=True)
        ## 전처리 데이터 저장
        save_data(pdf, pmode='PP', file_code='LINE')
        ## 클래스에 저장
        self.pdf = pdf
        
        logs.stop()
        
    def _compute_seq(self):
        logs = Logs('PP_SEQ')
        
        # 전주 전처리 데이터를 이용해 전주 전산화번호별 [x, y]를 리턴하는 Dict생성
        self._ppoledf = self._ppoledf.drop_duplicates(subset='COMP_ID')
        pole_dict = self._ppoledf[['COMP_ID', 'X', 'Y']]\
                        .set_index('COMP_ID').T.to_dict('list')
                        
        # 공사번호별 전주 및 지선주 갯 수 계산
        def computed_pole_counts(curr_pole_df, curr_line_df):
            # 지선주 갯 수: temp_df.shape[0]
            temp_df = curr_pole_df[
                ~curr_pole_df.COMP_ID.isin(curr_line_df.COMP_ID) &
                ~curr_pole_df.COMP_ID.isin(curr_line_df.FROM_COMP_ID)
            ]
            curr_pole_total_count = curr_pole_df.shape[0]
            curr_support_pole_count = temp_df.shape[0]
            return [
                curr_pole_total_count-curr_support_pole_count, 
                curr_support_pole_count
            ]
            
        # 공사번호별 전주 순서계산 함수
        def computed_pole_seqs(paths, curr_pole_df, curr_line_df):
            comp_ids = curr_line_df.COMP_ID.tolist()
            from_comp_ids = curr_line_df.FROM_COMP_ID.tolist()
            spans = curr_line_df.SPAN.tolist()
            pole_comp_ids = curr_pole_df.COMP_ID.tolist()
            only_from_ids = [item for item in from_comp_ids if item not in comp_ids]

            # 현 공사비에서 점검할 전체 전주 갯 수 계산
            curr_data_size = len(from_comp_ids)
            
            # 예외사항 처리
            ## 출발지가 없는 공사번호
            try:
                next_comp_id = only_from_ids[0]
            except Exception:
                return 1
            
            for idx in range(cfg.COND_MAX_POLE_COUNT):
                ## 현재 전주의 기설(1)/신설(0) 여부 판단
                is_already = next_comp_id not in pole_comp_ids
                ## 중간에 기설 전주가 있는 경우 학습에서 제외
                if is_already and idx != 0:
                    return 2
                
                ## 현 전주의 좌표 가져오기
                xy = pole_dict.get(next_comp_id, [0, 0])
                
                if idx < curr_data_size:
                    try:
                        next_comp_id_idx = from_comp_ids.index(next_comp_id)
                        next_span = spans[next_comp_id_idx]
                        paths.extend([is_already, next_comp_id, xy[0], xy[1], next_span])
                        next_comp_id = comp_ids[next_comp_id_idx]
                    except Exception:
                        ## 전주가 끈어진 경우
                        return 3
                elif idx == curr_data_size:
                    paths.extend([is_already, next_comp_id, xy[0], xy[1], 0])
                else:
                    paths.extend([False, '', 0, 0, 0])
                    
            return 0
            
        # 전주/전산 경로 계산
        def computed_pole_paths(cons_id):
            # 공사번호 추가
            pole_path = [cons_id]
            curr_pole_df = self._ppoledf[self._ppoledf.CONS_ID == cons_id]
            curr_line_df = self._plinedf[self._plinedf.CONS_ID == cons_id]
            
            # 전주 및 지선주 갯 수 추가
            pole_path.extend(computed_pole_counts(curr_pole_df, curr_line_df))
            # 전주 순서 구하기
            is_exception = computed_pole_seqs(pole_path, curr_pole_df, curr_line_df)
            
            return is_exception, pole_path
            
        # 공사번호별 전주 순서 계산
        unique_cons_ids = self.pdf.CONS_ID.unique()
        # 공사번호별 경로 데이터 저장소
        path_cons_ids = []
        # 예외사항
        exception_types = []
        
        for id in unique_cons_ids:
            is_exception, pole_path = computed_pole_paths(id)
            if is_exception == 0:
                path_cons_ids.append(pole_path)
            exception_types.append(is_exception)
            
        column_names = ['CONS_ID', 'REAL_POLE_CNTS', 'SUPPORT_POLE_CNT']
        for idx in range(cfg.COND_MAX_POLE_COUNT):
            curr_idx = idx + 1
            column_names += [
                f'POLE{curr_idx}_IS_ALREADY', f'POLE{curr_idx}_COMP_ID',
                f'POLE{curr_idx}_X', f'POLE{curr_idx}_Y', f'POLE{curr_idx}_SPAN'
            ]
        pole_path_df = pd.DataFrame(path_cons_ids, columns=column_names)
        pole_path_df = pole_path_df.applymap(lambda x: int(x) if isinstance(x, bool) else x)

        # 데이터 저장
        ## 임시 데이터 저장
        if cfg.IS_SAVE_TEMPFILE:
            save_data(pole_path_df, pmode='PP', file_code='SEQ', is_temp=True)
            
        pdf = pd.merge(
            self.pdf, pole_path_df,
            left_on='CONS_ID', right_on='CONS_ID', how='right'
        )
        logs.mid('RESULT', pdf.shape)
        
        ## 전처리 데이터 저장
        save_data(pdf, pmode='PP', file_code='SEQ')
        ## 클래스에 저장
        self.pdf = pdf
        
        logs.stop()
            
    def _sl(self): 
        logs = Logs('PP_SL')
        
        # 전처리 데이터 준비
        ## 인입선 데이터 불러오기
        df = self.pdata['SL']
        logs.mid('SOC', df.shape)
        ## 학습에 필요한 데이터 추출
        ### 대상 컬럼
        select_columns = [
            'CONS_ID', 'COMP_ID', 'SL_TYPE_CD', 'SL_SPEC_CD', 'SPAN', 'SUPERVISOR'
        ]
        df = df[select_columns].copy()
        ### 대상 레코드(공사비에 있는 공사번호만 추출)
        df = df[df.CONS_ID.isin(self.pdf.CONS_ID)].copy()
        logs.mid('TARGET', df.shape)
        
        # 데이터 전처리
        
        ## One-Hot Encoding
        df = pd.get_dummies(
            df, columns=['SL_TYPE_CD', 'SL_SPEC_CD'], prefix=['SL_TYPE', 'SL_SPEC']
        )
        df = df.applymap(lambda x: int(x) if isinstance(x, bool) else x)
        
        ## 공사번호별 인입선 데이터 합산
        ### 공사번호 리스트 생성
        unique_cons_ids = df.CONS_ID.unique()
        ### 공사번호별 인입선 합산 데이터 저장
        cons_id_info = []
        ### 합산할 컬럼 리스트
        summation_columns = df.columns.tolist()[2:]
        ### 공사번호별 인입선 합산 데이터 저장
        for id in unique_cons_ids:
            temp_df = df[df.CONS_ID == id]
            id_info = temp_df[summation_columns].sum().values.tolist()
            cons_id_cnt = temp_df.COMP_ID.nunique()
            cons_id_info.append([id, cons_id_cnt, temp_df.shape[0]]+id_info)
        ### 그룹 데이터프레임 만들기
        cons_ids_df = pd.DataFrame(
            cons_id_info,
            columns=['CONS_ID', 'SL_COMP_ID_CNTS', 'REAL_SL_CNTS', 'SL_SPAN_SUM'] \
                     + summation_columns[1:]
        )
        logs.mid('PP1', cons_ids_df.shape)
        
        # 전처리 데이터 병합
        pdf = self.pdf.merge(cons_ids_df, on='CONS_ID', how='left')
        logs.mid('RESULT', pdf.shape)
        
        # 데이터 저장
        ## 임시 데이터 저장
        if cfg.IS_SAVE_TEMPFILE:
            save_data(cons_ids_df, 'PP', 'SL', True)
        ## 전처리 데이터 저장
        save_data(pdf, 'PP', 'SL')
        ## 클래스에 저장
        self.pdf = pdf
        
        logs.stop()
        


    