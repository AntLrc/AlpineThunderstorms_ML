if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Plot wind gust distribution')
    parser.add_argument('--module-path', type=str, help='path to dir where is module from which the function is supposed to run')
    parser.add_argument('--module-name', type=str, help='name of the module from which the function is supposed to run')
    parser.add_argument('--function-name', type=str, help='name of the function to run')
    
    args = parser.parse_args()
    
    import sys
    sys.path.append(args.module_path)
    
    import importlib
    module = importlib.import_module(args.module_name)
    
    function = getattr(module, args.function_name)
    
    function()