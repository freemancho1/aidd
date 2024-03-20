import os


# 학습에 사용할 데이터 셋 종류
DATA_SETs = ['CONS', 'POLE', 'LINE', 'SL']
# 전주 갯 수를 기준으로 데이터 구분(전체, 하나인것, 하나가 아닌것)
DATA_PC_TYPE = ['ALL', '1', 'N1']
# 모델링 데이터 타입
DATA_MD_TYPE = ['TRAIN_X', 'TEST_X', 'TRAIN_y', 'TEST_y']

# 데이터 기본 경로
BASE_PATH = os.path.join(os.path.expanduser('~'), 'projects', 'data', 'aidd')
# 시스템 전체에서 사용할 파일명
FILE_NAMEs = {
    'PROVIDE': {
        'CONS': 'CONS_INFO.xlsx',
        'POLE': 'POLE_DATA.xlsx',
        'LINE': 'LINE_DATA.xlsx', 
        'SL': 'SL_DATA.xlsx',
    },
    'MERGE': {
        'BATCH': {name: f'STEP01_MB_{name}.CSV' for name in DATA_SETs},
        'ONLINE': {name: f'STEP01_MO_{name}.CSV' for name in DATA_SETs},
    }, 
    'PP': {
        name: f'STEP0{idx+2}_PP_{name}.CSV' \
            for idx, name in enumerate(DATA_SETs)
    }, 
    'ONLINE': 'STEP06_ONLINE.CSV',  # 전처리된 시험용 최종 데이터
    'SCALING': {
        'X': {name: f'STEP07_X_{name}.CSV' for name in DATA_PC_TYPE},
        'y': {name: f'STEP07_y_{name}.CSV' for name in DATA_PC_TYPE},
        'TRAIN_X': {name: f'STEP08_TRAIN_X_{name}.CSV' for name in DATA_PC_TYPE},
        'TEST_X': {name: f'STEP08_TEST_X_{name}.CSV' for name in DATA_PC_TYPE},
        'TRAIN_y': {name: f'STEP09_TRAIN_y_{name}.CSV' for name in DATA_PC_TYPE},
        'TEST_y': {name: f'STEP09_TEST_y_{name}.CSV' for name in DATA_PC_TYPE},
    },
    'DUMP': {
        'OFFICE_LIST': 'MEM01_OFFICE_LIST.pkl',
        'POLE_ONE_HOT_COLS': 'MEM02_POLE_ONE_HOT_COLS.pkl',
        'LINE_ONE_HOT_COLS': 'MEM03_LINE_ONE_HOT_COLS.pkl',
        'SL_ONE_HOT_COLS': 'MEM04_SL_ONE_HOT_COLS.pkl',
        'LAST_PP_COLS': 'MEM05_LAST_PP_COLS.pkl',
        'SCALER': {name: f'MEM06_SCALER_{name}.pkl' for name in DATA_PC_TYPE},
    },
}

# 학습 데이터 제약조건
CONSTRAINTS = {
    'ACC_TYPE_NAME'         : '신설(상용/임시)',
    'MAX_CONT_CAP'          : 50,
    'CONS_TYPE_CD'          : 2,
    'MAX_TOTAL_CONS_COST'   : 30000000,
    'MIN_POLE_CNT'          : 1,
    'MAX_POLE_CNT'          : 10,
    'MIN_LINE_CNT'          : 1,
    'MAX_LINE_CNT'          : 11
}

# Online/Batch 테스트 공사번호
# 전주와 전선은 모두 1~10개 사이이고, 인입선은 제약이 없기 때문에,
# 마지막 데이터는 인입선이 없는 데이터를 샘플로 함.
CHECK_CONS_IDS = ['477420204194', '474620226651', '475920223725']

# 다양하게 사용될 컬럼들
COLS = {
    # 타겟 컬럼
    'TARGET': 'TOTAL_CONS_COST', 
    # 예측결과 리턴할 항목 리스트(현재 사용하지 않음)
    'RETURN': ['CONS_ID', 'TOTAL_CONS_COST'],
    # 영문으로 변경할 컬럼들
    'RENAME': {
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
    },

    # 전처리에 사용되는 컬럼들
    'PP': {
        'CONS': {
            'SOURCE': [
                'CONS_ID', 'TOTAL_CONS_COST', 'CONS_TYPE_CD', 
                'LAST_MOD_DATE', 'LAST_MOD_EID', 
                'OFFICE_NAME', 'CONT_CAP', 'ACC_TYPE_NAME' 
            ],
            'PP': [
                'CONS_ID', 'TOTAL_CONS_COST', 'LAST_MOD_DATE', 
                'LAST_MOD_EID', 'OFFICE_NAME', 
                'YEAR', 'MONTH', 'DAY', 'DAYOFWEEK', 'DAYOFYEAR', 'YEAR_MONTH',
                'EID_NUMBER', 'OFFICE_NUMBER',
            ],
        },
        'POLE': {
            'SOURCE': [
                'CONS_ID', 'COMP_ID',
                'POLE_SHAPE_CD', 'POLE_TYPE_CD', 'POLE_SPEC_CD',
                'COORDINATE'    
            ],
        },
        'LINE': {
            'SOURCE': [
                'CONS_ID', 'COMP_ID', 'FROM_COMP_ID',
                'WIRING_SCHEME', 'LINE_TYPE_CD', 'LINE_SPEC_CD', 'LINE_PHASE_CD',
                'SPAN', 'NEUTRAL_TYPE_CD', 'NEUTRAL_SPEC_CD', 'COORDINATE'
            ], 
        },
        'SL': {
            'SOURCE': [
                'CONS_ID', 'COMP_ID', 'SL_TYPE_CD', 'SL_SPEC_CD', 'SPAN', 'SUPERVISOR'
            ],
        }
    },

    # 모델학습에 사용할 중요 컬럼들
    'SPECIAL': [
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
    ],
}

# 학습에 관련된 사항들
from sklearn.linear_model import Lasso, Ridge, LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import ElasticNet
from xgboost import XGBRegressor
import lightgbm as lgbm

SEED = 1234
MODELS = {
    'ML': {
        'LIN': LinearRegression(),
        'LASSO': Lasso(),
        # 'RIDGE': Ridge(),
        # 'KNR': KNeighborsRegressor(),
        # 'DTR': DecisionTreeRegressor(),
        # 'RFR': RandomForestRegressor(n_estimators=200, n_jobs=-1, random_state=SEED),
        # 'GBR': GradientBoostingRegressor(),
        # 'EN': ElasticNet(alpha=0.1, l1_ratio=0.5, random_state=SEED),
        # 'XGR': XGBRegressor(eta=0.01, n_estimators=100, n_jobs=-1),
        # 'LGBM': 추후 테스트 진행 후 추가 예정
    },
}
MODELS_KEY = list(MODELS['ML'].keys())
FILE_NAMEs['DUMP']['MODELS'] = {
    pc_type: {
        model_name: f'MEM_07_MODEL_{pc_type}_{model_name}.pkl' \
            for model_name in MODELS_KEY+['BEST']
    } for pc_type in DATA_PC_TYPE
}