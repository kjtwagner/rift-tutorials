import re
import os
import h5py
import yaml
import numpy as np

from my_functions import get_event, get_value, get_type, get_string_value
from my_functions import string_dict_to_dict, convert_to_dict_NRSur
from my_functions import remove_none_values, save_psd_data
#################################################################################

###### IMRPhenomXPHM ############ IMRPhenomXPHM ############ IMRPhenomXPHM ######

#################################################################################


################
# Define Event #
################

folder = 'downloaded_files'
for filename in os.listdir(folder):
    if filename.startswith('IGWN') and filename.endswith('_PEDataRelease_mixed_cosmo.h5'):

        f = os.path.join(folder, filename)
        event    = get_event(filename)
        filepath = f'{folder}/{filename}'
        # Creates a directory for event
        os.makedirs(f"test_yamls/IMRPhenomPv2/{event}", exist_ok=True)
        os.makedirs(f"test_yamls/psds/{event}", exist_ok=True)
        
        ###############
        # Get Configs #
        ###############        

        with h5py.File(filepath, "r") as file:
            print(f'\n')
            print(f"Event {event}")           # TROUBLESHOOTING
            print(f"{filename}")
            # Get the psds
            try: 
                psd_dict = {}
                group0 = file["C01:IMRPhenomXPHM"]["psds"]
                for key, value in group0.items():
                    psd_dict[f'{key}'] = value[()] 
            except: 
                try:
                    psd_dict = {}
                    group0 = file["C01:IMRPhenomXPHM"]["config_file"]["config"]
                    for key, value in group0.items():
                        psd_dict[f'{key}'] = value[()] 
                except:
                    print("filepath group0 DNE")
