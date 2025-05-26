

retrieve_data:
	mkdir frames; exit 0
	for i in H L V; do curl    https://dcc.ligo.org/public/0146/P1700349/001/$${i}-$${i}1_LOSC_CLN_16_V1-1187007040-2048.gwf  >  frames/$${i}-$${i}1_LOSC_CLN_16_V1-1187007040-2048.gwf; done

local.cache:
	find frames -name '*.gwf' | lal_path2cache > local.cache

coinc.xml:
	gracedb get file G298048 coinc.xml > coinc.xml   # modern gracedb, helps us get standard event time and central parameters
	ligolw_no_ilwdchar coinc.xml

# https://dcc.ligo.org/LIGO-P1900011/public
psds: Makefile
	mkdir psds; exit 0
	curl https://dcc.ligo.org/public/0158/P1900011/001/GWTC1_GW170817_PSDs.dat  > psds/net_psd.dat
	(cd psds;  \
	cat net_psd.dat | awk '{print $$1, $$2}' > H1-psd.dat; \
	cat net_psd.dat | awk '{print $$1, $$3}' > L1-psd.dat; \
	cat net_psd.dat | awk '{print $$1, $$4}' > V1-psd.dat)
	(cd psds; \
	convert_psd_ascii2xml --fname-psd-ascii H1-psd.dat --ifo H1 --conventional-postfix; \
	convert_psd_ascii2xml --fname-psd-ascii L1-psd.dat --ifo L1 --conventional-postfix; \
	convert_psd_ascii2xml --fname-psd-ascii V1-psd.dat --ifo V1 --conventional-postfix; )

rundir_GW170817_knownhost_inclprior_DiColambda-2:
	util_RIFT_pseudo_pipe.py --use-ini `pwd`/GW170817.ini --use-rundir `pwd`/$@ --use-coinc `pwd`/coinc.xml  --fake-data-cache `pwd`/local.cache
	cp psds/*psd.xml.gz $@/

