from statistics import mode
import numpy as np
import pandas as pd
import os

labeled_folder = 'Dr_Vishnuvardhan_Road-2026-05-13_07-07-49 labelled'

# Load merged data
df = pd.read_csv(os.path.join(labeled_folder, 'merged_data.csv'))
df = df.fillna(0)

print('Loading merged data...')
print(f'Shape: {df.shape}')

# Add labels if not present
if 'label' not in df.columns:
    print('Adding labels from Annotation.csv...')
    annot_df = pd.read_csv(os.path.join(labeled_folder, 'Annotation.csv'))
    
    def find_annotation(sec_elapsed, window=0.5):
        matches = annot_df[
            (annot_df['seconds_elapsed'] >= sec_elapsed - window) & 
            (annot_df['seconds_elapsed'] <= sec_elapsed + window)
        ]
        if len(matches) > 0:
            closest = matches.loc[(matches['seconds_elapsed'] - sec_elapsed).abs().idxmin()]
            return closest['text']
        return "SMOOTH_ROAD"
    
    df['label'] = df['seconds_elapsed'].apply(find_annotation)
    print('Labels added!')

win_siz = 0.5
win_data = []
tot_time = df['seconds_elapsed'].max()
num_win = int(np.ceil(tot_time / win_siz))

print(f'Creating {num_win} windows (0.5s each)...\n')

for window in range(num_win):
    win_start = window * win_siz
    win_end = win_start + win_siz
    
    win_df = df[(df['seconds_elapsed'] >= win_start) & 
                (df['seconds_elapsed'] < win_end)]
    
    if win_df.empty:
        continue
    
    accel_x_means = win_df['accel_x'].mean()
    accel_x_std = win_df['accel_x'].std()
    accel_x_min = win_df['accel_x'].min()
    accel_x_max = win_df['accel_x'].max()
    accel_x_range = accel_x_max - accel_x_min

    accel_y_means = win_df['accel_y'].mean()
    accel_y_std = win_df['accel_y'].std()   
    accel_y_min = win_df['accel_y'].min()
    accel_y_max = win_df['accel_y'].max()
    accel_y_range = accel_y_max - accel_y_min

    accel_z_means = win_df['accel_z'].mean()
    accel_z_std = win_df['accel_z'].std()
    accel_z_min = win_df['accel_z'].min()
    accel_z_max = win_df['accel_z'].max()
    accel_z_range = accel_z_max - accel_z_min

    accel_magnitude = np.sqrt(
        win_df['accel_x']**2 + 
        win_df['accel_y']**2 + 
        win_df['accel_z']**2
    )
    accel_magn_mean = accel_magnitude.mean()
    accel_magn_std = accel_magnitude.std()
    accel_magn_max = accel_magnitude.max()

    gyro_x_means = win_df['gyro_x'].mean()
    gyro_x_std = win_df['gyro_x'].std()
    gyro_x_min = win_df['gyro_x'].min()
    gyro_x_max = win_df['gyro_x'].max()
    gyro_x_range = gyro_x_max - gyro_x_min

    gyro_magnitude = np.sqrt(
        win_df['gyro_x']**2 + 
        win_df['gyro_y']**2 + 
        win_df['gyro_z']**2
    )
    gyro_magn_mean = gyro_magnitude.mean()
    gyro_magn_std = gyro_magnitude.std()
    gyro_magn_max = gyro_magnitude.max()

    gravity_x_means = win_df['gravity_x'].mean()
    gravity_x_std = win_df['gravity_x'].std()
    gravity_x_min = win_df['gravity_x'].min()
    gravity_x_max = win_df['gravity_x'].max()
    gravity_x_range = gravity_x_max - gravity_x_min

    gravity_magnitude = np.sqrt(
        win_df['gravity_x']**2 + 
        win_df['gravity_y']**2 + 
        win_df['gravity_z']**2
    )
    gravity_magn_mean = gravity_magnitude.mean()
    gravity_magn_std = gravity_magnitude.std()
    gravity_magn_max = gravity_magnitude.max()

    label = mode(win_df['label'].dropna())

    feature_dict = {
        'win_start': win_start,
        'win_end': win_end,
        'num_samples': len(win_df),
        'accel_x_mean': accel_x_means,
        'accel_x_std': accel_x_std,
        'accel_x_min': accel_x_min,
        'accel_x_max': accel_x_max,
        'accel_x_range': accel_x_range,
        'accel_y_mean': accel_y_means,
        'accel_y_std': accel_y_std,
        'accel_y_min': accel_y_min,
        'accel_y_max': accel_y_max,
        'accel_y_range': accel_y_range,
        'accel_z_mean': accel_z_means,
        'accel_z_std': accel_z_std,
        'accel_z_min': accel_z_min,
        'accel_z_max': accel_z_max,
        'accel_z_range': accel_z_range,
        'accel_magn_mean': accel_magn_mean,
        'accel_magn_std': accel_magn_std,
        'accel_magn_max': accel_magn_max,
        'gyro_x_mean': gyro_x_means,
        'gyro_x_std': gyro_x_std,
        'gyro_x_min': gyro_x_min,
        'gyro_x_max': gyro_x_max,
        'gyro_x_range': gyro_x_range,
        'gyro_magn_mean': gyro_magn_mean,
        'gyro_magn_std': gyro_magn_std,
        'gyro_magn_max': gyro_magn_max,
        'gravity_x_mean': gravity_x_means,
        'gravity_x_std': gravity_x_std,
        'gravity_x_min': gravity_x_min,
        'gravity_x_max': gravity_x_max,
        'gravity_x_range': gravity_x_range,
        'gravity_magn_mean': gravity_magn_mean,
        'gravity_magn_std': gravity_magn_std,
        'gravity_magn_max': gravity_magn_max,
        'label': label
    }
    win_data.append(feature_dict)

print(f"Processing complete! Created {len(win_data)} windows.\n")

features_df = pd.DataFrame(win_data)
print(f"Windowed Features DataFrame:")
print(f"  Shape: {features_df.shape[0]} windows × {features_df.shape[1]} features")
print(f"\nLabel distribution:")
print(features_df['label'].value_counts())

output_path = os.path.join(labeled_folder, 'windowed_features.csv')
features_df.to_csv(output_path, index=False)
print(f"\n✓ Saved to: {output_path}")
print(f"File size: {features_df.memory_usage(deep=True).sum() / 1024:.2f} KB")
