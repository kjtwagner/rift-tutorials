Setting up a RIFT run for real data is more straightforward once you have your environment and path properly configured. Make sure you have properly sourced your environment and setup your path variables before you begin. New users are advised to look carefully at the files they are asked to run and use. Blindly running commands will work, but is not the best way to learn.

RIFT was originally developed to perform parameter inference on binary black hole (BBH) mergers, but it has since been extended to include binary neutron star (BNS) sources. For BNS systems, users can incorporate external likelihoods and priors specific to neutron star physics. I can model tidal deformability parameters ($\lambda_1, \lambda_2$), which offer insight into the internal structure of neutron stars and help constrain the nuclear equation of state (EOS). This makes RIFT a powerful tool for multi-messenger astrophysics and nuclear physics studies.

### Building the run directory
For this event, we use an external supplementary prior. These functions are contained in an external script called `external_prior_example.py`. You must put the external prior file into a place where RIFT can find it. To do this, you can add the current directory to your `PYTHONPATH`. Setting the `PYTHONPATH` environment variable tells Python where to look for modules and packages that aren't in the standard library or  working directory. It’s useful when you want to import code from other directories in your project without installing it as a package, and is particularly important when you submit local jobs to HTCondor.  Before you source your setup scrupt, open it (`setup.sh`), and add the following line anywhere after your `conda activate`, if it's present:
```
export PYTHONPATH=/home/albert.einstein/PATH_TO_PRIOR/:${PYTHONPATH}
```
where `PATH_TO_PRIOR` is a placeholder that represents the location you have this repository checked out. You can find this place by running `pwd` in the directory where this tutorial file is located. For example, the author's path would be `/home/katelyn.wagner/rift-tutorials/03b_real_data_bns/`, so the `PYTHONPATH` variable would be:
```
export PYTHONPATH=/home/katelyn.wagner/rift-tutorials/03b_real_data_bns/:${PYTHONPATH}
```
Once the line is properly added according to *your* paths, you can source your env and setup script as usual. Then, `cd` into your `/rift-tutorials/03b_real_data_bns/` folder.

Next, to build the actual run directory, you need to authenticate your username to be able to download data from online. Run the following command:

```
htgettoken -a vault.ligo.org -i igwn
```

This will provide you a browser link to complete the authentication. Copy and paste the output link into your browser and log in. Return to your terminal to continue. You should see some output like:

```
Storing vault token in /tmp/<rand>
Saving credkey to /home/albert.einstein/.config/htgettoken/credkey-igwn-default
Saving refresh token ... done
```

There is now an authentication token associated with your albert.einstein account and the following commands will work. For now, this example uses a Makefile to retrieve the necessary files and build the run directory.

With your usual environment and setup script sourced, begin by running the following command to retrieve the data frames for this event:
```
make retrieve_data
```
New users mote that when you're using the command line, you can type a few letters and then press tab to complete your request, something like `make re<TAB>`. This is nice for speed and to confirm you're in the right place. There will be some output text from above, but you should end up with a `frames` directory that contains H/L/V frames. 

Next, run `make local.cache` to store the paths to the frames to later tell RIFT where to find them, and avoid a duplicate download. Then, get a file called `coinc.xml` by simply running:
```
make coinc.xml
```
This calls out to GraceDB, the open GW data web storage, to retrieve this file which contains important information about event time and central parameters for the particular event. RIFT will also later need to know about this. Finally, you need the PSDs, or Power Spectral Densities. These describe the characteristic noise of the detector as a function of frequency. Knowing the real PSD of the detector helps extract the astrophysical signal from the known noise. Each detector has its own PSD. For this event for now, retrieve them as
```
make psds
```
This will make a psd directory, download them from online (the dcc, for now), and convert them to the appropriate format for RIFT. Finally, you're ready to build the run directory. Before you run the following command, make sure you open the ini file and change the `accounting_group_user` to your own. Use tab complete, but the command is:
```
make rundir_GW170817_knownhost_inclprior_DiColambda-2
```
This calls our internal pipeline builder, a script called `util_RIFT_pseduo_pipe.py`. This is a giant master script which contains defaults for settings and calls to other scripts to properly build the run directory, condor submit files, and the DAG. It uses sensible defaults, you can customize the run by passing an .ini configuration file.

HTCondor submit files define how to run individual jobs on a computing cluster, specifying the executable, arguments, and input/output files. For our workflow, a DAG (Directed Acyclic Graphs) is used to manage dependencies between multiple jobs, ensuring they run in the correct order. DAGs make it easy to chain together and/or parallelize stages.

Once the `rundir...` appears, `cd` into it and take a few minutes to look through the files. Then, with your env and setup script (still) sourced, run
```
./command-single.sh
```
This runs a single instance of ILE to verify that the correct files are present and the job should be able to run if submitted to the cluster. You're looking for some output similar to:
```
-------> Arguments ('right ascension', 'declination', 'phi _orb', 'inclination', 'psi', 'distance')
mcsampler : providing verbose output .....
iteration Neff sqrt (2*lnLmax) sart (2*lnLmarg) In (Z/Lmax) int_var
: 10000 12.307066439716408 6.824081525864119 5.944754763710367 -5.613989735491433 0.18414994040088967
Worthwhile modes : {(2, -2), (2, 2)}
```
It this appears, you can press ctrl-C to halt the process. If there are errors, reach out for help to debug. Finally, you're ready to submit the job to HTcondor to run:
```
condor_submit_dag marginalize_intrinsic_parameters_BasicIterationWorkflow.dag
```
Then type `condor_q` to check the status of the run. If the job is running well, there should always be jobs in the RUN and IDLE categories:
```
OWNER           BATCH_NAME             SUBMITTED    DONE    RUN    IDLE    TOTAL   JOB_IDS
katelyn.wagner master.dag+54824584    3/25 20:31    24580    41     795    43111   54825855.0...54876867.0
```

Once the job completes (or sometimes, fails, but see the debugging section), it will disappear from `condor_q` and you can begin making plots. In brief, you can do the following, but see the plotting section for more detail.

Once your run completes, you can make corner plots to assess the accuracy of the parameter recovery performed by RIFT in your run. RIFT contains a built in plotting code called `plot_posterior_corner.py` with default settings. The user can supply an `rcparams` file to modify the defaults. 

You must specify the posterior files you want to plot and the parameters you wish to include. You may also choose to plot the posterior samples generated from the final extrinsic recovery step. To do this, you need to change the parameters specified and the name of the posterior file containing the appropriate samples.
```
    plot_posterior_corner.py --posterior-file posterior_samples-1.dat
     --posterior-label 0 --posterior-file posterior_samples-2.dat  --posterior-label 1 
     --parameter mc  --parameter q  --parameter chi_eff --use-legend --ci-list [0.9] --quantiles None --lnL-cut 15 
     --use-all-composite-but-grayscale --composite-file all.net
```
You can view the plots by navigate to `/home/albert.einstein/public_html/` and making a symbolic link to your run directory using `ln -s <PATH_TO_RUNDIR>`. Then, go to `https://ldas-jobs.ligo.caltech.edu/~albert.einstein` to view your files.

For more info about this event, in particular using RIFT with matter settings, see the following relevant papers:
- Neutron star EOS: [arXiv:2407.15753](https://arxiv.org/pdf/2407.15753)
- Kilonova Inference: [arXiv:2503.12320](https://arxiv.org/pdf/2503.12320)