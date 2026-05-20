import pandas as pd
import numpy as np
import os
import glob

def merge_folder(folder_path):
    accel_df = pd.read_csv(os.path.join(folder_path, 'Accelerometer.csv'))
    accel_df = accel_df.rename(columns={'x': 'accel_x', 'y': 'accel_y', 'z': 'accel_z'})
    accel_df = accel_df[['time', 'seconds_elapsed', 'accel_x', 'accel_y', 'accel_z']]
    result_df = accel_df.copy()
    
    result_df = result_df.sort_values('seconds_elapsed')

    gyro_path = os.path.join(folder_path, 'Gyroscope.csv')
    if os.path.exists(gyro_path):
        gyro_df = pd.read_csv(gyro_path)
        gyro_df = gyro_df.rename(columns={'x': 'gyro_x', 'y': 'gyro_y', 'z': 'gyro_z'})
        gyro_df = gyro_df.sort_values('seconds_elapsed')
        result_df = pd.merge_asof(
            result_df, 
            gyro_df[['seconds_elapsed', 'gyro_x', 'gyro_y', 'gyro_z']], 
            on='seconds_elapsed', 
            direction='nearest'
        )

    gravity_path = os.path.join(folder_path, 'Gravity.csv')
    if os.path.exists(gravity_path):
        gravity_df = pd.read_csv(gravity_path)
        gravity_df = gravity_df.rename(columns={'x': 'gravity_x', 'y': 'gravity_y', 'z': 'gravity_z'})
        gravity_df = gravity_df.sort_values('seconds_elapsed')
        result_df = pd.merge_asof(
            result_df, 
            gravity_df[['seconds_elapsed', 'gravity_x', 'gravity_y', 'gravity_z']], 
            on='seconds_elapsed', 
            direction='nearest'
        )

    location_path = os.path.join(folder_path, 'Location.csv')
    if os.path.exists(location_path):
        loc_df = pd.read_csv(location_path)
        loc_df = loc_df.sort_values('seconds_elapsed')
        result_df = pd.merge_asof(
            result_df, 
            loc_df[['seconds_elapsed', 'latitude', 'longitude', 'speed']], 
            on='seconds_elapsed', 
            direction='nearest'
        )

    annot_path = os.path.join(folder_path, 'Annotation.csv')
    if os.path.exists(annot_path):
        annot_df = pd.read_csv(annot_path)
        
        # Check if 'text' column exists
        if 'text' in annot_df.columns:
            def find_annotation(sec_elapsed, window=0.5):
                matches = annot_df[
                    (annot_df['seconds_elapsed'] >= sec_elapsed - window) & 
                    (annot_df['seconds_elapsed'] <= sec_elapsed + window)
                ]
                if len(matches) > 0:
                    closest = matches.loc[(matches['seconds_elapsed'] - sec_elapsed).abs().idxmin()]
                    return closest['text']
                return "Smooth Road"
                
            result_df['label'] = result_df['seconds_elapsed'].apply(find_annotation)
        else:
            result_df['label'] = "Smooth Road"
    else:
        result_df['label'] = "Smooth Road"

    output_file = os.path.join(folder_path, 'merged_data.csv')
    result_df.to_csv(output_file, index=False)
    print(f"Saved to {output_file}")
    
    return result_df

if __name__ == "__main__":
    search_path = os.path.join('.', '**', 'Accelerometer.csv')
    accelerometer_files = glob.glob(search_path, recursive=True)
    target_folders = sorted(list(set([os.path.dirname(f) for f in accelerometer_files])))
    
    print(f"Found {len(target_folders)} session folders to process.\n")
    print(f"Target folders: {target_folders}\n")
    
    for folder in target_folders:
        print(f"Processing: {folder}...")
        try:
            result = merge_folder(folder)
            print(f"  [OK] Merged successfully! Rows: {len(result)}")
        except Exception as e:
            print(f"  [ERROR] Error processing {folder}: {e}")
            import traceback
            traceback.print_exc()
            
    print("\nMerge complete!")
