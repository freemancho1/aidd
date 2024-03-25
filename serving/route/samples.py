from flask import jsonify, request
from flask.views import MethodView

from aidd.sys.json_io import get_sample_data


class Samples(MethodView):
    def get(self):
        try:
            sdata = get_sample_data()
            return jsonify(sdata), 200
        except Exception as e:
            return jsonify({'error:', e}), 400
        
    def post(self):
        try:
            jdata = request.json
            return jsonify(jdata), 200
        except Exception as e:
            return jsonify({'error:', e})