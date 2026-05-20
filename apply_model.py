import pickle 
import pandas as pd
import glob
import os

with open('train_pothole_model.pkl', 'rb') as f:
    model = pickle.load(f)
print("Model loaded successfully!")

unlabelled_folders = ['2026-05-09_02-29-53', '5th_A_Cross_Road-2026-05-13_06-34-36', 'Subramanya_Pura_Road-2026-05-09_02-41-24']

for folder in unlabelled_folders:
    feature_path = os.path.join(folder, 'windowed_features.csv')
    if not os.path.exists(feature_path):
        print(f"Feature file not found in {folder}. Skipping...")
        continue
    features_df = pd.read_csv(feature_path)
    X = features_df.drop('label', axis=1)

    predictions = model.predict(X)
    confidences = model.predict_proba(X).max(axis=1)

    features_df['predicted_label'] = predictions
    features_df['confidence'] = confidences

    output_path = os.path.join(folder, 'windowed_features_with_predictions.csv')
    features_df.to_csv(output_path, index=False)
    print(f"\nFolder: {folder}")
    print(f"Predictions distribution:")
    print(features_df['predicted_label'].value_counts())
    print(f"Average confidence: {confidences.mean():.2%}")

print("\n" + "="*70)
print("PREDICTION SUMMARY - ALL FOLDERS")
print("="*70)
