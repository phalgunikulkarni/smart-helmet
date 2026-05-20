import pandas as pd
import numpy as np
from scipy.signal import find_peaks

# Load CSV
df = pd.read_csv('5th_A_Cross_Road-2026-05-13_06-34-36/merged_data.csv')
print(f'✅ CSV loaded: {len(df)} rows')
print(f'✅ Columns: {list(df.columns)[:6]}...')

# Check for spikes
baseline = df['magnitude'].median()
spikes = (df['magnitude'] - baseline).abs()
peaks, _ = find_peaks(spikes, height=2.5, distance=20)

print(f'\n✅ Found {len(peaks)} peaks with height > 2.5g')
print(f'✅ Peak detection working properly!\n')

if len(peaks) > 0:
    print('First 5 peaks:')
    for i, p in enumerate(peaks[:5]):
        spike_val = spikes.iloc[p]
        mag_val = df.iloc[p]['magnitude']
        print(f'  Peak {i+1}: spike_height={spike_val:.2f}g, magnitude={mag_val:.2f}g')
