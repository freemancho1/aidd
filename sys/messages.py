# 시스템 메시지
SYS = {
    'WEB_SERVICE_COMPLETED': 'The web service has completed. Please access http://localhost:',
    'PREDICTION_SERVICE_READY': 'The AI-based construction cost prediction service is ready.',
    'START_SERVICE_MANAGER': 'The service manager for the web service has started.',
}

EXCEPIONs = {
    # 시스템 오류
    'EXCEPTION_ERR': '예외처리 과정에서 에러가 발생했습니다.',
    'EXCEPTION_TEST': '예외처리 테스트',
}

# Service 
ERRORs = {
    'ERR': 'error',
    '400': 'Invalid JSON',
}

LOGs = {
    'SYS': {
        'START': '시작',
        'STOP': '종료',
        'TOTAL': '최종 처리시간',
        'NONE': '',
    },
    'MAIN': {
        'MODELING_MAIN': '데이터 모델링',
        'GET_PROVIDE_DATA': '제공받은 데이터 불러오기',
        'GET_MERGED_DATA': '1차 전처리 완료된 데이터 불러오기',
        'PP': '데이터 전처리',
        'PREPARATION': '제약조건을 기준으로 1차 데이터 제거',
        'PP_CONS': '공사비 데이터 전처리',
        'PP_COMPUTE': '공사비 기준 설비 갯 수 계산',
        'PP_POLE': '전주 데이터 전처리',
        'PP_LINE': '전선 데이터 전처리',
        'PP_SL': '인입선 데이터 전처리',
        'SCALING': '전처리 데이터 분할 및 스케일링',
        'LEARNING': '모델 학습',
        'SERVICE': '모델 서비스',
    },
    'SUB': {
        'GET_PROVIDE_DATA': {
            'CONS': '공사비 데이터 셋',
            'POLE': '전주 데이터 셋',
            'LINE': '전선 데이터 셋',
            'SL': '인입선 데이터 셋',
        },
        'GET_MERGED_DATA': {
            'CONS': '1차 전처리된 공사비 데이터 셋',
            'POLE': '1차 전처리된 전주 데이터 셋',
            'LINE': '1차 전처리된 전선 데이터 셋',
            'SL': '1차 전처리된 인입선 데이터 셋',
        },
        'PREPARATION': {
            'CONS': '1차 제약조건을 제외한 공사비 데이터 셋 크기',
            'POLE': '1차 제약조건을 제외한 전주 데이터 셋 크기',
            'LINE': '1차 제약조건을 제외한 전선 데이터 셋 크기',
            'SL': '1차 제약조건을 제외한 인입선 데이터 셋 크기',
            'SAVE': '1차 제약조건을 제외한 데이터 셋들 저장',
        },
        'PP_CONS': {
            'SOURCE': '전처리 전 공사비 데이터 셋 크기',
            'RESULT': '전처리 후 공사비 데이터 셋 크기',
        }, 
        'PP_COMPUTE': {
            'COMPUTE': '공사비 기준 설비 갯 수 계산 후 데이터 셋 크기',
            'RESULT': '공사비 기준 설비 갯 수 체크 후 데이터 셋 크기',
        },
        'PP_POLE': {
            'SOURCE': '전처리 전 전주 데이터 셋 크기',
            'ONE_HOT': '전주 데이터 ONE HOT ENCODING 후 데이터 셋 크기',
            'RESULT': '전주 데이터 전처리 후 모델링 데이터 셋 크기',
        },         
        'PP_LINE': {
            'SOURCE': '전처리 전 전선 데이터 셋 크기',
            'ONE_HOT': '전선 데이터 ONE HOT ENCODING 후 데이터 셋 크기',
            'RESULT': '전선 데이터 전처리 후 모델링 데이터 셋 크기',
        }, 
        'PP_SL': {
            'SOURCE': '전처리 전 인입선 데이터 셋 크기',
            'ONE_HOT': '인입선 데이터 ONE HOT ENCODING 후 데이터 셋 크기',
            'RESULT': '인입선 데이터 전처리 후 모델링 데이터 셋 크기',
        }, 
        'SCALING': {
            'SOURCE_X': '학습대상 속성 데이터 전체 크기',
            'PC_TYPE_X': '전주 수 타입',
            'PC_TYPE_TT': '전주 수 타입별 훈련/시험 데이터 크기'
        },
        'LEARNING': {
            'RESULT': '모델학습 결과',
        },
        'SERVICE': {
            'INPUT_ERR': 'JSON 이외의 데이터가 입력되었습니다.',
            'INPUT_OK': '입력 데이터',
        },
    },
}