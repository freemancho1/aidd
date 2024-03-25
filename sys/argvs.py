import argparse

def run_args():
    parser = argparse.ArgumentParser(
        description='Server-side Program of an Artificial Intelligence-based Distribution Design System',
        usage='Please use it as follows.\n' \
              '- modeling: run [--modeling, -m] [--skip-gpd, -sg]\n' \
              '- serving: run -s(--service) [--port, -p] PORT-NO(default: 11001)',
    )
    
    parser.add_argument(
        '--modeling', '-m', action='store_true',
        help='Training artificial intelligence models. '\
             'If nothing is entered, the [--modeling] option will be applied automatically.'
    )
    parser.add_argument(
        '--skip-gpd', '-sg', action='store_true',
        help='If modeling operations have been performed than once, ' \
             'reading the source data is skipped for faster modeling. ' \
             'Instead, a preprocessed file removing constraints records and ' \
             'columns is read to improve processing speed.'
    )
    
    parser.add_argument(
        '--serving', '-s', action='store_true',
        help='Starting a construction cont prediction service using AI models.'
    )
    parser.add_argument(
        '--port', '-p', type=int, default=11001,
        help='When specifying the port to be used for serving via the web, ' \
             'the default value is 11001'
    )
    args = parser.parse_args()
    return args

def modeling_argvs():
    parser = argparse.ArgumentParser(
        description='Server-side Program of an Artificial Intelligence-based Distribution Design System'
    )
    parser.add_argument('--skip-gpd', '-s', action='store_true', help='')
    args = parser.parse_args()
    return args

def serving_argvs():
    parser = argparse.ArgumentParser(
        description='Server-side Program of an Artificial Intelligence-based Distribution Design System'
    )
    parser.add_argument('--port', '-p', type=int, default=11001, help='')

    args = parser.parse_args()
    return args