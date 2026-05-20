"""
Curve-Based Peak Detection for Pothole/Speed Bump Classification
Approach 2: Time Series Analysis with Acceleration Peaks

This pipeline:
1. Extracts acceleration curves from sensor data
2. Detects peaks in the acceleration magnitude
3. Classifies events based on peak characteristics
4. Generates spatial-temporal hazard map

Author: Smart Helmet Team
Date: May 2026
"""

import pandas as pd
import numpy as np
import os
import glob
from scipy.signal import find_peaks

detected_anomalies_list = []
def calculate_curve_features(df):
    """
    Calculate heuristic curve features
    """

    features = {}

    features['rise_rate'] = df['absolute_spike'].diff().max()

    features['fall_rate'] = abs(df['absolute_spike'].diff().min())

    features['curve_skewness'] = (
        df['absolute_spike'].skew()
        if len(df) > 2 else 0
    )

    features['curve_variance'] = (
        df['absolute_spike'].var()
        if len(df) > 1 else 0
    )

    gyro_x = df['gyro_x'].abs().mean()
    gyro_y = df['gyro_y'].abs().mean()
    gyro_z = df['gyro_z'].abs().mean()

    features['gyro_magnitude'] = (
        gyro_x + gyro_y + gyro_z
    )

    features['z_component'] = (
        df['accel_z'].abs().max()
    )

    features['num_local_peaks'] = (
        (df['absolute_spike'] > 2.0).sum()
    )

    return features
def classify_anomaly(peak_height, elevated_duration, features):
    """
    Heuristic anomaly classification
    """

    rise_rate = features['rise_rate']
    fall_rate = features['fall_rate']
    curve_skewness = features['curve_skewness']
    gyro_magnitude = features['gyro_magnitude']
    z_component_spike = features['z_component']
    num_local_peaks = features['num_local_peaks']

    pothole_score = (
        (peak_height * 0.3) +
        ((25 - elevated_duration) * 0.2) +
        (abs(curve_skewness) * 0.2) +
        (z_component_spike * 0.15)
    )

    speed_bump_score = (
        (peak_height * 0.25) +
        ((elevated_duration - 5) * 0.25) +
        ((1 - abs(curve_skewness)) * 0.25)
    )

    anomaly_class = "Smooth road"
    confidence_score = 0.85

    if pothole_score > speed_bump_score and pothole_score > 2.0:

        if peak_height >= 4.5 and elevated_duration < 10:

            anomaly_class = "Pothole"

            confidence_score = min(
                pothole_score / 5.0,
                1.0
            )

    elif speed_bump_score > 2.2:

        if peak_height >= 2.0 and elevated_duration >= 8:

            anomaly_class = "Speed bump"

            confidence_score = min(
                speed_bump_score / 5.0,
                1.0
            )

    return (
        anomaly_class,
        confidence_score,
        pothole_score,
        speed_bump_score
    )

