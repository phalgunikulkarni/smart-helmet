import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle

features_df = pd.read_csv('Dr_Vishnuvardhan_Road-2026-05-13_07-07-49 labelled/windowed_features.csv')

print('Loading and preparing data...')
print(f'Missing values:\n{features_df.isnull().sum()}\n')

features_df = features_df.fillna(0)
X = features_df.drop('label', axis=1) 
y = features_df['label']

print(f'Features shape: {X.shape}, Labels shape: {y.shape}')
print(f'Label values: {y.unique()}\n')

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Training set: {len(X_train)} samples")
print(f"Testing set: {len(X_test)} samples")
print(f"\nTraining label distribution:")
print(y_train.value_counts())
print(f"\nTesting label distribution:")
print(y_test.value_counts())

print("\nTraining Random Forest model...")
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced', max_depth=15, n_jobs=-1)
model.fit(X_train, y_train)
print("Model training completed!")

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f'\nAccuracy Score: {accuracy:.4f} ({accuracy*100:.2f}%)')

cm = confusion_matrix(y_test, y_pred)
print(f'\nConfusion Matrix:\n{cm}')

print("\nClassification report:")
print(classification_report(y_test, y_pred))

importances = model.feature_importances_
feature_names = X.columns

print("\nTop 10 most important features:")
top_features = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
for name, importance in top_features[:10]:
    print(f"  {name}: {importance:.4f}")

model_path = 'train_pothole_model.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print(f"\nModel saved to: {model_path}")

info = {
    'accuracy': accuracy,
    'n_features': len(feature_names),
    'feature_importances': feature_names.tolist(),
    'classes': model.classes_.tolist()
}

with open('model_info.pkl', 'wb') as f:
    pickle.dump(info, f)
print("Model info saved!")
