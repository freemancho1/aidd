import uuid
import platform
import warnings
import sys
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime
from sklearn.exceptions import DataConversionWarning, ConvergenceWarning

import aidd.sys.config as cfg
import aidd.sys.messages as msg


class AiddInit:
    def __init__(self):
        self._set_warnings()
        
    def _set_warnings(self):
        # 엑셀파일 데이터를 읽는 경우 발생할 수 있는 경고(무시가능)
        module = 'openpyxl.styles.stylesheet'
        warnings.filterwarnings('ignore', category=UserWarning, module=module)
        
        # scikit-learn에서 데이터 변환 과정에서 발생할 수 있는 경고로,
        # 일반적으로는 잡는 것을 권하지만, 
        # 데이터 양이 많은 경우 정상적으로 처리된 경우에도 발생할 수 있음
        warnings.filterwarnings(action='ignore', category=DataConversionWarning)
        
        # scikit-learn의 알고리즘이 기본옵션의 반복횟수에서 최적의 성능을 나타내지
        # 못했다는걸 말하는데, 일반적으로 이런 경우 'max_iter' 옵션값을 높여주는
        # 방법을 사용하지만, 그 값을 올려도 안되는 경우가 만음.
        # max_iter를 높이면 처리시간에 영향을 주기 때문에 일단 무시.
        warnings.filterwarnings(action='ignore', category=ConvergenceWarning)
        

class PltInit:
    # matplotlib 사용 시 발생하는 한글문제 등을 해결하기 위해 설정하는 코드로,
    # 쥬피터 노트북에서 이미지 처리할 때 호출하면 됨
    def __init__(self, korean=True, dpi=100):
        # 한글처리 여부와 해상도 지정(시스템 기본값이 100임)
        self.korean = korean
        self.dpi = dpi
        if self.korean:
            self._set_korean()
        self._set_minus()
        self._set_dpi()
        
    def _set_minus(self):
        # Matplotlib x,y축 레이블이 마이너스 일 때, '-'로 표시하도록 설정
        # 이 설정을 하지 않으면 음수 기호가 세모인가로 표시됨
        plt.rcParams['axes.unicode_minus'] = False
        
    def _set_dpi(self):
        # 해상도 지정
        # - 일반적으로 100이면 충분하며, 인쇄용 고해상도가 필요할 때 200 이상 지정
        self.dpi = 100 if self.dpi is None else self.dpi
        plt.rcParams['figure.dpi'] = self.dpi
        
    def _set_korean(self):
        # 기본적인 경우는 아래 4컬럼만 해도 됨
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
        
        
class AiddException(Exception):
    def __init__(self, e_code, value=None, se_msg=None):
        # e_code: error code
        # se_msg: super exception message
        
        # 에러 단계별로 구분하는 구분자('\n')
        self.delimiter = cfg.EXCEPTION_DELIMITER
        try:
            self.msg = msg.EXCEPIONs[e_code]
            self.msg += '' if value is None else f'[{value}]'
            self.msg += '' if se_msg is None else f'{self.delimiter}{se_msg}'
            self.msgs = self.msg.split(self.delimiter)
            self.out_msg = ''
            for m in self.msgs:
                self.out_msg += f'{"  "+m}{self.delimiter}'
            super().__init__(self.out_msg)
        except Exception as e:
            print(f'{msg.EXCEPIONs["EXCEPTION_ERR"]}\n{e}')
            sys.exit(-1)


class Logs:
    # 중첩 로그의 깊이를 저장하는 정형변수
    depth = -1
    
    def __init__(self, code='NONE', is_disp=True):
        self.uuid = str(uuid.uuid4()).split('-')[-1]
        self.is_log_display = cfg.IS_LOG_DISPLAY and is_disp
        self.start_time = datetime.now()
        self.code = code
        self.msg = msg.LOGs['MAIN'][code]
        Logs.depth += 1
        self.depth = Logs.depth
        self._start()
        
    def _start(self):
        self._print(self._get_message('START'))
        
    def mid(self, dcode=None, value=None):
        # dcode: details code
        out_msg = ''
        if dcode is not None:
            out_msg = msg.LOGs['SUB'][self.code][dcode]
            if value is not None:
                out_msg += f': {value}'
        else:
            if value is not None:
                out_msg = value
        self._print(out_msg, depth=self.depth+1)
        
    def stop(self):
        ptime = datetime.now() - self.start_time
        self._print(self._get_message('STOP'), ptime)
        Logs.depth -= 1
    
    def _get_message(self, mode='START'):
        tail = msg.LOGs['SYS'][mode]
        return tail if self.code=='NONE' else f'{self.msg} {tail}'
    
    def _print(self, pmsg, ptime=None, depth=None):
        # pmsg: print message, ptime: processing time
        if not self.is_log_display:
            return
        dspace = '  ' * (self.depth if depth is None else depth)
        print(f'[{self.uuid}][{datetime.now()}] {dspace}{pmsg}', end='')
        print('' if ptime is None else f', {msg.LOGs["SYS"]["TOTAL"]}: {ptime}')
        