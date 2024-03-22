from aidd.sys.utils import AiddInit as aidd_init
from aidd.sys.argvs import check_argvs
from aidd.modeling.main import main as modeling_main
from aidd.serving.main import main as serving_main

aidd_init()

args = check_argvs()
if args.modeling:
    modeling_main()
if args.serving:
    serving_main(s_port=args.port)
