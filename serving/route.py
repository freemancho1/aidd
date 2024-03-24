import pandas as pd
from flask import request, jsonify
from flask.views import MethodView

from aidd.serving.service import ServiceManager

sm = ServiceManager()


class Predict(MethodView):
    def post(self):
        print('요청 접수')
        print(f'최대 요청 컨텐츠 길이: {request.max_content_length}')
        data = request.json
        
        # print(data['BASIC']['OFFICE_NAME'])
        
        # if data and 'name' in data: 
        #     name = data['name']
        #     msg = sm.get_service().predict()
        #     return jsonify({'name': name, 'msg': msg}), 200
        # else:
        #     return jsonify({'error': 'Invalid JSON data'}), 400
        
        # jdata, _ = self._json_to_dataframe(data)
        
        return jsonify(data), 200
    
    def _json_to_dataframe(self, data):
        jdata = {}
        basic = data['BASIC']
        for key, value in data['PREDICT'].items():
            jdata[key] = value
            jdata[key]['BASIC']['ACC_NO'] = basic['ACC_NO']
        df = pd.DataFrame()
        return jdata, df