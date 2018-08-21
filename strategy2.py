#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------
import pandas as pd
import numpy as np
from profit import change5
from orders import orders, volatility_corection
from mldata import ml_data
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.neural_network import BernoulliRBM
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from vecstack import stacking
from sklearn.metrics import accuracy_score
import sys
# dada una serie de pandas o una lista y el numero de muestras para la EMA y
# SMA devuelve vector w considerando el cruce entre EMA y SMA


def EMAvsSMA(serie, smaPeriod=20, emaPeriod=5):
    # Calculando media movil a 20 muestras
    sma = serie.rolling(smaPeriod, min_periods=1).mean()
    # caculando exponential movil average
    ema = serie.ewm(span=emaPeriod, adjust=False).mean()

    # Encontrando el signo de la resta entre ellas para encontrar los cruces
    dif = (ema - sma).apply(np.sign)

    w = pd.DataFrame(data={"w": (dif+1)/2})

    w['w'] = w['w'].apply(change5)

    w["orders"] = orders(w["w"])

    w["price"] = serie

    return w


def EMAvsSMA2(serie, volatility, smaPeriod=20, emaPeriod=5):
    """
    Cruce de medias corregido por volatilidad
    """

    # Calculando media movil a 20 muestras
    sma = serie.rolling(smaPeriod, min_periods=1).mean()
    # caculando exponential movil average
    ema = serie.ewm(span=emaPeriod, adjust=False).mean()

    # Encontrando el signo de la resta entre ellas para encontrar los cruces
    dif = (ema - sma).apply(np.sign)

    w = pd.DataFrame(data={"w": (dif+1)/2})

    w['w'] = w['w'].apply(change5)

    # corrigiendo por volatilidad
    w["w"] = volatility_corection(w["w"], volatility)

    w["orders"] = orders(w["w"])

    w["price"] = serie

    return w


def SMAvsSMA(serie, smaPeriod=20, emaPeriod=10):
    # Calculando media movil a 20 muestras
    sma = serie.rolling(smaPeriod, min_periods=1).mean()
    # Calculando media movil a 10 muestras
    ema = serie.rolling(emaPeriod, min_periods=1).mean()

    # Encontrando el signo de la resta entre ellas para encontrar los cruces
    dif = (ema - sma).apply(np.sign)

    w = pd.DataFrame(data={"w": (dif+1)/2})

    w['w'] = w['w'].apply(change5)

    w["orders"] = orders(w["w"])

    w["price"] = serie
    
    return w


def SMAvsSMA2(serie,  volatility, smaPeriod=20, emaPeriod=10):
    # Calculando media movil a 20 muestras
    sma = serie.rolling(smaPeriod, min_periods=1).mean()
    # Calculando media movil a 10 muestrase
    ema = serie.rolling(emaPeriod, min_periods=1).mean()

    # Encontrando el signo de la resta entre ellas para encontrar los cruces
    dif = (ema - sma).apply(np.sign)

    w = pd.DataFrame(data={"w": (dif+1)/2})

    w['w'] = w['w'].apply(change5)

    # corrigiendo por volatilidad
    w["w"] = volatility_corection(w["w"], volatility)

    w["orders"] = orders(w["w"])
    
    w["price"] = serie

    return w

# dada una serie de pandas y el numero de muestras para las EMAs devuelve
# vector w considerando el cruce entre estas
def EMAvsEMA(serie, smaPeriod=20, emaPeriod=5):

    # caculando exponential movil average lenta
    sma = serie.ewm(span=smaPeriod, adjust=False).mean()
    # caculando exponential movil average rapida
    ema = serie.ewm(span=emaPeriod, adjust=False).mean()

    # Encontrando el signo de la resta entre ellas para encontrar los cruces
    dif = (ema - sma).apply(np.sign)

    w = pd.DataFrame(data={"w":(dif+1)/2})

    w['w'] = w['w'].apply(change5)

    w["orders"] = orders(w["w"])
    
    w["price"] = serie

    return w


