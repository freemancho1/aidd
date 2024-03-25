from flask import Flask

from serving.route.predict import Predict
from serving.route.samples import Samples


app = Flask(__name__)

# 플라스크 정의
app.debug = True

# 라우터 정의
app.add_url_rule('/predict', view_func=Predict.as_view('predict'))
app.add_url_rule('/samples', view_func=Samples.as_view('samples'))