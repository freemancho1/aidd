
from aidd.sys.utils import AiddInit as aidd_init
from aidd.sys.argvs import modeling_argvs
from aidd.sys.utils import Logs, AiddException
from aidd.sys.data_io import get_provide_data, get_merged_data
from aidd.modeling.preprocessing import Preprocessing
from aidd.modeling.scaler import Scaling
from aidd.modeling.learning import Learning


def main(is_skip_gpd=False):    # gpd: get provide data
    logs = Logs('MODELING_MAIN')
    
    try:
        # 이부분은 최초 수행 시 항상 체크할 것
        pdata = get_merged_data() if is_skip_gpd else get_provide_data()
        pp = Preprocessing(
            pdata, is_modeling=True, is_preparation= not is_skip_gpd
        )
        sc = Scaling(pp.ppdf)
        Learning(sc.sdata)
    except AiddException as ae:
        print(f'Error:\n{ae}')
    finally:
        logs.stop()
        
if __name__ == '__main__':
    aidd_init()
    args = modeling_argvs()
    main(is_skip_gpd=args.skip_gpd)