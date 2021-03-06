"""Parameter Sensitivity Analysis for Contact Tracing Model
Sample pairs of (parameters, output summary) must be generated by param_samples.py in advance.

Usage:
  analyse_sensitivity.py <INPUT_DIR> <OUTPUT_DIR> [--seed=<seed>]
  analyse_sensitivity.py (-h | --help)
  analyse_sensitivity.py --version

Options:
  -h --help                       Show this screen.
  --version                       Show version.
  --seed=<seed>                   Random seed [default: 1234].
  
"""

import numpy as np
import pandas as pd
import os
from docopt import docopt
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
import shap
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

if __name__ == '__main__':
    args = docopt(__doc__, version='0.0.1')
    
    def _getopt(key, default):
        return args[key] if key in args and args[key] is not None else default

    indir = _getopt('<INPUT_DIR>', None)
    outdir = _getopt('<OUTPUT_DIR>', None)
    seed = int(_getopt('--seed', 1234))

    X = pd.read_csv('{}/input_parameter_samples.csv'.format(indir))
    Y = pd.read_csv('{}/output_loss_samples.csv'.format(indir))
    X = X.set_index(X.columns[0])
    Y = Y.set_index(Y.columns[0])
    
    n = X.shape[0]
    
    ms_list = np.unique(np.round(np.logspace(np.log10(2.0), np.log10(np.min([1000, n / 2])), 10)).astype(int))

    try:
        os.mkdir(outdir)
    except:
        pass

    imp = []
    for metric in Y.columns:
        # Step 1. Fitting a non-linear extra-trees regressor with out-of-bag model selection
        X_train, X_test, y_train, y_test = train_test_split(X, Y[metric], test_size=0.5, random_state=1234)
        
        model = GridSearchCV(
            estimator=ExtraTreesRegressor(
                n_estimators=100,
                criterion='mse',
                max_depth=None,
                bootstrap=True,
                oob_score=True,
                random_state=seed),
            param_grid={
                'min_samples_split': ms_list,
                'max_features': [int(1), 0.33, 1.0]
                },
            scoring='r2'
            # scoring='neg_mean_squared_error'
        ).fit(X_train, y_train)
       
        # This is a biased but useful importance estimate.
        fimp = model.best_estimator_.feature_importances_
        fimp /= fimp.sum()
        imp.append(fimp.reshape(-1, 1))
    
        explainer = shap.TreeExplainer(model.best_estimator_)
        shap_values = explainer.shap_values(X)
        
        with PdfPages('{}/{}.pdf'.format(outdir, metric)) as pdf:
            plt.figure(figsize=(6, 6))
            plt.scatter(model.predict(X_test), y_test)
            plt.title('{}: Forecast of Meta Model vs Actual Target by Simulator'.format(metric))
            plt.xlabel('Forecast')
            plt.ylabel('Actual')
            pdf.savefig()
            plt.close()

            plt.figure(figsize=(6, 12))
            shap.summary_plot(shap_values, X, show=False)
            plt.title('Datapoint-specific sensitivities to {}'.format(metric))
            pdf.savefig()
            plt.close()

            for xcol in X.columns:
                plt.figure(figsize=(6, 6))
                shap.dependence_plot(xcol, shap_values, X, show=False)
                plt.title('How interaction with {} affects {}'.format(xcol, metric))
                pdf.savefig()
                plt.close()
        
    imp = pd.DataFrame(
        data=np.hstack(tuple(imp)),
        index=X.columns,
        columns=Y.columns
        )

    imp.to_csv('{}/relative_importance.csv'.format(outdir))
        
