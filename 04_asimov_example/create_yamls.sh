#! /bin/bash

###########
# Part 01 #
###########
# Generate all the yamls for individual events and individual waveforms
# (Erase the "> /dev/null 2>&1" to avoid surpressing print statements)

# Source: https://git.ligo.org/deanna.fernando/settings/-/blob/main/analysis_scripts/02_create_yamls.sh?ref_type=heads

echo "Generate all the yaml files..."

python generate_yamls.py > /dev/null 2>&1


# Generate yamls for individual events with all waveforms

cd test_yamls

while read -r line; do
    # Extract the event_name
    event_name=$(echo "$line" | awk '{print $1}')
    mkdir -p "All-Waveforms/$event_name"
    # Save the following content to a file called sample_rift.yaml in the event_name folder
    cat <<EOF > "All-Waveforms/$event_name/sample_rift.yaml"
kind: analysis
name: Bayeswave
pipeline: bayeswave
comment: Bayeswave on-source PSD estimation job
EOF
    # Append the content including and after "---" from other files
    awk '/^---/{flag=1} flag' "IMRPhenomPv2/$event_name/sample_rift.yaml"  >> "All-Waveforms/$event_name/sample_rift.yaml"
    awk '/^---/{flag=1} flag' "SEOBNRv4PHM/$event_name/sample_rift.yaml"  >> "All-Waveforms/$event_name/sample_rift.yaml"
    awk '/^---/{flag=1} flag' "SEOBNRv5PHM/$event_name/sample_rift.yaml"  >> "All-Waveforms/$event_name/sample_rift.yaml"
done < ../run_list.txt

echo "Done"

###########
# Part 02 #
###########
# Convert psd.dat files to xml files (supresses any error messages if one of the .dat files does not exist)

echo "Converting extracted psd.dat files to xml files..."
while read -r line; do
    # Extracting the event name from the first column using awk
    event_name=$(echo "$line" | awk '{print $1}')
    cd psds/$event_name/
    convert_psd_ascii2xml --fname-psd-ascii H1-psd.dat --ifo H1 --conventional-postfix 2>/dev/null
    convert_psd_ascii2xml --fname-psd-ascii L1-psd.dat --ifo L1 --conventional-postfix 2>/dev/null
    convert_psd_ascii2xml --fname-psd-ascii V1-psd.dat --ifo V1 --conventional-postfix 2>/dev/null
    cd ../../
done < ../run_list.txt
echo "Done"


###########
# Part 03 #
###########
# Copy over the PE priors and defaults

echo "Copying over the PE priors and defaults..."
while read -r line; do
    # Extracting the event name from the first column using awk
    event_name=$(echo "$line" | awk '{print $1}')
    cp IMRPhenomPv2/$event_name/production_pe_priors.yaml All-Waveforms/$event_name
    cp IMRPhenomPv2/$event_name/testing_pe_osg.yaml All-Waveforms/$event_name
done < ../run_list.txt
echo "Done"




