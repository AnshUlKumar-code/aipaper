# Requirements: streamlit
# Run: streamlit run app.py

import streamlit as st
import json
import subprocess
import pandas as pd
from pathlib import Path
from PIL import Image

st.title('Smart Parking Allocation — Demo')

# Upload JSON files
uploaded_cars = st.file_uploader('Upload vehicles JSON', type='json')
uploaded_slots = st.file_uploader('Upload slots JSON', type='json')

if uploaded_cars and uploaded_slots:
    # Load JSON
    cars = json.load(uploaded_cars)
    slots = json.load(uploaded_slots)

    # Show tables
    st.write('Vehicles:', pd.json_normalize(cars))
    st.write('Slots:', pd.json_normalize(slots))

    if st.button('Run allocation'):
        # Save temp files
        Path('temp_input_cars.json').write_text(json.dumps(cars))
        Path('temp_input_slots.json').write_text(json.dumps(slots))

        # Run agent
        cmd = [
            'python',
            '../agent/agent.py',
            '--input', 'temp_input_cars.json',
            '--slots', 'temp_input_slots.json',
            '--out', '../allocations.csv'
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)

        # Show agent output
        st.text('Agent output:')
        st.code(res.stdout)

        # Show latest allocations
        allocations_file = Path('../allocations.csv')
        if allocations_file.exists():
            df = pd.read_csv(allocations_file)
            st.dataframe(df.tail(20))
        else:
            st.write('No allocations file generated.')

        # Show heatmap
        heatmap_file = Path('../heatmap/heatmap.png')
        if heatmap_file.exists():
            st.image(str(heatmap_file))
        else:
            st.write('No heatmap yet — run heatmap generator.')
