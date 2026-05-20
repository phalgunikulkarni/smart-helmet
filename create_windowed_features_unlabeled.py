import pandas as pd
import numpy as np
from statistics import mode
import os

unlabeled_folders = [
    '2026-05-09_02-29-53',
    '5th_A_Cross_Road-2026-05-13_06-34-36',
    'Subramanya_Pura_Road-2026-05-09_02-41-24'
]

def create_windowed_features_from_merged(folder_path):
    merged_path = os.path.join(folder_path, 'merged_data.csv')
    
    if not os.path.exists(merged_path):
        print(f"  [SKIP] No merged_data.csv in {folder_path}")
        return
    
    print(f"\n[Processing] {folder_path}")
    df = pd.read_csv(merged_path)
    df = df.fillna(0)
    
    print(f"  Loaded: {len(df)} rows")
    
    win_siz = 0.5
    win_data = []
    tot_time = df['seconds_elapsed'].max()
    num_win = int(np.ceil(tot_time / win_siz))
    
    print(f"  Creating {num_win} windows (0.5s each)...")
    
    for window in range(num_win):
        win_start = window * win_siz
        win_end = win_start + win_siz
        
        win_df = df[(df['seconds_elapsed'] >= win_start) & 
                    (df['seconds_elapsed'] < win_end)]
        
        if win_df.empty:
            continue
        
        accel_magnitude = np.sqrt(
            win_df['accel_x']**2 + 
            win_df['accel_y']**2 + 
            win_df['accel_z']**2
        )
        
        gyro_magnitude = np.sqrt(
            win_df['gyro_x']**2 + 
            win_df['gyro_y']**2 + 
            win_df['gyro_z']**2
        )
        
        gravity_magnitude = np.sqrt(
            win_df['gravity_x']**2 + 
            win_df['gravity_y']**2 + 
            win_df['gravity_z']**2
        )
        
        feature_dict = {
            'win_start': win_start,
            'win_end': win_end,
            'num_samples': len(win_df),
            'accel_x_mean': win_df['accel_x'].mean(),
            'accel_x_std': win_df['accel_x'].std(),
            'accel_x_min': win_df['accel_x'].min(),
            'accel_x_max': win_df['accel_x'].max(),
            'accel_x_range': win_df['accel_x'].max() - win_df['accel_x'].min(),
            'accel_y_mean': win_df['accel_y'].mean(),
            'accel_y_std': win_df['accel_y'].std(),
            'accel_y_min': win_df['accel_y'].min(),
            'accel_y_max': win_df['accel_y'].max(),
            'accel_y_range': win_df['accel_y'].max() - win_df['accel_y'].min(),
            'accel_z_mean': win_df['accel_z'].mean(),
            'accel_z_std': win_df['accel_z'].std(),
            'accel_z_min': win_df['accel_z'].min(),
            'accel_z_max': win_df['accel_z'].max(),
            'accel_z_range': win_df['accel_z'].max() - win_df['accel_z'].min(),
            'accel_magn_mean': accel_magnitude.mean(),
            'accel_magn_std': accel_magnitude.std(),
            'accel_magn_max': accel_magnitude.max(),
            'gyro_x_mean': win_df['gyro_x'].mean(),
            'gyro_x_std': win_df['gyro_x'].std(),
            'gyro_x_min': win_df['gyro_x'].min(),
            'gyro_x_max': win_df['gyro_x'].max(),
            'gyro_x_range': win_df['gyro_x'].max() - win_df['gyro_x'].min(),
            'gyro_magn_mean': gyro_magnitude.mean(),
            'gyro_magn_std': gyro_magnitude.std(),
            'gyro_magn_max': gyro_magnitude.max(),
            'gravity_x_mean': win_df['gravity_x'].mean(),
            'gravity_x_std': win_df['gravity_x'].std(),
            'gravity_x_min': win_df['gravity_x'].min(),
            'gravity_x_max': win_df['gravity_x'].max(),
            'gravity_x_range': win_df['gravity_x'].max() - win_df['gravity_x'].min(),
            'gravity_magn_mean': gravity_magnitude.mean(),
            'gravity_magn_std': gravity_magnitude.std(),
            'gravity_magn_max': gravity_magnitude.max(),
            'label': 'SMOOTH_ROAD'
        }
        win_data.append(feature_dict)
    
    features_df = pd.DataFrame(win_data)
    output_path = os.path.join(folder_path, 'windowed_features.csv')
    features_df.to_csv(output_path, index=False)
    
    print(f"  [OK] Created {len(features_df)} windows")
    print(f"      Saved to: {output_path}")


print("="*70)
print("CREATING WINDOWED FEATURES FOR UNLABELED DATA")
print("="*70)

for folder in unlabeled_folders:
    create_windowed_features_from_merged(folder)

print("\n" + "="*70)
print("COMPLETE!")
print("="*70)
print("\nNext: Run apply_model.py to generate predictions")
