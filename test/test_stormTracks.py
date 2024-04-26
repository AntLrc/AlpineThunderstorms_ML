import os, sys
dev_path = os.path.join(os.path.dirname(__file__))
src_path = os.path.join(dev_path, "..", 'src')
sys.path.append(src_path)

import CombiPrecip as cp

print(cp)