import warnings
from sklearn.exceptions import DataConversionWarning

# 경고 무시 설정
warnings.filterwarnings(action='ignore', category=DataConversionWarning)