#                 continue
 

            ##################
            # Save PSD Files #
            ##################

            count=0
            if "H1" in psd_dict:
                h1_data = {
                    'name': 'H1',
                    'data': psd_dict['H1'].tolist()
                }
                save_psd_data(h1_data['data'], f'test_yamls/psds/{event}/H1-psd.dat')
                count+=1

            if "L1" in psd_dict:
                l1_data = {
                    'name': 'L1',
                    'data': psd_dict['L1'].tolist()
                }
                save_psd_data(l1_data['data'], f'test_yamls/psds/{event}/L1-psd.dat')
                count+=1

            if "V1" in psd_dict:
                v1_data = {
                    'name': 'V1',
                    'data': psd_dict['V1'].tolist()
                }
                save_psd_data(v1_data['data'], f'test_yamls/psds/{event}/V1-psd.dat')
                count+=1

            if count==0:
                print(f"Could not make PSD files for {event}")

            print("Created PSDs")


 ####################################################################################

            #####################
            # Create YAML Files #
            #####################
            
            
            
            sample_rift_dict1 = [
                   {'kind': 'analysis',
                    'name': 'Bayeswave',
                    'pipeline': 'bayeswave',
                    'comment': 'Bayeswave on-source PSD estimation job' 
                    
                }
            ]
            
            sample_rift_dict2 = [
                   {'kind': 'analysis',
                    'name': 'rift-IMRPhenomPv2',
                    'status': 'Ready',
                    'pipeline': 'RIFT',
                    'needs': ["Bayeswave"],
                    'event': event,
                    'waveform': {
                        'approximant': 'IMRPhenomPv2'
                    },
                    'comment': 'This is a sample RIFT analysis',
                    'likelihood': {
                        'start frequency': 10,
                        'psd fractional overlap': float(get_value(filepath, ['psd-fractional-overlap'])) \
                            if get_value(filepath, ['psd-fractional-overlap']) is not None else None,
                        'psd length': int(get_value(filepath, ['psd-length', 'max-psd-length'])) \
                            if get_value(filepath, ['psd-length', 'max-psd-length']) is not None else None,
                        'psd maximum duration': int(get_value(filepath, ['psd-maximum-duration'])) \
                            if get_value(filepath, ['psd-maximum-duration']) is not None else None,
                        'psd method': get_value(filepath, ['psd-method']) \
                            if get_value(filepath, ['psd-method']) is not None else None,
                        'reference frequency': 10
                    },
                    'scheduler': {
                        'osg': True
                    }
                }
            ]

            sample_rift_dict2 = remove_none_values(sample_rift_dict2)
            combined_dicts = sample_rift_dict1 + sample_rift_dict2

            # Save dictionary to a YAML file
            with open(f'test_yamls/IMRPhenomPv2/{event}/sample_rift.yaml', 'w') as yaml_file:
                yaml.dump_all(combined_dicts, 
                              yaml_file,
                              default_flow_style=False, 
                              sort_keys=False,
                              indent=2)
            print('Created IMRPhenomPv2 sample_rift.yaml')
        

    
 #################################################################################### 

        production_pe_priors_dict = [
            {
                'kind': 'configuration',
                'priors': {
                    'amplitude order': int(get_value(filepath, ['pn-amplitude-order', 'amporder'])),
                    'chirp mass': {
                        'maximum': float(get_string_value(get_value(filepath, ['chirp_mass']), 'maximum')),
                        'minimum': float(get_string_value(get_value(filepath, ['chirp_mass']), 'minimum')),
                        'type': get_type(get_value(filepath, ['chirp_mass']))
                    },
                    'dec': {'type': get_type(get_value(filepath, ['zenith']))},
                    'luminosity distance': {
                        'alpha': int(float(get_string_value(get_value(filepath, ['luminosity_distance']), 'alpha'))),
                        'maximum': int(float(get_string_value(get_value(filepath, ['luminosity_distance']), 'maximum'))),
                        'minimum': int(float(get_string_value(get_value(filepath, ['luminosity_distance']), 'minimum'))),
                        'type': get_type(get_value(filepath, ['luminosity_distance']))
                    },
                    'mass 1': {
                        'maximum': int(float(float(get_string_value(get_value(filepath, ['mass_1']), 'maximum')))), 
                        'minimum': int(float(float(get_string_value(get_value(filepath, ['mass_1']), 'minimum')))), 
                        'type': 'Constraint'},
                    'mass 2': {
                        'maximum': int(float(get_string_value(get_value(filepath, ['mass_2']), 'maximum'))),
                        'minimum': int(float(get_string_value(get_value(filepath, ['mass_2']), 'minimum'))), 
                        'type': get_type(get_value(filepath, ['mass_2']))},
                    'mass ratio': {
                        'maximum': float(get_string_value(get_value(filepath, ['mass_ratio']), 'maximum')),
                        'minimum': float(get_string_value(get_value(filepath, ['mass_ratio']), 'minimum')),
                        'type': get_type(get_value(filepath, ['mass_ratio']))
                    },
                    'phase': {'boundary': get_string_value(get_value(filepath, ['phase']), 'boundary')[1:-1], 
                              'type': get_type(get_value(filepath, ['phase']))},
                    'phi 12': {'type': get_type(get_value(filepath, ['phi_12']))},
                    'phi jl': {'type': get_type(get_value(filepath, ['phi_jl']))},
                    'psi': {'type': get_type(get_value(filepath, ['psi']))},
                    'ra': {'type': get_type(get_value(filepath, ['azimuth']))}, 
                    'spin 1': {'maximum': 1, 'minimum': 0, 'type': 'Uniform'}, # NOT FOUND
                    'spin 2': {'maximum': 1, 'minimum': 0, 'type': 'Uniform'}, # NOT FOUND
                    'theta jn': {'type': get_type(get_value(filepath, ['theta_jn']))},
                    'tilt 1': {'type': get_type(get_value(filepath, ['tilt_1']))},
                    'tilt 2': {'type': get_type(get_value(filepath, ['tilt_2']))}
                }
            }
        ]

        # Save dictionary to a YAML file
        with open(f'test_yamls/IMRPhenomPv2/{event}/production_pe_priors.yaml', 'w') as yaml_file:
            yaml.dump_all(production_pe_priors_dict, 
                          yaml_file,
                          default_flow_style=False, 
                          sort_keys=False,
                          indent=2)
        print('Created IMRPhenomPv2 production_pe_priors.yaml')
        
