# param4ramp-covid

Sensitivty analysis for Contact Tracing Model in RAMP COVID-19 Project.

Randomly generate samples of model parameters, and perform
regression between the input parameters and output time-series of SEIR.

# Requirement

numpy, scipy, pandas, scikit-learn, docopt, shap, matplotlib

# Usage

`uk.co.ramp.exec.draw_parameters` is a command-line program to
generate samples of model parameters and corresponding model output time-series.
These samples should be fed into `uk.co.ramp.exec.analyse_sensitivity`
to understand which parameter strongly affects which aspect of the output time-series.

Simply executing each script provides a list of command-line options.

```
python draw_parameters.py 
python analyse_sensitivity.py 
```

# Example

Below you get `${HOME}/covid-19/resultrelative_importance.biased.csv`
and `${HOME}/covid-19/resultrelative_importance.unbiased.csv` as the final results.
These CSV files contain which parameter strongly affects the total number of severe infections and that of deaths
over the entire simulation period. In the future the metrics we focus on can be customisable.

```
python draw_parameters.py ~/covid-19/result --n-simulations=1000 \
  --java-project-dir=~/git/Contact-Tracing-Model \
  --tmp-dir=~/covid-19/tmp
  
python analyse_sensitivity.py ~/covid-19/result ~/covid-19/result
 
```





```


