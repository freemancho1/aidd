import argparse

def check_argvs():
    parser = argparse.ArgumentParser(
        description='Server-side Program of an Artificial Intelligence-based Distribution Design System'
    )
    parser.add_argument(
        '--modeling', '-m', action='store_true', 
        help='When running the program, the execution of ' \
             'the "modeling" section is determined, ' \
             'and if display, the modeling section will be executed. ' \
             'By default, it does not run.'
    )
    parser.add_argument(
        '--serving', '-s', action='store_true', 
        help='When running the program, the execution of ' \
             'the "serving" section is determined, ' \
             'and if display, the modeling section will be executed. ' \
             'By default, it does not run.'
    )
    parser.add_argument(
        '--port', '-p', type=int, default=11001,
        help='When specifying the port to be used for serving via the web, ' \
             'the default value is 11001'
    )
    
    args = parser.parse_args()
    # 아래 강제로 설정된 두 줄은 나중에 제거해야함
    # args.modeling = True
    # args.serving = True
    return args