####################################################################################

        testing_pe_osg_dict = [
            {
                'kind': 'configuration',
                'pipelines': {
                      'bayeswave':{
                          'quality':
                          {
                            'state vector':string_dict_to_dict(get_value(filepath, ['channel-dict', 'channel_dict']))
                          },
                        'likelihood':
                          {'iterations': 100000,
                          'chains': 20,
                          'threads': 4},
                        'scheduler':
                          {'copy frames': True,
                          'accounting group': 'ligo.dev.o4.cbc.pe.rift',
                          'request memory': 1024,
                          'request disk': 3000000,
                          'request post memory': 16384,
                          'osg': True}
                      },
                    
                    'rift': {
                        'scheduler': {
                            'osg': True,
                            'accounting group': 'ligo.dev.o4.cbc.pe.rift',
                            'request memory': 1000000,
                            'request disk': '1G',
                            'singularity image': '/cvmfs/singularity.opensciencegrid.org/james-clark/research-projects-rit/rift:test',
                            'singularity base exe directory': '/usr/local/bin/',
                            'gpu architectures': ['Tesla K10.G1.8GB', 'Tesla K10.G2.8GB'],
                            'avoid hosts': [
                                'qa-rtx6k-030.crc.nd.edu',
                                'qa-rtx6k-029.crc.nd.edu',
                                'qa-rtx6k-026.crc.nd.edu',
                                'qa-rtx6k-036.crc.nd.edu',
                                'qa-rtx6k-020.crc.nd.edu',
                                'node504.cluster.ldas.cit',
                                'node540.cluster.ldas.cit',
                                'node512.cluster.ldas.cit',
                                'node2231.cluster.ldas.cit',
                                'node2236.cluster.ldas.cit',
                                'node2237.cluster.ldas.cit',
                                'qa-v100-010.crc.nd.edu',
                                'deepclean.ldas.cit',
                                'e1002.chtc.wisc.edu',
                                'wn-a10-01.gina.surfsara.nl',
                                'wn-a10-03.gina.surfsara.nl',
                                'wn-a10-04.gina.surfsara.nl',
                                'wn-a10-02.gina.surfsara.nl',
                            ]
                        },
                        'sampler': {
                            'cip': {
                                'fitting method': 'rf', 
                                'sampling method': 'AV', 
                                'explode jobs auto': True 
                            },
                            'ile': {
                                'n eff': 1000 if str(get_value(filepath, ['neff','n-effective','n_effective', 'neffsamples']) or 1000).lower() == 'inf' 
                                else int(get_value(filepath, ['neff','n-effective','n_effective', 'neffsamples']) or 1000),
                                'sampling method': 'AV',
                                'jobs per worker': 50, 
                                'request disk': '1G'
                            },
                        }
                    }
                },
                'postprocessing': {
                    'pesummary': {
                        'accounting group': 'ligo.dev.o4.cbc.pe.rift',
                        'cosmology': get_value(filepath, ['cosmology']),
                        'multiprocess': 4, # multiprocessing: N/A
                        'redshift': 'exact',
                        'regenerate posteriors': [
                            'redshift',
                            'mass_1_source',
                            'mass_2_source',
                            'chirp_mass_source',
                            'total_mass_source',
                            'final_mass_source',
                            'final_mass_source_non_evolved',
                            'radiated_energy'
                        ],
                        'skymap samples': 2000 # NOT FOUND
                    }
                }
            }
        ]
        testing_pe_osg_dict = remove_none_values(testing_pe_osg_dict)
        # Save dictionary to a YAML file
        with open(f'test_yamls/IMRPhenomPv2/{event}/testing_pe_osg.yaml', 'w') as yaml_file:
            yaml.dump_all(testing_pe_osg_dict, 
                          yaml_file,
                          default_flow_style=False, 
                          sort_keys=False,
                          indent=2)
        print('Created IMRPhenomPv2 testing_pe_osg.yaml')



###########################################################################

###### SEOBNRv4PHM ############ SEOBNRv4PHM ############ SEOBNRv4PHM ######

###########################################################################


################
# Define Event #
################

        # Creates a directory for event
        os.makedirs(f"test_yamls/SEOBNRv4PHM/{event}", exist_ok=True)

        ###############
        # Get Configs #
        ###############        

        with h5py.File(filepath, "r") as file:
            
################################################################################ 

            sample_rift_dict2[0]['name'] = 'rift-SEOBNRv4PHM'
            sample_rift_dict2[0]['waveform']['approximant'] = 'SEOBNRv4PHM'
            sample_rift_dict2[0]['likelihood']['psd maximum duration'] = int(get_value(filepath, ['psd_maximum_duration', 'psd-maximum-duration', 'max-psd-length']))
            try: del sample_rift_dict2[0]['likelihood']['psd fractional overlap']
            except: continue
            try: del sample_rift_dict2[0]['likelihood']['psd length']
            except: continue
            try: del sample_rift_dict2[0]['likelihood']['psd method']
            except: continue

            combined_dicts = sample_rift_dict1 + sample_rift_dict2 

            # Save dictionary to a YAML file
            with open(f'test_yamls/SEOBNRv4PHM/{event}/sample_rift.yaml', 'w') as yaml_file:
                yaml.dump_all(combined_dicts, 
                              yaml_file,
                              default_flow_style=False, 
                              sort_keys=False,
                              indent=4)
            print('Created SEOBNRv4PHM sample_rift.yaml')
        

    
