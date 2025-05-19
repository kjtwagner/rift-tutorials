#! /bin/bash

# From "GWTC-3: Compact Binary Coalescences Observed by LIGO and Virgo During the Second Part of the Third Observing Run — Parameter estimation data release"
# https://zenodo.org/records/8177023

# Analysis of GWTC-3 with fully precessing numerical relativity surrogate models
# https://zenodo.org/records/8115310

# Source: https://git.ligo.org/deanna.fernando/settings/-/blob/main/analysis_scripts/01_download_h5_files.sh?ref_type=heads

files="downloaded_files"
mkdir $files
cd $files

# Download O3b release
python3 ../download_O3b_files.py ../run_list.txt

# Download previous NRSur7dq4 runs
while read -r line; do
    # Extracting the event name from the first column using awk
    event_name=$(echo "$line" | awk '{print $1}')
    echo "Downloading files for event: $event_name"

    url="https://zenodo.org/records/8115310/files/${event_name}_NRSur7dq4.h5"
    wget "$url"
    echo "Downloaded NRSur7dq4 file"
done < ../run_list.txt
