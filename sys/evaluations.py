import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import mean_absolute_error as MAE
from sklearn.metrics import mean_squared_error as MSE
from sklearn.metrics import mean_absolute_percentage_error as MAPE
from sklearn.metrics import r2_score as R2_SCORE


def user_MAPE(y, p):    # test_y, prediction
    max_value = max(np.max(y), 1)
    umape = 0.
    data_size = len(y)
    for i in range(data_size):
        (_y, _p) = (max_value, p[i]+max_value) if y[i] < 1 else (y[i], p[i])
        umape += abs((_y-_p)/_y)
    return umape / data_size


def reg_evaluation(y, p, verbose=1):    # verbose != 0 => 로그 출력
    # Numpy 자체 버그 해결을 목적으로 모든 값을 소숫점 5자리에서 반올림
    y, p = np.round(y, decimals=5), np.round(p, decimals=5)
    
    mse = MSE(y, p)
    rmse = np.sqrt(mse)
    mae = MAE(y, p)
    r2_score = R2_SCORE(y, p)
    mape = MAPE(y, p)
    umape = user_MAPE(y, p)

    if verbose != 0:
        print(
            f'MAPE[U]: {umape:.6f}, MAPE[S]: {mape:.6f}, R2SCORE: {r2_score:.6f}, '
            f'MAE: {mae:.6f}, MSE: {mse:.6f}, RMSE: {rmse:.6f}'
        )
    return [umape, mape, r2_score, mae, mse, rmse]

def f_importances(model, columns, title):
    fi = model.feature_importances_
    
    plt.figure(figsize=(12,12))
    plt.barh(range(len(fi)), fi)
    plt.yticks(range(len(fi), columns))
    plt.xlabel('Importances')
    plt.ylabel('Feature')
    plt.title(f'{title} Importance by Feature')
    plt.show()

