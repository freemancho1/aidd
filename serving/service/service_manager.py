import aidd.sys.messages as msg
from aidd.serving.service.predict import Predict


class ServiceManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceManager, cls).__new__(cls)
            cls._instance._predict = Predict()
            print(msg.SYS['START_SERVICE_MANAGER'])
        return cls._instance
    
    def get_predict(cls):
        return cls._predict