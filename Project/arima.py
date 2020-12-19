# coding=utf-8
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from matplotlib.pylab import rcParams
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller
from elasticSearch import ElasticObj
import make_picture as mp

obj = ElasticObj("ott", "_doc")
x = mp.Get_time_every("2020-01-01 00:00:00", "2020-02-28 00:00:00")
[date_list_new, date_every_sentiment] = mp.get_sentiment(x, "发烧")


# 移动平均图
def draw_trend(timeSeries, size):
    f = plt.figure(facecolor='white')
    # 对size个数据进行移动平均
    rol_mean = timeSeries.rolling(window=size).mean()
    # 对size个数据进行加权移动平均
    rol_weighted_mean = pd.ewma(timeSeries, span=size)

    timeSeries.plot(color='blue', label='Original')
    rol_mean.plot(color='red', label='Rolling Mean')
    rol_weighted_mean.plot(color='black', label='Weighted Rolling Mean')
    plt.legend(loc='best')
    plt.title('Rolling Mean')
    plt.show()


# 自相关和偏相关图，默认阶数为31阶
def draw_acf_pacf(ts, lags=31):
    f = plt.figure(facecolor='white')
    ax1 = f.add_subplot(211)
    plot_acf(ts, lags=31, ax=ax1)
    ax2 = f.add_subplot(212)
    plot_pacf(ts, lags=31, ax=ax2)
    plt.show()


def test_stationarity(timeseries):
    # 决定起伏统计
    rolmean = pd.rolling_mean(timeseries, window=12)  # 对size个数据进行移动平均
    rolstd = pd.rolling_std(timeseries, window=12)  # 偏离原始值多少
    # 画出起伏统计
    orig = plt.plot(timeseries, color='blue', label='Original')
    mean = plt.plot(rolmean, color='red', label='Rolling Mean')
    std = plt.plot(rolstd, color='black', label='Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show(block=False)
    # 进行df测试
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic', 'p-value', '#Lags Used', 'Number of observations Used'])
    for key, value in dftest[4].items():
        dfoutput['Critical value(%s)' % key] = value


def arima_model(date_list, date_every_sentiment):
    rcParams['figure.figsize'] = 15, 6
    df = pd.DataFrame(date_every_sentiment)
    df['time'] = date_list
    df = df.set_index(['time'])
    df.index = pd.to_datetime(df.index)
    ts = df[0]

    # 估计estimating
    ts_log = np.log(ts)

    moving_avg = ts_log.rolling(12).mean()
    ts_log_moving_avg_diff = ts_log - moving_avg
    ts_log_moving_avg_diff.dropna(inplace=True)

    # 差分differencing
    ts_log_diff = ts_log.diff(1)
    ts_log_diff.dropna(inplace=True)

    # 分解decomposing
    # 填充缺失值（均值）
    decomposition = seasonal_decompose(ts_log, freq = 1)
    trend = decomposition.trend  # 趋势
    seasonal = decomposition.seasonal  # 季节性
    residual = decomposition.resid  # 剩余的

    ts_log_decompose = residual
    ts_log_decompose.dropna(inplace=True)

    ##预测##
    # 确定参数
    lag_acf = acf(ts_log_diff, nlags=20)
    lag_pacf = pacf(ts_log_diff, nlags=20, method='ols')
    # q的获取:ACF图中曲线第一次穿过上置信区间.这里q取2
    '''
    plt.subplot(121)
    plt.plot(lag_acf)
    plt.axhline(y=0, linestyle='--', color='gray')
    plt.axhline(y=-1.96 / np.sqrt(len(ts_log_diff)), linestyle='--', color='gray')  # lowwer置信区间
    plt.axhline(y=1.96 / np.sqrt(len(ts_log_diff)), linestyle='--', color='gray')  # upper置信区间
    plt.title('Autocorrelation Function')
    plt.subplot(122)
    plt.plot(lag_pacf)
    plt.axhline(y=0, linestyle='--', color='gray')
    plt.axhline(y=-1.96 / np.sqrt(len(ts_log_diff)), linestyle='--', color='gray')
    plt.axhline(y=1.96 / np.sqrt(len(ts_log_diff)), linestyle='--', color='gray')
    plt.title('Partial Autocorrelation Function')
    plt.tight_layout()
    #plt.show()
    '''
    model = ARIMA(ts_log, order=(2, 1, 0))
    result_ARIMA = model.fit(disp=-1)
    '''
    plt.plot(ts_log_diff)
    plt.plot(result_ARIMA.fittedvalues, color='red')
    plt.title('AR model RSS:%.4f' % sum(result_ARIMA.fittedvalues - ts_log_diff) ** 2)
    #plt.show()
    '''
    pre = result_ARIMA.predict(1, len(date_list) + 5)
    '''
    plt.plot(ts_log_diff, label='原数据')
    plt.plot(predict, label='预测数据')
    plt.legend()
    #plt.show()
    '''
    predictions_ARIMA_diff = pd.Series(pre, copy=True)
    predictions_ARIMA_diff_cumsum = predictions_ARIMA_diff.cumsum()
    predictions_ARIMA_log = pd.Series(ts_log.iloc[0], index=ts_log.index)
    predictions_ARIMA_log = predictions_ARIMA_log.add(predictions_ARIMA_diff_cumsum, fill_value=0)
    predictions_ARIMA = np.exp(predictions_ARIMA_log)
    '''
    plt.plot(ts)
    plt.plot(predictions_ARIMA)
    plt.title('predictions_ARIMA RMSE: %.4f' % np.sqrt(sum((predictions_ARIMA - ts) ** 2) / len(ts)))
    #plt.show()
    '''
    date_l = []
    for i in range(0, len((predictions_ARIMA.index))):
        date_l.append(str(predictions_ARIMA.index[i]))
    true_l = []
    predict_l = []
    for i in range(0, len(ts)):
        true_l.append(ts[i])
    for i in range(0, len(predictions_ARIMA)):
        predict_l.append(predictions_ARIMA[i])
    return [date_l, true_l, predict_l]