################################################################################

        # Priors are the same as the IMRPhenomXPHM analysis
        # Save dictionary to a YAML file
        with open(f'test_yamls/SEOBNRv4PHM/{event}/production_pe_priors.yaml', 'w') as yaml_file:
            yaml.dump_all(production_pe_priors_dict, 
                          yaml_file,
                          default_flow_style=False, 
                          sort_keys=False,
                          indent=2)
        print('Created SEOBNRv4PHM production_pe_priors.yaml')
            
################################################################################

        testing_pe_osg_dict[0]['pipelines']['bayeswave']['quality']['state vector'] = string_dict_to_dict(get_value(filepath, ['channels', 'channel_dict', 'channel-dict']))
        testing_pe_osg_dict[0]['pipelines']['rift']['sampler']['ile']['n eff'] = 1000 if str(get_value(filepath, ['neff','n-effective','n_effective', 'neffsamples']) or 1000).lower() == 'inf' \
        else int(get_value(filepath, ['neff','n-effective','n_effective', 'neffsamples']) or 1000)
        testing_pe_osg_dict[0]['pipelines']['rift']['sampler']['ile']['sampling method'] = 'lal'

        # Osg test_yamls are the same as the IMRPhenomXPHM analysis
        # Save dictionary to a YAML file
        with open(f'test_yamls/SEOBNRv4PHM/{event}/testing_pe_osg.yaml', 'w') as yaml_file:
            yaml.dump_all(testing_pe_osg_dict, 
                          yaml_file,
                          default_flow_style=False, 
                          sort_keys=False,
                          indent=4)
        print('Created SEOBNRv4PHM testing_pe_osg.yaml')
  


###########################################################################

###### SEOBNRv5PHM ############ SEOBNRv5PHM ############ SEOBNRv5PHM ######

###########################################################################
            
        os.makedirs(f"test_yamls/SEOBNRv5PHM/{event}", exist_ok=True)
#         print(f"Event {event} for SEOBNRv5PHM")
        
        combined_dicts[1]['waveform']['approximant']='SEOBNRv5PHM'
        combined_dicts[1]['likelihood']['assume']   = "precessing"
        with open(f'test_yamls/SEOBNRv5PHM/{event}/sample_rift.yaml', 'w') as yaml_file:
            yaml.dump_all(combined_dicts, 
                          yaml_file,
                          default_flow_style=False, 
                          sort_keys=False,
                          indent=4)
        print('Created SEOBNRv5PHM sample_rift.yaml')

        with open(f'test_yamls/SEOBNRv5PHM/{event}/production_pe_priors.yaml', 'w') as yaml_file:
            yaml.dump_all(production_pe_priors_dict, 
                          yaml_file,
                          default_flow_style=False, 
                          sort_keys=False,
                          indent=2)
        print('Created SEOBNRv5PHM production_pe_priors.yaml')


        testing_pe_osg_dict[0]['pipelines']['rift']['sampler']['ile']['manual extra args']=['--use-gwsignal']
        with open(f'test_yamls/SEOBNRv5PHM/{event}/testing_pe_osg.yaml', 'w') as yaml_file:
            yaml.dump_all(testing_pe_osg_dict, 
                          yaml_file,
                          default_flow_style=False, 
                          sort_keys=False,
                          indent=4)   
        print('Created SEOBNRv5PHM testing_pe_osg.yaml')
            
         


###########################################################################

######## NRSur7dq4 ############# NRSur7dq4 ############# NRSur7dq4 ########

###########################################################################

folder = 'downloaded_files/'
for filename in os.listdir(folder):
    if filename.endswith('_NRSur7dq4.h5'):
        f = os.path.join(folder, filename)
        event    = filename[:15]
        os.makedirs(f"test_yamls/NRSur7dq4/{event}", exist_ok=True)


        ###################
        # Getting Configs #
        ###################
        h5_data_dict = {}

        with h5py.File(f, "r") as file:
#             print(f"Event {event}")           # TROUBLESHOOTING
            group = file["Bilby:NRSur7dq4"]["meta_data"]["other"]["config_file"]
            h5_data_dict = convert_to_dict_NRSur(group)
            
            config_dict = {key: value for key, value in h5_data_dict.items() if value is not None}
            del config_dict['prior_dict']

