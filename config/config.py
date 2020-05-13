# platform
import platform

if platform.system() == "Windows":
    import sys
    sys.path.insert(1, r'C:\Users\jonas\OneDrive\ETH\DataAna\vaderFolder')
    data_dir = r'C:\Users\jonas\OneDrive\ETH\DataAna'+'\\'
else:
    data_dir = "data_git/"
