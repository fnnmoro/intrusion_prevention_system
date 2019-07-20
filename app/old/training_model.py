from shutil import rmtree
from tempfile import mkdtemp
from sklearn.model_selection import train_test_split
from core.paths import paths
from model.detection import Detector
from model.gatherer import open_csv
from model.preprocess import Extractor
from model.preprocess import Formatter
from model.preprocess import Preprocessor
from model.tools import evaluation_metrics, export_results_csv
from model.walker import DirectoryContents


print('training classifier', end=f'\n{"-" * 10}\n')

result_name = 'test'

dir_cont = DirectoryContents(f'{paths["csv"]}datasets/')
path, file = dir_cont.choose_files()

if not file:
    raise IndexError('error: empty file')

print(end=f'{"-" * 10}\n')

header, flows = open_csv(path, file[0])

# old dataset
tmp = list()
for flow in flows:
    new.append(flow[0:2]+flow[4:])
flows = tmp

for entry in flows:
    Formatter.convert_features(entry, True)

ex = Extractor(3, [0, 1, 2, 3, 4])

pre_method = 'normal'
preprocess = Preprocessor.methods[pre_method]

features, labels = ex.extract_features(flows)

dataset = train_test_split(features, labels,
                           test_size=0.3,
                           random_state=13,
                           stratify=labels)

dt = Detector()
tmp_dir = mkdtemp()

for clf in ['decision tree', 'k-nearest neighbors']:
    dt.tuning_hyperparameters(clf, preprocess, 5, tmp_dir)

    param, train_date, train_dur = dt.train_classifier(clf,
                                                       dataset[0],
                                                       dataset[2])

    pred, test_date, test_dur = dt.execute_classifier(clf, dataset[1])

    results = [clf, train_date, test_date, train_dur, test_dur]
    results.extend(evaluation_metrics(dataset[3], pred))
    results.extend([pre_method, param])

    text = ['classifier', 'train date', 'test date',
            'train duration', 'test duration',
            'accuracy', 'precision', 'recall', 'f1-score',
            'tue negative', 'false positive',
            'false negative', 'true positive',
            'preprocess', 'hyperparameters']

    export_results_csv(results, text,
                       paths['csv'], 'result.csv')

rmtree(tmp_dir)

print('trained classifier', end=f'\n{"-" * 10}\n')