####################################################################################

            #####################
            # Create YAML Files #
            #####################
            
            sample_rift_dict2 = [
                   {'kind': 'analysis',
                    'name': 'rift-NRSur7dq4',
                    'status': 'Ready',
                    'pipeline': 'RIFT',
                    'event': event,
                    'priors': {
                        'mass ratio':{
                            'minimum': 0.16666667,
                            'maximum': 1
                        }
                    },
                    'waveform': {
                        'approximant': 'NRSur7dq4'
                    },
                    'comment': 'This is a sample RIFT analysis',
                    'likelihood': {
                        'start frequency': 10,
                        'psd fractional overlap': float(config_dict['psd_fractional_overlap']),
                        'psd length': int(config_dict['psd_length']),
                        'psd maximum duration': int(config_dict['psd_maximum_duration']),
                        'psd method': config_dict['psd_method'],
                        'reference frequency': 10
                    },
                    'scheduler': {
                        'osg': True,
                        'additional files': ['/home/pe.o4/lalsuite-extra/data/lalsimulation/NRSur7dq4.h5'],
                        'pipeline': {
                            'manual-extra-ile-args': "--force-adapt-all"
                        }
                    }
                }
            ]

            combined_dicts = sample_rift_dict2

            # Save dictionary to a YAML file
            with open(f'test_yamls/NRSur7dq4/{event}/sample_rift.yaml', 'w') as yaml_file:
                yaml.dump_all(combined_dicts, 
                              yaml_file,
                              default_flow_style=False, 
                              sort_keys=False,
                              indent=2)
            print('Created NRSur7dq4 testing_pe_osg.yaml')

####################################################################################

        #################
        # Getting Priors#
        #################
        prior_dict = {}
        prior_dict_string = h5_data_dict['prior_dict']
        prior_dict_string = prior_dict_string.replace(":", "=").replace(" ", "").replace('-', ' ')
        prior_dict_string = prior_dict_string.replace('_', ' ').replace("{","").replace("}","").replace("2*np.pi",'6.2831853')

        # Convert prior_dict keys and values to a YAML-compatible format
        entries = re.split(r'\),', prior_dict_string)

        for entry in entries:
            # Splitting each entry at the first '='
            key, value = entry.split('=', 1)
            # Splitting the value at the first '('
            type_str, rest = value.split('(', 1)
            # Prepending "type=" to the type string
            type_str_with_type = "type: " + type_str.strip()
            # Removing the substring starting with "name" and ending with the next ","
            cleaned_rest = re.sub(r"name='[^']*',", "", rest)
            cleaned_rest = cleaned_rest.replace(')', '').replace('=', ': ').replace('\'', '')
            # Splitting the cleaned rest at commas to turn into a list
            value_list = cleaned_rest.split(',')
            # Constructing the new value as a list
            new_value = [type_str_with_type] + value_list
            # Splitting each item in the value list at the ":" character to create a dictionary
            value_dict = {item.split(":")[0].strip(): item.split(":")[1].strip() for item in new_value}
            # Converting numbered values with decimal places to floats, integer numbers to ints,
            # and evaluating anything that says "2*np.pi" and converting it to float
            for k, v in value_dict.items():
                if '.' in v:
                    try:
                        value_dict[k] = float(v)
                    except ValueError:
                        pass
                elif v.isdigit():
                    value_dict[k] = int(v)
            # Adding key-value pair to the dictionary
            prior_dict[key.strip()] = value_dict
        
        prior_dict["psi"]["maximum"]=6.2831853
        prior_dict['spin 1'] = prior_dict.pop('a 1')
        prior_dict['spin 2'] = prior_dict.pop('a 2')
        yaml_dict = {"kind": "configuration",
                     "priors": prior_dict}
                      

        # Write YAML data to file
        with open(f"test_yamls/NRSur7dq4/{event}/production_pe_priors.yaml", "w") as yaml_file:
            yaml.dump(yaml_dict, 
                      yaml_file, 
                      default_flow_style=False,
                      indent=4)
        print('Created NRSur7dq4 production_pe_priors.yaml')    
            
####################################################################################
        
        testing_pe_osg_dict[0]['pipelines']['bayeswave']['quality']['state vector']=config_dict['channel_dict']

        # Save dictionary to a YAML file
        with open(f'test_yamls/NRSur7dq4/{event}/testing_pe_osg.yaml', 'w') as yaml_file:
            yaml.dump_all(testing_pe_osg_dict, 
                          yaml_file,
                          default_flow_style=False, 
                          sort_keys=False,
                          indent=2)
        print('Created NRSur7dq4 testing_pe_osg.yaml')
        

