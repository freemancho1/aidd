import os

# 로그 설정
IS_DEBUG_MODE = True
MESSAGE_DELIMITER = '\n'

# 폰트 설정
WIN_FONT_PATH = 'c:/Windows/Fonts/malgun.ttf'
WIN_FONT_NAME = 'MalgunGothic'
UBUNTU_FONT_PATH = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
UBUNTU_FONT_NAME = 'NanumGothic'

# 시스템 설정
IS_SAVE_TEMPFILE = True

# 학습에 사용할 데이터 설정
BASE_DATA_PATH = os.path.join(os.path.expanduser('~'), 'projects', 'data', 'aidd')
## 제공받은 데이터 종류
DATA_TYPE = ['CONS', 'POLE', 'LINE', 'SL'] 
## 파일 이름들
FILE_NAME = {
    'PROVIDE': {                            # 제공받은 데이터
        'CONS': 'CONS_INFO.xlsx',
        'POLE': 'POLE_DATA.xlsx',
        'LINE': 'LINE_DATA.xlsx',
        'SL': 'SL_DATA.xlsx',
    },
    'MB': {                                 # Merge Batch
        'CONS': 'STEP01_MB_CONS',
        'POLE': 'STEP01_MB_POLE',
        'LINE': 'STEP01_MB_LINE',
        'SL': 'STEP01_MB_SL',  
    },
    'MO': {                                 # Merge Online
        'CONS': 'STEP01_MO_CONS',
        'POLE': 'STEP01_MO_POLE',
        'LINE': 'STEP01_MO_LINE',
        'SL': 'STEP01_MO_SL',  
    },
    'PP': {                                 # Pre-Processing(전처리) 데이터
        'CONS': 'STEP01_PP_CONS',           # 공사비 전처리(1차)
        'CONS_FC': 'STEP02_PP_CONS_FC',     # 공사비 전처리(2차) - 설비 갯 수
        'POLE': 'STEP03_PP_POLE',           # 전주 전처리(공사비별 병합 포함)
        'LINE': 'STEP04_PP_LINE',           # 전선 전처리(공사비별 병합 포함)
        'SEQ': 'STEP05_PP_SEQ',             # 전주/전선 경로지정
        'SL': 'STEP06_PP_SL',               # 인입선 전처리
    },
    'PP_MEM': {                             # 전처리에 저장되는 메모리 정보
        'OFFICE_LIST': 'MEM01_OFFICE_LIST.pkl',
    },
    'SCALING': {
        'X': 'STEP10_X',
        'y': 'STEP10_y',
        'X_ALL': 'STEP11_X_ALL',
        'y_ALL': 'STEP11_y_ALL',
        'X_1': 'STEP11_X_1',
        'y_1': 'STEP11_y_1',
        'X_N1': 'STEP11_X_N1',
        'y_N1': 'STEP11_y_N1',
        'ALL_TRAIN_ALL': 'STEP12_SCALING_ALL_TRAIN_X_ALL',
        'ALL_TEST_ALL': 'STEP12_SCALING_ALL_TEST_X_ALL',
        'ALL_TRAIN_1': 'STEP12_SCALING_ALL_TRAIN_X_1',
        'ALL_TEST_1': 'STEP12_SCALING_ALL_TEST_X_1',
        'ALL_TRAIN_N1': 'STEP12_SCALING_ALL_TRAIN_X_N1',
        'ALL_TEST_N1': 'STEP12_SCALING_ALL_TEST_X_N1',
        'SPC_TRAIN_ALL': 'STEP12_SCALING_SPC_TRAIN_X_ALL',
        'SPC_TEST_ALL': 'STEP12_SCALING_SPC_TEST_X_ALL',
        'SPC_TRAIN_1': 'STEP12_SCALING_SPC_TRAIN_X_1',
        'SPC_TEST_1': 'STEP12_SCALING_SPC_TEST_X_1',
        'SPC_TRAIN_N1': 'STEP12_SCALING_SPC_TRAIN_X_N1',
        'SPC_TEST_N1': 'STEP12_SCALING_SPC_TEST_X_N1',
        
        
        
        'SC_TRAIN_ALL': 'STEP12_SCALING_TRAIN_ALL_X',
        'SC_TEST_ALL': 'STEP12_SCALING_TEST_ALL_X'
    },
}
## 출력파일 확장자
FILE_EXT = '.CSV'
TEMP_FILE_EXT = f'_TEMP{FILE_EXT}'

# 전주 갯 수를 기준으로 데이터 구분
DMODE = ['ALL', '1', 'N1']

