LOG = {
    'START': '시작',
    'END': '종료',
    'TOTAL': '최종 처리시간',
    
    'NONE': '',
    'BATCH_MAIN': '배치 데이터 전처리 및 모델링',
    'GET_PROVIDE_DATA': '제공받은 데이터 불러오기',
    'BATCH_MERGE': '전처리를 위해 제공받은 데이터 병합',
    'BATCH_MERGE details': {
        'BEFORE_DEL_SIZE': '공사번호별 데이터 병합 결과',
        'AFTER_DEL_SIZE': '전주/전선 10개 이상 데이터 삭제 후 결과',  
    },
    'BATCH_PREPROCESSING': '배치 데이터 전처리',
    
    'PP_CONS': '공사비 데이터 전처리',
    'PP_CONS details': {
        'RESULT': '공사비 데이터 1차 전처리 결과(데이터 크기)',
        'COLUMNS': '공사비 데이터 1차 전처리 후 컬럼들',
    },
    'PP_FACILITES_COUNT': '공비비 데이터별 설비 갯 수 계산 전처리',
    'PP_FACILITES_COUNT details': {
        'RESULT': '공사비 데이터별 설비 갯 수 계산 후 데이터 크기',
    },
    'PP_POLE': '전주 데이터 전처리',
    'PP_POLE details': {
        'RESULT': '전주 데이터 전처리 결과(데이터 크기)',
        'PP_POLE_ONLY': '전주 데이터만 전처리한 결과(데이터 크기)',
        'PP_POLE_SUM': '전주 데이터 합산 데이터 크기',
        'PP_POLE_MERGE': '공사비와 전주 데이터 병합한 데이터 크기',
    },
    'PP_LINE': '전선 데이터 전처리',
    'PP_LINE details': {
        'RESULT': '전선 데이터 전처리 결과(데이터 크기)',
        'PP_LINE_SOC': '학습에 필요한 컬럼만 추출한 데이터 크기',
        'PP_LINE_REC': '학습에 필요한 레코드만 추출한 데이터 크기',
        'PP_LINE_ONLY': '전선 데이터만 전처리한 결과(데이터 크기)',
        'PP_LINE_SUM': '전선 데이터 합산 데이터 크기',
    },
    'PP_SEQ': '전주/전선 순번 및 전선 갯 수 계산',
    'PP_SEQ details': {
        'RESULT': '전주/전선 순번 계산 결과 데이터',
    },
    'PP_SL': '인입선 데이터 전처리',
    'PP_SL details': {
        'RESULT': '인입선 데이터 전처리 결과, 데이터 크기',
        'SOC': '최초 인입선 데이터 크기',
        'TARGET': '학습대상 데이터 크기',
        'PP1': '인입선 그룹화 후 데이터 크기',
    },
    'BATCH_SCALING': '배치 전처리 데이터 스케일링',
    'SPLIT_DATA': '학습대상 데이터 분리',
    'SPLIT_DATA details': {
        'SOC': '전체 학습대상 데이터 크기',
        'NORMAL_X': '전체 학습대상 컬럼 데이터 크기',
        'ALL': '학습 데이터 크기(DMODE=ALL)',
        '1': '학습 데이터 크기(DMODE=1)',
        'N1': '학습 데이터 크기(DMODE=N1)',
    },
    'SCALING_DATA': '학습대상 데이터 스케일링',
    'batchModeling': '배치 데이터 모델링',
}

ERRORS = {
    'EXCEPTION_ERR': '예외처리 과정에서 에러가 발생했습니다.',
    'NO_PROCESS_MODE': '데이터 경로를 생성하는 과정에 프로세스 모드를 제공하지 않았습니다.',
    'NO_FILE_CODE': '데이터 경로를 생성하는 과정에 파일 코드를 제공하지 않았습니다.',
    'GET_FILE_PATH_ERR': '데이터 경로를 생성하는 과정에서 에러가 발생했습니다.',
    'NONEXISTENT_FILE_PATH': '지정한 경로에 파일이 존재하지 않습니다. 파일경로',
    'READ_DATA_ERR': '데이터를 읽어오는 과정에서 에러가 발생했습니다.',
    'SAVE_DATA_ERR': '데이터를 저장하는 과정에서 에러가 발생했습니다.',
    'SAVE_DATA_ERR2': '데이터를 저장하는 과정(2)에서 에러가 발생했습니다.',
    'GET_PROVIDED_DATA_ERR': '제공받은 데이터를 불러오는 과정에서 에러가 발생했습니다. 데이터 타입',
    'NO_PROVIDE_DATA': '배치 데이터 전처리 과정에 한전에서 제공받은 데이터가 없습니다.',
    'BATCH_PREPROCESSING_ERR': '배치 데이터 전처리 과정에서 에러가 발생했습니다.',
    'BATCH_PREPROCESSING_SERR': '배치 데이터 전처리 과정에서 시스템 에러가 발생했습니다.',
}