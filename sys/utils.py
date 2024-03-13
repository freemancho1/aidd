import uuid
import platform
import warnings
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

import aidd.sys.config as cfg
import aidd.sys.messages as msg


class AiddInit:
    def __init__(self):
        self._set_warning()
        
    def _set_warning(self):
        module = 'openpyxl.styles.stylesheet'
        warnings.filterwarnings('ignore', category=UserWarning, module=module)


class AiddException(Exception):
    def __init__(self, err_code=None, value=None, super_err=None):
        self.delimiter = cfg.MESSAGE_DELIMITER
        try:
            self.message = msg.ERRORS[err_code]
            if value is not None:
                self.message += f'[{value}]'
            if super_err is not None:
                self.message += f'{self.delimiter}{super_err}'
            self.messages = self.message.split(self.delimiter)
            self.out_message = ''
            for message in self.messages:
                self.out_message += f'{"  "+message}{self.delimiter}'
            super().__init__(self.out_message)
        except Exception as e:
            print(msg.ERRORS['EXCEPTION_ERR'])
            print(e)
            sys.exit(-1)  
        

class Logs:
    # Logs를 상속중인 모든 클래스의 중첩도를 체크하는 변수(정형변수)
    logs_depth = -1
    
    def __init__(self, type='NONE'):
        self.unique_id = str(uuid.uuid4()).split('-')[-1]
        self.is_debug_mode = cfg.IS_DEBUG_MODE
        self.start_time = None
        self.type = type
        self.base_message = msg.LOG[self.type]
        Logs.logs_depth += 1
        self.depth = Logs.logs_depth
        self._start()
        
    def _get_message(self, mode='START'):
        tail = msg.LOG[mode]
        message = tail if self.type=='NONE' else f'{self.base_message} {tail}'
        return message
    
    def _print(self, message, ptime=None, depth=None):
        if not self.is_debug_mode:
            return
        depth_space = '  ' * (self.depth if depth is None else depth)
        print(f'[{self.unique_id}][{datetime.now()}] {depth_space}{message}', end='')
        print('' if ptime is None else f', {msg.LOG["TOTAL"]}: {ptime}')
        
    def _start(self):
        self.start_time = datetime.now()
        self._print(self._get_message('START'))
        
    def stop(self):
        ptime = datetime.now() - self.start_time
        self._print(self._get_message('END'), ptime)
        Logs.logs_depth -= 1
        
    def mid(self, detail=None, value=''):
        out_message = ''
        if detail is not None:
            out_message = msg.LOG[f'{self.type} details'][detail]
            if value != '':
                out_message += f': {value}'
        else:
            if value != '':
                out_message = value
        self._print(out_message, depth=self.depth+1)
            
            
class PltSettings:
    """쥬피터 노트북에서 이미지 출력관련 환경설정 클래스
       * _set_dpi(): 
          이미지 기본 해상도 및 표 레이블의 '-'값 표시 설정
       * _set_korean(): 
          이미지에 한글을 출력할 수 있도록 설정
    """
    
    def __init__(self, korean=True, etc=None):
        self.korean = korean
        self.etc = etc
        if self.korean:
            self._set_korean()
        self._set_dpi()
        
    def _set_dpi(self):
        """이미지 기본 해상도 및 표 레이블의 '-'값 표시 설정
        """
        # Matplotlib x,y축 레이블이 마이너스 일 때, '-'로 표시하도록 설정
        plt.rcParams['axes.unicode_minus'] = False
        
        # 해상도 지정
        # - 일반적으로 100이면 충분하며, 인쇄용 고해상도가 필요할 때 200 이상 지정
        self.dpi = 100 if self.etc is None else self.etc
        plt.rcParams['figure.dpi'] = self.dpi
        
    def _set_korean(self):
        """이미지에 한글이 표시될 수 있도록 설정(기본값은 한글 표시 안됨)
           * 기본적으로 초반 4줄만 설정해도 되는데, 
             Matplotlib에서 관리하는 폰튼 캐시에 해당 한글폰트가 없을 수 있어
             강제로 추가할 필요가 있음
        """
        osName = platform.system()
        fontPath = cfg.WIN_FONT_PATH if osName == 'Windows' else cfg.UBUNTU_FONT_PATH
        fontFamily = fm.FontProperties(fname=fontPath).get_name()
        plt.rcParams['font.family'] = fontFamily
        
        # 위와 같이 해도 안되는 경우
        # Matplotlib에서 자체적으로 관리하는 폰트 캐시에 해당 문자를 추가함
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = [fontFamily]
        
        font_entry = fm.FontEntry(
            fname = cfg.WIN_FONT_PATH if osName == 'Windows' else cfg.UBUNTU_FONT_PATH,
            name = cfg.WIN_FONT_NAME if osName == 'Windows' else cfg.UBUNTU_FONT_NAME
        )
        fm.fontManager.ttflist.insert(0, font_entry)