def process_session_curves(folder_path):
    """
    Process a session folder to detect and classify road hazards using curve analysis
    
    Args:
        folder_path: Path to session folder containing sensor CSVs
    
    Returns:
        result_df: DataFrame with merged sensor data and computed metrics
    """
    
    # 1. Ingest core accelerometer telemetry stream
    accel_df = pd.read_csv(os.path.join(folder_path, 'Accelerometer.csv'))
    accel_df = accel_df.rename(columns={'x': 'accel_x', 'y': 'accel_y', 'z': 'accel_z'})
    accel_df = accel_df[['time', 'seconds_elapsed', 'accel_x', 'accel_y', 'accel_z']]
    result_df = accel_df.copy().sort_values('seconds_elapsed')

    # Compute raw vector magnitude metric across spatial dimensions
    result_df['magnitude'] = np.sqrt(
        result_df['accel_x']**2 + 
        result_df['accel_y']**2 + 
        result_df['accel_z']**2
    )

    # 2. Append supplemental gyroscope stream
    gyro_path = os.path.join(folder_path, 'Gyroscope.csv')
    if os.path.exists(gyro_path):
        gyro_df = pd.read_csv(gyro_path).rename(columns={'x': 'gyro_x', 'y': 'gyro_y', 'z': 'gyro_z'})
        result_df = pd.merge_asof(
            result_df, 
            gyro_df.sort_values('seconds_elapsed')[['seconds_elapsed', 'gyro_x', 'gyro_y', 'gyro_z']], 
            on='seconds_elapsed', 
            direction='nearest'
        )

    # 3. Append supplemental gravity component baseline reference
    gravity_path = os.path.join(folder_path, 'Gravity.csv')
    if os.path.exists(gravity_path):
        gravity_df = pd.read_csv(gravity_path).rename(columns={'x': 'gravity_x', 'y': 'gravity_y', 'z': 'gravity_z'})
        result_df = pd.merge_asof(
            result_df, 
            gravity_df.sort_values('seconds_elapsed')[['seconds_elapsed', 'gravity_x', 'gravity_y', 'gravity_z']], 
            on='seconds_elapsed', 
            direction='nearest'
        )

    # 4. Append low-frequency GPS geolocation spatial array
    location_path = os.path.join(folder_path, 'Location.csv')
    if os.path.exists(location_path):
        loc_df = pd.read_csv(location_path).sort_values('seconds_elapsed')
        result_df = pd.merge_asof(
            result_df, 
            loc_df[['seconds_elapsed', 'latitude', 'longitude', 'speed']], 
            on='seconds_elapsed', 
            direction='nearest'
        )

    # 5. Extract continuous wave variations (Approach 2 Peak Detection Loop)
    baseline_gravity = result_df['magnitude'].median()
    result_df['absolute_spike'] = (result_df['magnitude'] - baseline_gravity).abs()
    
    # Identify local wave maximum spikes
    peaks, _ = find_peaks(result_df['absolute_spike'], height=2.5, distance=20)
    
    for peak_idx in peaks:
        timestamp = result_df.iloc[peak_idx]['seconds_elapsed']
        peak_height = result_df.iloc[peak_idx]['absolute_spike']
        
        # Isolate localized continuous wave slice around target index point
        slice_start = max(0, peak_idx - 15)
        slice_end = min(len(result_df), peak_idx + 15)
        curve_slice = result_df.iloc[slice_start:slice_end]
        
        # Calculate dynamic width signature (duration) of the spike vibration
        elevated_duration = (curve_slice['absolute_spike'] > 1.2).sum()
        
        # Evaluate physical threshold signatures
        if peak_height >= 5.5 and elevated_duration < 8:
            anomaly_class = "Pothole"
        elif peak_height >= 2.5 and elevated_duration >= 8:
            anomaly_class = "Speed bump"
        else:
            anomaly_class = "False error"
            
        detected_anomalies_list.append({
            'folder_session': os.path.basename(folder_path),
            'seconds_elapsed': timestamp,
            'peak_height': peak_height,
            'vibration_duration_samples': elevated_duration,
            'latitude': result_df.iloc[peak_idx]['latitude'] if 'latitude' in result_df.columns else 0,
            'longitude': result_df.iloc[peak_idx]['longitude'] if 'longitude' in result_df.columns else 0,
            'speed': result_df.iloc[peak_idx]['speed'] if 'speed' in result_df.columns else 0,
            'predicted_anomaly_type': anomaly_class
        })

    # Save tracking reference metrics back to the session archive
    result_df.to_csv(os.path.join(folder_path, 'merged_data.csv'), index=False)
    return result_df

if __name__ == "__main__":
    search_pattern = os.path.join('.', '**', 'Accelerometer.csv')
    active_folders = sorted(list(set([os.path.dirname(f) for f in glob.glob(search_pattern, recursive=True)])))
    
    print("="*70)
    print("CURVE-BASED POTHOLE DETECTION PIPELINE (Approach 2)")
    print("="*70)
    print(f"\nTargeting {len(active_folders)} active session logs...\n")
    
    for session in active_folders:
        try:
            process_session_curves(session)
            print(f"[OK] Successfully extracted curves from: {session}")
        except Exception as error_msg:
            print(f"[SKIP] Skipped processing path [{session}]: {error_msg}")
    
    print("\n" + "="*70)        
    if detected_anomalies_list:
        summary_export_df = pd.DataFrame(detected_anomalies_list).fillna(0)
        print("DETECTION RESULTS")
        print("="*70)
        print(f"\nTotal anomalies detected: {len(summary_export_df)}")
        print("\nAnomaly Type Distribution:")
        print(summary_export_df['predicted_anomaly_type'].value_counts())
        
        summary_export_df.to_csv('all_detected_hazards.csv', index=False)
        print(f"\nMaster spatial record saved to: all_detected_hazards.csv")
        print(f"File location: {os.path.abspath('all_detected_hazards.csv')}")
    else:
        print("NO ANOMALIES DETECTED")
        print("="*70)
