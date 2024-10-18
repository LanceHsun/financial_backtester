import joblib
from .models import StockData
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import os
import numpy as np
from django.conf import settings

MODEL_DIR = os.path.join(settings.BASE_DIR, 'ml_models')

def train_and_save_model(symbol):
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    data = StockData.objects.filter(symbol=symbol).order_by('date')
    df = pd.DataFrame(list(data.values()))

    df['target'] = df['close_price'].shift(-30)  # Predict 30 days in the future
    df = df.dropna()

    features = ['open_price', 'high_price', 'low_price', 'close_price', 'volume']
    X = df[features]
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    model_path = os.path.join(MODEL_DIR, f'stock_predictor_{symbol}.pkl')
    joblib.dump({'model': model, 'features': features}, model_path)
    return model, features

def predict_stock_prices(symbol, days=30):
    model_path = os.path.join(MODEL_DIR, f'stock_predictor_{symbol}.pkl')
    
    if not os.path.exists(model_path):
        print(f"Model for {symbol} not found. Training new model...")
        model, features = train_and_save_model(symbol)
    else:
        loaded_data = joblib.load(model_path)
        model = loaded_data['model']
        features = loaded_data['features']
    
    latest_data = StockData.objects.filter(symbol=symbol).order_by('-date')[:days].values()
    
    if len(latest_data) < days:
        raise ValueError(f"Not enough data for {symbol}. Only {len(latest_data)} days available.")
    
    input_data = pd.DataFrame(list(latest_data))[features]
    
    predictions = []
    for _ in range(days):
        prediction = model.predict(input_data.iloc[[0]])[0]
        predictions.append(float(prediction))
        
        # Update input data for next prediction
        new_row = input_data.iloc[0].copy()
        new_row['close_price'] = prediction
        input_data = pd.concat([pd.DataFrame([new_row]), input_data.iloc[:-1]]).reset_index(drop=True)
    
    return predictions