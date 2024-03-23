from aidd.sys.utils import AiddInit as aidd_init
from aidd.sys.argvs import check_argvs
from aidd.modeling.main import main as modeling_main
from aidd.serving.main import main as serving_main

aidd_init()

args = check_argvs()
if args.modeling:
    # is_skip_gpd는 최초 한번만 False로 했으면, 이후는 True로 변경해 
    # 처리 속도를 빠르게 할 수 있다.
    modeling_main(is_skip_gpd=True)    # gpd: get provide data
if args.serving:
    serving_main(s_port=args.port)
