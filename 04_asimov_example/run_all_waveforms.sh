#! /bin/bash

# Source: https://git.ligo.org/deanna.fernando/settings/-/blob/main/analysis_scripts/04_run_all_waveforms.sh?ref_type=heads

codename="asimov-demo-AllWaveforms"

mkdir $codename
cd $codename

analysisname=("All-Waveforms")

mkdir $analysisname
cd $analysisname

asimov init "$analysisname Analysis"

asimov configuration update condor/user ${USER}
asimov configuration update pipelines/environment /cvmfs/oasis.opensciencegrid.org/ligo/sw/conda/envs/igwn-py39-testing
asimov configuration update pesummary/executable /cvmfs/oasis.opensciencegrid.org/ligo/sw/conda/envs/igwn-py39-testing/bin/summarypages
asimov configuration update general/webroot /home/${USER}/public_html/asimov-demo/$codename/$analysisname

sed -i '/^\[general\]/a osg = True' .asimov/asimov.conf
export SINGULARITY_RIFT_IMAGE='/cvmfs/singularity.opensciencegrid.org/james-clark/research-projects-rit/rift:test'

while read -r line; do
    	event=$(echo "$line" | awk '{print $1}')
	asimov apply -f ../../test_yamls/$analysisname/$event/testing_pe_osg.yaml
	asimov apply -f ../../test_yamls/$analysisname/$event/production_pe_priors.yaml
	asimov apply -f ../../events/gwtc-3-peconfig/$event.yaml
	asimov apply -f ../../test_yamls/$analysisname/$event/sample_rift.yaml -e $event
done < ../../run_list.txt 

asimov monitor --chain
asimov start

