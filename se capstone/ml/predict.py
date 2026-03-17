import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, '..', 'weight_readings.csv')
MODEL_PATH = os.path.join(BASE, 'model.pkl')

DAY_MAP  = {'Monday':0,'Tuesday':1,'Wednesday':2,'Thursday':3,'Friday':4,'Saturday':5,'Sunday':6}
TIME_MAP = {'Morning':0,'Afternoon':1,'Evening':2,'Night':3}
AREA_MAP = {'Residential':0,'Market':1,'Commercial':2,'School Zone':3,'Beach':4}

def train():
    df      = pd.read_csv(DATA)
    bins_df = pd.read_csv(os.path.join(BASE, '..', 'bins.csv'))
    df = df.merge(bins_df[['bin_id','area_type','capacity_kg']], on='bin_id', how='left')
    df['day_num']      = df['day_of_week'].map(DAY_MAP).fillna(0)
    df['time_num']     = df['time_of_day'].map(TIME_MAP).fillna(0)
    df['area_num']     = df['area_type'].map(AREA_MAP).fillna(0)
    df['will_overflow']= (df['fill_percent'] >= 80).astype(int)
    features = ['day_num','time_num','area_num','capacity_kg','fill_percent']
    X = df[features].fillna(0)
    y = df['will_overflow']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    print(f"Model accuracy: {score*100:.1f}%")
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    return model

def predict_all_bins(bins):
    if not os.path.exists(MODEL_PATH):
        train()
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    from datetime import datetime
    now  = datetime.now()
    day  = now.strftime('%A')
    hour = now.hour
    tod  = 'Morning' if 5<=hour<12 else ('Afternoon' if 12<=hour<17 else ('Evening' if 17<=hour<21 else 'Night'))
    results = []
    for b in bins:
        feat = [[DAY_MAP.get(day,0), TIME_MAP.get(tod,0), AREA_MAP.get(b.get('area_type','Residential'),0), b.get('capacity_kg',100), b.get('fill_percent',0)]]
        prob = model.predict_proba(feat)[0][1]
        results.append({
            'bin_id': b['bin_id'], 'zone': b.get('zone',''),
            'fill_percent': b.get('fill_percent',0),
            'area_type': b.get('area_type',''),
            'overflow_probability': round(prob*100,1),
            'risk': 'HIGH' if prob>=0.7 else ('MEDIUM' if prob>=0.4 else 'LOW')
        })
    results.sort(key=lambda x: x['overflow_probability'], reverse=True)
    return results

if __name__ == '__main__':
    train()
