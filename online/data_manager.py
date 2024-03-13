import aidd.sys.config as cfg

def get_online_sample(data):
    """온라인 서비스 샘플 데이터 생성 함수
    * 온라인 서비스나 온라인 서비스를 위한 전처리 프로세스 테스트를 위한
      샘플 데이터를 생성하는 함수로, 대상 데이터는 `config`에 지정되어 있음
    * 실제 온라인 작업에선 사용하지 않음
    Args:
        data (dict): 학습용으로 제공받은 전체 데이터
            - `key: df`로 구성된 딕셔너리로 제공됨
    Returns:
        jsons (dict): Online으로 받을 예정인 JSON 데이터의 딕셔너리
    """
    # 전체 데이터에서 샘플 데이터만 추출한 데이터프레임 딕셔너리
    jsons = {}
    for key in cfg.DATA_TYPE:
        df = data[key]
        df = df[df.CONS_ID.isin(cfg.CHECK_CONS_IDS)]
        if key == 'CONS':
            df.drop(columns=('TOTAL_CONS_COST'), inplace=True)
        jsons[key] = df[cfg.MODELING_COLS[key]].to_json(orient='records')
        
    return jsons