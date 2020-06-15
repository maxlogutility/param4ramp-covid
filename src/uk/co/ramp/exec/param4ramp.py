"""Parameter Sensitivity Analysis for Contact Tracing Model.

Usage:
  param4ramp.py <OUTPUT_DIR> [--n-simulations=<n_sim>] [--seed=<seed>] [--java-project-dir=<JPDIR>] [--input-locations-file=<ILFILE>] [--output-summary-file=<OSFILE>] [--tmp-dir=<TMPDIR>]
  param4ramp.py (-h | --help)
  param4ramp.py --version

Options:
  -h --help                       Show this screen.
  --version                       Show version.
  --n-simulations=<n_sim>         Number of parameter samples generated [default: 1000].
  --seed=<seed>                   Random seed [default: 1234].
  --java-project-dir=<JPDIR>      Project directory of Contact Tracing Model Java codes
  --input-locations-file=<ILFILE> JSON file of storing input filenames at java-project-dir [default: input/inputLocations.json]
  --output-summary-file=<OSFILE>  CSV file that stores a summary of one simulation [default: Compartments.csv]
  --tmp-dir=<TMPDIR>               Temporary directory in which temporary settings files are generated
  
"""

import json
import os
import numpy as np
import pandas as pd
from os.path import expanduser
from docopt import docopt
from uk.co.ramp.gencfg.disease import DiseaseSettings
from uk.co.ramp.gencfg.population import PopulationSettings

if __name__ == '__main__':
    args = docopt(__doc__, version='0.0.1')
    
    def _getopt(key, default):
        return args[key] if key in args and args[key] is not None else default

    java_project_dir = _getopt('--java-project-dir', expanduser('~/git/Contact-Tracing-Model'))
    input_loc_file = _getopt('--input-locations-file', 'input/inputLocations.json')
    output_summary_file = _getopt('--output-summary-file', 'Compartments.csv')
    
    tmp_indir = _getopt('--tmp-dir', expanduser('~/tmp/covid-19'))
    n_simulations = int(_getopt('--n-simulations', 1000))
    seed = int(_getopt('--seed', 1234))
    outdir = _getopt('<OUTPUT_DIR>', None)
    
    try:
        os.mkdir(tmp_indir)
    except:
        pass
    os.chdir(java_project_dir)
    
    disease = DiseaseSettings(random_state=seed)
    population = PopulationSettings(random_state=seed)
    
    X_columns = []
    X = []
    for trial in range(n_simulations):
        X_t = []
    
        # Generate a run Settings File: deterministic at the moment
        run_file = '{}/runSettings.{:03d}.json'.format(tmp_indir, trial)
        run_sample = {
            "populationSize": 10000,
            "timeLimit": 200,
            "initialExposures": 1000,
            "seed": trial,
            "steadyState": True
        }
        with open(run_file, 'w') as fout:
            json.dump(run_sample, fout)
    
        # Generate a Population Settings File
        population_file = '{}/populationSettings.{:03d}.json'.format(tmp_indir, trial)
        population_sample = population.next()
        if trial == 0:
            for key in population_sample.keys():
                X_columns.append(key)
        X_t.append(list(population_sample.values()))
        with open(population_file, 'w') as fout:
            json.dump(PopulationSettings.export(population_sample), fout)
        
        # Generate a Disease Settings File
        disease_file = '{}/diseaseSettings.{:03d}.json'.format(tmp_indir, trial)
        disease_sample = disease.next()
        if trial == 0:
            for key in disease_sample.keys():
                X_columns.append(key)
        X_t.append(list(disease_sample.values()))
        with open(disease_file, 'w') as fout:
            json.dump(DiseaseSettings.export(disease_sample), fout)
            
        # Currently using project sample file, but later we will add purturbation
        # because contact data are always imperfect samples
        contact_file = '{}/input/homogeneous_contacts.csv'.format(java_project_dir)
        initexp_file = '{}/input/initialExposures.csv'.format(java_project_dir)
            
        input_locations = {
          'runSettings': run_file,
          'populationSettings': population_file,
          'diseaseSettings': disease_file,
          'contactData': contact_file,
          'initialExposures': initexp_file
        }
        
        with open(input_loc_file, 'w') as fout:
            json.dump(input_locations, fout)
            
        os.system('gradle run')
        
        X.append(np.concatenate(X_t).reshape(1, -1))
    
        # Read the summary results file and calculate the summary statistic
        Y = pd.read_csv('{}/{}'.format(java_project_dir, output_summary_file)).set_index('time')
        print(Y)
        
    
    X = pd.DataFrame(
        data=np.vstack(tuple(X)),
        index=np.arange(n_simulations),
        columns=X_columns
        )
    
    try:
        os.mkdir(outdir)
    except:
        pass
    
    X.to_csv('{}/parameter_samples.csv'.format(outdir))
