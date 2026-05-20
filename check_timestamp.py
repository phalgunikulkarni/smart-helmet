import numpy as np
import datetime
import pandas as pd
import matplotlib.pyplot as plt

accel_df = pd.read_csv('Dr_Vishnuvardhan_Road-2026-05-13_07-07-49 labelled/Accelerometer.csv')
annot_df = pd.read_csv('Dr_Vishnuvardhan_Road-2026-05-13_07-07-49 labelled/Annotation.csv')

print("Accelerometer DataFrame:")
print(accel_df.head())

first_sensor_time_ns = accel_df.iloc[0]['time']
first_sensortime = first_sensor_time_ns/1e9
print("First sensor time (s):", first_sensortime)

print("Annotation DataFrame:")
print(annot_df.head())

annot_df['true_elapsed'] = (annot_df['time'] - first_sensor_time_ns) / 1e9
annot_df['drift'] = annot_df['seconds_elapsed'] - annot_df['true_elapsed']

mean_drift = annot_df['drift'].mean()
min_drift = annot_df['drift'].min()
max_drift = annot_df['drift'].max()
std_drift = annot_df['drift'].std()

gaps_list = []

for i in range(len(annot_df)-1):
    annot_time = annot_df.iloc[i]['seconds_elapsed']
    annot_time_next = annot_df.iloc[i+1]['seconds_elapsed'] if i+1 < len(annot_df) else None
    
    if annot_time_next is not None:
        gap = annot_time_next - annot_time
        gaps_list.append({
            'start_time': annot_time,
            'end_time': annot_time_next,
            'duration': gap,
            'event_after_gap': annot_df.iloc[i+1]['text']
        })

gap_0 = {
    'start_time': 0,
    'end_time': annot_df.iloc[0]['seconds_elapsed'],
    'duration': annot_df.iloc[0]['seconds_elapsed'],
    'event_after_gap': annot_df.iloc[0]['text']
}
gaps_list.insert(0, gap_0)

print("Drift Analysis:")
print(f"Mean Drift: {mean_drift:.2f} seconds")
print(f"Min Drift: {min_drift:.2f} seconds")
print(f"Max Drift: {max_drift:.2f} seconds")
print(f"Standard Deviation of Drift: {std_drift:.2f} seconds")
print("\nGaps Between Annotations:")
for gap in gaps_list:    
    print(f"Gap from {gap['start_time']:.2f} to {gap['end_time']:.2f} seconds (Duration: {gap['duration']:.2f} seconds) - Next Event: {gap['event_after_gap']}")
print("no. of gaps:", len(gaps_list))