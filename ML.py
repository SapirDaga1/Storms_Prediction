import pandas as pd
from sklearn import metrics
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import r2_score, f1_score


def coordinateValidation(lat, long):
    return (-90 <= lat <= 90) and (-180 <= long <= 180)


def airPressureValidation(airPressure):
    return airPressure > 0


def dateValidation(year, month, day):
    if year < 0:
        return False
    day_count_for_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        day_count_for_month[1] = 29
    return (1 <= month <= 12 and 1 <= day <= day_count_for_month[month])


def getParams():
    lat = float(input("Please enter Latitude value: "))
    long = float(input("Please enter Longitude value: "))
    while not coordinateValidation(lat, long):
        print('Your coordinate are out of range please enter again. ')
        lat = float(input("Please enter Latitude value: "))
        long = float(input("Please enter Longitude value: "))
    pressure = float(input("Please enter air pressure value: "))
    while not airPressureValidation(pressure):
        print('Your air pressure are out of range please enter again. ')
        pressure = float(input("Please enter air pressure value: "))
    year, month, day = map(int, input('Enter a date in date format: year month day: ').split(' '))
    while not dateValidation(year, month, day):
        print('Your date are out of range please enter again.')
        year, month, day = map(int, input('Enter a date in date format: year month day. ').split(' '))
    return lat, long, pressure, year, month, day


def linearRegressionModel(df):
    X = df.loc[:, ~df.columns.isin(
        ['storm_name', 'time', 'wind_power', 'storm_type', 'Ocean', 'ocean_code', 'beaufort_scale'])]
    y = df['wind_power']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=45)
    model = LinearRegression().fit(X_train, y_train)
    y_pred = model.predict(X_test)
    lat, long, pressure, year, month, day = getParams()
    print(f"You've entered Coordinate ({lat}, {long}), Air Pressure {pressure} and Date {year}/{month}/{day}: ")
    print(f'\nPrediction of wind power is: {float(model.predict([[year, pressure, lat, long, month, day]])[0]):.3f}'
          f' mph')
    print(f'The R^2 score of our model is: {r2_score(y_test, y_pred)}\n')


def getWindFromLinearModel(df, lat, long, pressure, year, month, day):
    X = df.loc[:, ~df.columns.isin(
        ['storm_name', 'time', 'wind_power', 'storm_type', 'Ocean', 'ocean_code', 'beaufort'])]
    y = df['wind_power']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=45)
    model = LinearRegression().fit(X_train, y_train)
    lat = lat
    long = long
    pressure = pressure
    year, month, day = year, month, day
    return round(float(model.predict([[year, pressure, lat, long, month, day]])[0]), 3)


def rearrangeBeaufortColumn(df):
    df = df.copy()
    dfBeaufortScaleLessThan5 = df[df['beaufort_scale'] < 5].reset_index(drop=True)
    dfBeaufortScaleBetween5To8 = df[(df['beaufort_scale'] >= 5) & (df['beaufort_scale'] <= 8)].reset_index(drop=True)
    dfBeaufortScaleBetween9To11 = df[(df['beaufort_scale'] >= 9) & (df['beaufort_scale'] <= 11)].reset_index(drop=True)
    dfBeaufortScaleHigherThan12 = df[(df['beaufort_scale'] >= 12)].reset_index(drop=True)
    dfBeaufortScaleLessThan5['beaufort'] = 0
    dfBeaufortScaleBetween5To8['beaufort'] = 1
    dfBeaufortScaleBetween9To11['beaufort'] = 2
    dfBeaufortScaleHigherThan12['beaufort'] = 3

    return pd.concat(
        [dfBeaufortScaleHigherThan12, dfBeaufortScaleBetween9To11, dfBeaufortScaleBetween5To8,
         dfBeaufortScaleLessThan5], ignore_index=True).drop(['beaufort_scale'], axis=1)


def logisticRegressionModel(df):
    # Logistic Regression by beaufort split (breeze ,low, med, high)
    df = rearrangeBeaufortColumn(df)
    X = df.loc[:, ~df.columns.isin(
        ['storm_name', 'time', 'storm_type', 'Ocean', 'ocean_code', 'beaufort'])]
    y = df['beaufort']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=40)
    scaler = MinMaxScaler(feature_range=(0, 1))
    X_train_scaled = scaler.fit_transform(X_train)
    model = LogisticRegression().fit(X_train_scaled, y_train)
    y_pred = model.predict(scaler.transform(X_test))
    lat, long, pressure, year, month, day = getParams()
    wind = getWindFromLinearModel(df, lat, long, pressure, year, month, day)
    cords = scaler.transform([[year, wind, pressure, lat, long, month, day]])
    predicted_values = model.predict_proba(cords)[0]
    breezeProb, lowProb, mediumProb, highProb = predicted_values[0] * 100, predicted_values[1] * 100, predicted_values[
        2] * 100, predicted_values[3] * 100
    print(f"You've entered Coordinate ({lat}, {long}), Air Pressure {pressure}, Wind Power {wind} (from linear model)"
          f" and Date {year}/{month}/{day}: ")
    print(f'A breeze storm probability: {breezeProb:.2f}%'
          f'\nTropical Depression probability: {lowProb:.2f}%\n'
          f'Tropical Storm probability: {mediumProb:.2f}%\nA deadly storm probability: {highProb:.2f}%\n')

    print(f'The f1 score (average=micro) of our model is: {f1_score(y_test, y_pred, average="micro")}')
    print(f'The Accuracy rate of our model is: {metrics.accuracy_score(y_test, y_pred)}')
    print(f'The Precision rate (average=micro) of our model is: '
          f'{metrics.precision_score(y_test, y_pred, average="micro")}')
    print(f'The Recall rate (average=micro)of our model is: {metrics.recall_score(y_test, y_pred, average="micro")}')
    print('Confusion Matrix of beaufort rate 0-3:')
    print(metrics.confusion_matrix(y_test, y_pred))


def printMenu():
    print('Please enter [0] to Exit\n'
          'please enter [1] to Linear model\n'
          'Please enter [2] to Logistic model')


def chooseModel():
    printMenu()
    userInput = int(input())
    while userInput != 0:
        if userInput == 0:
            break
        elif userInput == 1:
            linearRegressionModel(df)
        elif userInput == 2:
            logisticRegressionModel(df)
        printMenu()
        userInput = int(input('Please enter number in the list.'))


df = pd.read_csv('cleaningDF.csv')

chooseModel()
