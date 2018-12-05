from tempfile import mkdtemp
from shutil import rmtree
from core import dataset_path, csv_path, log_path
from model.preprocessing import Formatter
from model.preprocessing import Extractor
from model.detection import Detector
from model import gatherer, tools
from view import evaluation_metrics


print("training the model")

result_name = "test_result.csv"

ex = Extractor()
dt = Detector()

path, files = tools.directory_content(csv_path)

flows = gatherer.open_csv(path, files)[0]

ft = Formatter(flows)
header, flows = ft.format_flows(training_model=True)

header_features, features = ex.extract_features(header,
                                                flows,
                                                list(range(10, 15)))

tools.save_choices_log(header_features[0], log_path)

labels = ex.extract_labels(flows)

dataset = ex.train_test_split(features, labels, 0.3)

ex.choose_preprocessing(0)

num_clf = dt.choose_classifiers(list(range(0, 11)))

tools.save_choices_log(dt.methods, log_path)
tools.save_choices_log([ex.methods], log_path)

temp_dir = mkdtemp()
for idx in range(num_clf):
    dt.tuning_hyperparameters(5, idx, ex.preprocessing, temp_dir)

    param, train_date, train_dur = dt.training_classifiers(
        dataset[0], dataset[2], idx)

    pred, test_date, test_dur = dt.execute_classifiers(
        dataset[1], idx)

    evaluation_metrics(dataset[3], param, pred,
                       [train_date, test_date, train_dur,
                        test_dur, dt.methods[idx]],
                       dataset_path + result_name, idx)

rmtree(temp_dir)


print("model finished", end="\n\n")