def pricevsEMA(serie, emaPeriod=5):
    """
    dada una serie de pandas y el numero de muestras para la EMA devuelve el
    vector w considerando el cruce entre EMA y el precio
    """
    # precio
    ema = serie
    # caculando exponential movil average rapida
    sma = serie.ewm(span=emaPeriod, adjust=False).mean()

    # Encontrando el signo de la resta entre ellas para encontrar los cruces
    dif = (ema - sma).apply(np.sign)

    w = pd.DataFrame(data={"w":(dif+1)/2})

    w['w'] = w['w'].apply(change5)

    w["orders"] = orders(w["w"])
    
    w["price"] = serie

    return w


def pricevsEMA2(serie, volatility, emaPeriod=5, type=0):
    """
    dada una serie de pandas y el numero de muestras para la EMA devuelve el
    vector w considerando el cruce entre EMA y el precio
    """
    # precio
    ema = serie
    # caculando exponential movil average rapida
    sma = serie.ewm(span=emaPeriod, adjust=False).mean()

    # Encontrando el signo de la resta entre ellas para encontrar los cruces
    dif = (ema - sma).apply(np.sign)

    w = pd.DataFrame(data={"w": (dif+1)/2})

    w['w'] = w['w'].apply(change5)

    # corrigiendo por volatilidad
    w["w"] = volatility_corection(w["w"], volatility, type)

    w["orders"] = orders(w["w"])

    w["price"] = serie

    return w


def pricevsSMA(serie, smaPeriod=20):
    """
    dada una serie de pandas y el numero de muestras para la EMA devuelve
    vector w considerando el cruce entre EMA y el precio
    """
    # precio
    ema = serie
    # Calculando media movil a 20 muestras
    sma = serie.rolling(smaPeriod, min_periods=1).mean()

    # Encontrando el signo de la resta entre ellas para encontrar los cruces
    dif = (ema - sma).apply(np.sign)

    w = pd.DataFrame(data={"w": (dif+1)/2})

    w['w'] = w['w'].apply(change5)

    w["orders"] = orders(w["w"])
    
    w["price"] = serie

    return w


def ml_logreg(close, per=0.9, model=None, count=None, **kwargs):
    """
    close: Serie de Pandas con precio de cierre. Se utiliza para crear
    estrategia ideal.
    per: Float que especifica en que porcentaje se dividiran train y test.
    mod: Modelo entrenado de machine learning
    **kwargs: Diccionario con las caracteristicas para entrenar y predecir.
    """

    # si el modelo no viene pre entrenado
    if count is None:
        model = LogisticRegression(C=0.150)
        model, test = train_ml_model(close, model, per, **kwargs)

    # si queremos que sea pre-entrenado pero es la primera corrida
    # debe entrenarse
    elif count == 1:
        model = LogisticRegression(C=0.150)
        model, test = train_ml_model(close, model, per, **kwargs)
        return model, test

    else:
        # obtenemos None y los datos de testeo
        no_model, test = train_ml_model(close, model, per, False, **kwargs)

    w_pred = test_ml_model(model, test)
    return w_pred


def ml_randfor(close, per=0.9, model=None, **kwargs):
    """
    close: Serie de Pandas con precio de cierre. Se utiliza para crear
    estrategia ideal.
    per: Float que especifica en que porcentaje se dividiran train y test.
    **kwargs: Diccionario con las caracteristicas para entrenar y predecir.
    """

    # si el modelo no viene pre entrenado
    if model is None:
        # iniciando modelo de regresion logistica
        model = RandomForestClassifier(n_estimators=45, max_depth=4,
                                               min_samples_split=65)

    model, test = train_ml_model(close, model, per, **kwargs)

    w_pred = test_ml_model(model, test)
    return w_pred


