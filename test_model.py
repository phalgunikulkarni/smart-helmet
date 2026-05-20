import pickle
import pandas as pd
import numpy as np

with open('train_pothole_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('model_info.pkl', 'rb') as f:
    info = pickle.load(f)

print('Model loaded successfully!')
print(f'Accuracy: {info["accuracy"]:.4f}')
print(f'Number of features: {info["n_features"]}')
print(f'Classes: {info["classes"]}')

features_df = pd.read_csv('Dr_Vishnuvardhan_Road-2026-05-13_07-07-49 labelled/windowed_features.csv')
sample_smooth = features_df[features_df['label'] == 'SMOOTH_ROAD'].iloc[0]
sample_pothole = features_df[features_df['label'] == 'Pothole'].iloc[0]
X_smooth = sample_smooth.drop('label').values.reshape(1, -1)
X_pothole = sample_pothole.drop('label').values.reshape(1, -1)

pred_smooth = model.predict(X_smooth)[0]
pred_pothole = model.predict(X_pothole)[0]
confidence_smooth = model.predict_proba(X_smooth)[0].max()
confidence_pothole = model.predict_proba(X_pothole)[0].max()

print(f'\nTest Prediction 1 (actual: SMOOTH_ROAD):')
print(f'  Predicted: {pred_smooth}')
print(f'  Confidence: {confidence_smooth:.2%}')

print(f'\nTest Prediction 2 (actual: Pothole):')
print(f'  Predicted: {pred_pothole}')
print(f'  Confidence: {confidence_pothole:.2%}')