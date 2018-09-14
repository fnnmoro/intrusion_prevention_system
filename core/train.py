from flask import Blueprint, render_template, request, redirect, url_for
from model import gatherer, tools
from model.preprocessing import Formatter, Extractor
from model.detection import Detector

bp = Blueprint('train', __name__, url_prefix='/train')

@bp.route('/config')
def config():
    algorithms = ['decision tree',
                  'random forest',
                  'bernoulli naive bayes',
                  'gaussian naive bayes',
                  'multinomial naive bayes',
                  'k-nearest neighbors',
                  'support vector machine',
                  'stochastic gradient descent',
                  'passive aggressive',
                  'perceptron',
                  'multi-layer perceptron']

    return render_template('train/config.html', algorithms=algorithms)

@bp.route('/training', methods=('POST'))
def training():
    if request.method == 'POST':
        print('noooo')
        path = '/home/flmoro/research_project/dataset/csv/'
        file = 'flows_w60_s800.csv'

        flows = gatherer.open_csv(path, file, -1, True)[0]

        ft = Formatter(flows)
        header, flows = ft.format_flows(True)

        ex = Extractor(header, flows)
        features = ex.extract_features(10, 12)[1]
        labels = ex.extract_labels()

        # features = ex.preprocessing_features(features)

        kf = ex.k_fold(2, True)

        dataset = ex.train_test_split(features, labels)

        dt = Detector()

        param = dt.define_parameters()
        dt.tuning_hyperparameters(param, kf)
    
        pred, param, dates, durations = dt.execute_classifiers(
            dataset[0], dataset[1], dataset[2], request.form['algorithms'])
    
        """for idx in range(len(pred)):
            evaluation_metrics(dataset[3], pred[idx], param[idx],
                               [dates[idx], methods_names[idx],
                                durations[idx]],
                               dataset_path + result_name, idx)"""
        #return redirect(url_for('home'))

    return redirect(url_for('home'))