def ml_knn(close, per=0.9, model=None, **kwargs):
    """
    close: Serie de Pandas con precio de cierre. Se utiliza para crear
    estrategia ideal.
    per: Float que especifica en que porcentaje se dividiran train y test.
    **kwargs: Diccionario con las caracteristicas para entrenar y predecir.
    """

    # si el modelo no viene pre entrenado
    if model is None:
        # iniciando modelo de regresion logistica
        model = KNeighborsClassifier(n_neighbors=110, weights="distance")

    model, test = train_ml_model(close, model, per, **kwargs)

    w_pred = test_ml_model(model, test)
    return w_pred


def ml_mlpc(close, per=0.9, model=None, **kwargs):
    """implements a multi-layer perceptron (MLP) algorithm
    close: Serie de Pandas con precio de cierre. Se utiliza para crear
    estrategia ideal.
    per: Float que especifica en que porcentaje se dividiran train y test.
    **kwargs: Diccionario con las caracteristicas para entrenar y predecir.
    """

    # si el modelo no viene pre entrenado
    if model is None:
        # iniciando modelo de red neuronal
        model = MLPClassifier(solver='lbfgs',
                             random_state=0, hidden_layer_sizes=(50, 20))

    model, test = train_ml_model(close, model, per, **kwargs)

    w_pred = test_ml_model(model, test)
    return w_pred


def ml_bm(close, per=0.9, model=None, **kwargs):
    """implements a Boltzman deep learning algorithm
    close: Serie de Pandas con precio de cierre. Se utiliza para crear
    estrategia ideal.
    per: Float que especifica en que porcentaje se dividiran train y test.
    **kwargs: Diccionario con las caracteristicas para entrenar y predecir.
    """

    # si el modelo no viene pre entrenado
    if model is None:
        # iniciando modelo de boltzman machine
        rbm = BernoulliRBM()
        logistic = LogisticRegression(C=0.150)
        model = Pipeline([("rbm", rbm), ("logistic", logistic)])

    model, test = train_ml_model(close, model, per, **kwargs)

    w_pred = test_ml_model(model, test)
    return w_pred


def ml_xgb(close, per=0.9, model=None, **kwargs):
    """
    close: Serie de Pandas con precio de cierre. Se utiliza para crear
    estrategia ideal.
    per: Float que especifica en que porcentaje se dividiran train y test.
    **kwargs: Diccionario con las caracteristicas para entrenar y predecir.
    """

    # si el modelo no viene pre entrenado
    if model is None:
        # iniciando modelo de XGBoost
        model = XGBClassifier(n_estimators=9, learning_rate=0.75, gamma=12)

    model, test = train_ml_model(close, model, per, **kwargs)

    w_pred = test_ml_model(model, test)
    return w_pred