# 학습 데이터 제약 조건
COND_ACC_TYPE_NAME = '신설(상용/임시)' 
COND_MAX_CONT_CAP = 50
COND_CONS_TYPE_CD = 2
COND_MAX_TOTAL_CONS_COST = 30000000
COND_MIN_POLE_COUNT = 1
COND_MIN_LINE_COUNT = 1
COND_MAX_POLE_COUNT = 10
COND_MAX_LINE_COUNT = 11

# 학습 대상 컬럼들
MODELING_COLS = {
    'CONS': [
        'CONS_ID', 'TOTAL_CONS_COST', 'CONS_TYPE_CD', 'LAST_MOD_DATE', 
        'LAST_MOD_EID', 'OFFICE_NAME', 'CONT_CAP', 'ACC_TYPE_NAME'
    ],
    'POLE': [
        'CONS_ID', 'COMP_ID',
        'POLE_SHAPE_CD', 'POLE_TYPE_CD', 'POLE_SPEC_CD',
        'COORDINATE'    
    ],
    'LINE': [
        'CONS_ID', 'COMP_ID', 'FROM_COMP_ID',
        'WIRING_SCHEME', 'LINE_TYPE_CD', 'LINE_SPEC_CD', 'LINE_PHASE_CD',
        'SPAN', 'NEUTRAL_TYPE_CD', 'NEUTRAL_SPEC_CD', 'COORDINATE'
    ], 
    'SL': [
        'CONS_ID', 'COMP_ID', 'SL_TYPE_CD', 'SL_SPEC_CD', 'SPAN', 'SUPERVISOR'
    ]
}

# Online/Batch 테스트 공사번호
# 전주와 전선은 모두 1~10개 사이이고, 인입선은 제약이 없기 때문에,
# 마지막 데이터는 인입선이 없는 데이터를 샘플로 함.
CHECK_CONS_IDS = ['477420204194', '474620226651', '475920223725']

# 학습에 사용할 컬럼명(한글명을 영문명으로 변환)
COMMON_COLUMNS = {
    '공사번호': 'CONS_ID',              # Construction ID
    '총공사비': 'TOTAL_CONS_COST',      # Total Construction Cost
    '최종변경일시': 'LAST_MOD_DATE',    # Last Modification Date and Time
    '최종변경자사번': 'LAST_MOD_EID',   # Last Modification Employee ID
    '사업소명': 'OFFICE_NAME',
    '계약전력': 'CONT_CAP',             # Contracted Capacity
    '접수종류명': 'ACC_TYPE_NAME',      # Accept Type Name
    '공사형태코드': 'CONS_TYPE_CD',     # Construction Type Code
    '전산화번호': 'COMP_ID',
    '전원측전산화번호': 'FROM_COMP_ID',
    'GISID': 'GIS_ID',
    '전주형태코드': 'POLE_SHAPE_CD',
    '전주종류코드': 'POLE_TYPE_CD',
    '전주규격코드': 'POLE_SPEC_CD',
    'X좌표-Y좌표': 'COORDINATE',
    '결선방식코드': 'WIRING_SCHEME',
    '지지물간거리': 'SPAN',
    '전선종류코드1': 'LINE_TYPE_CD',
    '전선규격코드1': 'LINE_SPEC_CD',
    '전선조수1': 'LINE_PHASE_CD',
    '중성선종류코드': 'NEUTRAL_TYPE_CD',
    '중성선규격코드': 'NEUTRAL_SPEC_CD',
    '인입전선종류코드': 'SL_TYPE_CD',
    '고객공급선규격코드': 'SL_SPEC_CD',
    '조수': 'SUPERVISOR',
}

SPECIAL_COLUMNS = [
    'CONT_CAP', 
    'YEAR_MONTH', 
    'EID_CODE_NUMBER', 'EID_NUMBER', 
    'OFFICE_NUMBER',
    'LINE_CNT', 
    'REAL_POLE_CNTS', 
    'SUPPORT_POLE_CNT', 
    'REAL_SL_CNTS', 'SL_SPAN_SUM',
    'POLE_SHAPE_O', 
    'POLE_TYPE_C', 'POLE_TYPE_H', 
    'POLE_SPEC_10.0', 'POLE_SPEC_12.0',
    'SPAN', 'LINE_LENGTH', 
    'WIRING_SCHEME_13', 'WIRING_SCHEME_43',
    'LINE_TYPE_AO', 'LINE_TYPE_C2', 'LINE_TYPE_OW',
    'LINE_SPEC_22.0', 'LINE_SPEC_35.0', 
    'LINE_PHASE_1', 
    'NEUTRAL_TYPE_AL', 'NEUTRAL_TYPE_WO', 'NEUTRAL_TYPE_ZZ', 
    'NEUTRAL_SPEC_0.0', 'NEUTRAL_SPEC_22.0', 'NEUTRAL_SPEC_32.0', 
    'POLE2_X', 'POLE2_Y',    
]