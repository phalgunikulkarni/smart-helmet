import os
import glob

search_path = os.path.join('.', '**', 'Accelerometer.csv')
print(f"Search pattern: {search_path}")

accelerometer_files = glob.glob(search_path, recursive=True)
print(f"Found {len(accelerometer_files)} Accelerometer.csv files:")
for f in accelerometer_files:
    print(f"  - {f}")

target_folders = sorted(list(set([os.path.dirname(f) for f in accelerometer_files])))
print(f"\nTarget folders: {len(target_folders)}")
for f in target_folders:
    print(f"  - {f}")