def ml_stacking(close, per=0.9, **kwargs):
    """
    close: Serie de Pandas con precio de cierre. Se utiliza para crear
    estrategia ideal.
    per: Float que especifica en que porcentaje se dividiran train y test.
    **kwargs: Diccionario con las caracteristicas para entrenar y predecir.
    """
    from vecstack import stacking
    from sklearn.svm import SVC
    from sklearn.metrics import accuracy_score



    clf1 = RandomForestClassifier(n_estimators=45, max_depth=4, min_samples_split=65)
    clf3 = XGBClassifier(n_estimators=9, learning_rate=0.75, gamma=12)
    #clf4 = SVC(probability=True)
    clf4 =  MLPClassifier(solver='lbfgs',random_state=0, hidden_layer_sizes=(50, 20))
    clf7 = KNeighborsClassifier(n_neighbors=110, weights="distance")

    models = [clf1,  clf4, clf7]

    # dataframe con pesos de la estrategia idea
    w = pd.DataFrame(data={"w": ml_data(close, pl=False).values,
                           "price": close})

    w["orders"] = orders(w["w"])
    # vector de pesos de la estrategia ideal

    # diccionario que contendra las caracteristicas para evaluar y
    # el precio o weightedAverage sobre el que se quiere predecir
    dic = {"best_w": w["w"], "close": close}
    # agregando el resto de las caracteristicas
    dic.update(kwargs)

    # creando dataframe con los valores del diccionario
    data = pd.DataFrame(data=dic)

    # quitando valores NaN
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    data.fillna(method='bfill', inplace=True)

    # separando datos para crear y evaluar el modelo de machine learning.
    # se toma train desde 1 para no tener NaN de la primera fila
    train = data[1:int(len(data)*per)]
    test = data[int(len(data)*per):]

    S_train, S_test = stacking(models,                     # list of models
                           train.drop(["best_w", "close"], axis=1), 
                           train["best_w"], test.drop(["best_w", "close"], axis=1),   
                           regression=False,

                           mode='oof_pred_bag',

                           needs_proba=False,

                           save_dir=None,

                           metric=accuracy_score,      # metric: callable
                           n_folds=4,                  # number of folds
                           stratified=True,
                           shuffle=True,
                           random_state=0,
                           verbose=1)
    try:
        # entrenando el modelo
        model = clf3.fit(S_train, train["best_w"])
    except ValueError:
        print data.isnull().any()
        print train[train['rsi'].isnull()]
        print train[train['rsi'] == np.inf]
        sys.exit(1)

    # prediciendo con el modelo
    pred = model.predict(S_test)

    # dataframe con vector de pesos de estrategia de regresio logistica
    w_pred = pd.DataFrame(data={"w": pred, "price": test["close"]})
    w_pred["orders"] = orders(w_pred["w"])
    
    print "Accuracy:%s"%accuracy_score(test["best_w"], pred)

    return w_pred


def train_ml_model(close, model, per=0.9, train_ml=True, **kwargs):
    """Entrena el modelo de las estrategias de ML. Devuelve el modelo
    entrenado y los datos de testeo.

    close: Serie de Pandas con precio de cierre. Se utiliza para crear
    estrategia ideal.
    per: Float que especifica en que porcentaje se dividiran train y test.
    **kwargs: Diccionario con las caracteristicas para entrenar y predecir.
    """

    # dataframe con pesos de la estrategia ideal
    w = pd.DataFrame(data={"w": ml_data(close, pl=False).values,
                           "price": close})

    # diccionario que contendra las caracteristicas para evaluar y
    # el precio o weightedAverage sobre el que se quiere predecir
    dic = {"best_w": w["w"], "close": close}
    # agregando el resto de las caracteristicas
    dic.update(kwargs)

    # creando dataframe con los valores del diccionario
    data = pd.DataFrame(data=dic)

    # quitando valores NaN
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    data.fillna(method='bfill', inplace=True)

    # separando datos para crear y evaluar el modelo de machine learning.
    # se toma train desde 1 para no tener NaN de la primera fila
    train = data[1:int(len(data)*per)]
    test = data[int(len(data)*per):]

    if train_ml:
        try:
            # entrenando el modelo
            model.fit(train.drop(["best_w", "close"], axis=1), train["best_w"])
        except ValueError:
            print data.isnull().any()
            print train[train['rsi'].isnull()]
            print train[train['rsi'] == np.inf]
            sys.exit(1)

    return model, test


def test_ml_model(model, test):
    """Predice utilizando el modelo model sobre los datos de testeo test.

    :param model: Modelo de machine learning previamente entrenado
    :type model: Modelo de machine learning de sklearn o xgboost
    :param test: Datos de testeo
    :type test: Pandas DataFrame
    """
    # prediciendo con el modelo
    pred = model.predict(test.drop(["best_w", "close"], axis=1))

    # dataframe con vector de pesos de estrategia de regresio logistica
    w_pred = pd.DataFrame(data={"w": pred, "price": test["close"]})

    print "Accuracy:%s"%accuracy_score(test["best_w"], pred)
    return w_pred