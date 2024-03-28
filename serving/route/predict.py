import pandas as pd
from flask import request, jsonify
from flask.views import MethodView

from aidd.sys.json_io import json_to_df
from aidd.serving.service.service_manager import ServiceManager

sm = ServiceManager()


class Predict(MethodView):
    
    def post(self):
        try:
            data = request.json
            jdict, ddict = json_to_df(data)
            pred = sm.get_predict().predict(ddict)
            print('++ route/predict')
            # print(data['BASIC']['OFFICE_NAME'])
            
            # if data and 'name' in data: 
            #     name = data['name']
            #     msg = sm.get_service().predict()
            #     return jsonify({'name': name, 'msg': msg}), 200
            # else:
            #     return jsonify({'error': 'Invalid JSON data'}), 400
            
            # jdata, _ = self._json_to_dataframe(data)
            
            return jsonify(jdict), 200
        except Exception as e:
            return jsonify({'error': e}), 400
    