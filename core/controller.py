import os
from model import Gatherer
from model import Formatter
from model import Modifier
from model import Extractor
from model import Detector
from view import print_flows, export_flows, evaluation_metrics, scatter_plot

print("anomaly detector")
print("1 - build the dataset")
print("2 - train the model")
print("3 - run the model")
print("4 - stop", end="\n\n")

option = int(input("choose an option: "))
print()

dataset_path = "/home/flmoro/research_project/dataset/"
pcap_path = "/home/flmoro/research_project/dataset/pcap/"
nfcapd_path = "/home/flmoro/research_project/dataset/nfcapd/"
csv_path = "/home/flmoro/research_project/dataset/csv/"
file_name = ["", "", ""]
ml_models = []

while option != 4:

    if option == 1:

        print("building the dataset", end="\n\n")
        print("1 - split pcap")
        print("2 - convert pcap to nfcapd")
        print("3 - convert nfcapd to flows")
        print("4 - format and modify the flows")
        print("5 - clean nfcapd files")
        print("6 - merge flows files")
        print("7 - back to main", end="\n\n")

        option = int(input("choose an option: "))
        print()

        gt = Gatherer(pcap_path, nfcapd_path, csv_path)
        while option != 7:
            if option == 1:
                print("splitting file", end="\n\n")
                gt.split_pcap(int(input("split size: ")))
                print("split file", end="\n\n")

            elif option == 2:
                print("converting pcap to nfcapd", end="\n\n")
                wtime = input("window time: ")
                file_name[0] = wtime

                gt.convert_pcap_nfcapd(int(wtime))
                print("converted pcap files", end="\n\n")

            elif option == 3:
                print("converting nfcapd to flows")
                file_name[2] = gt.convert_nfcapd_csv()
                print("converted nfcapd files", end="\n\n")

            elif option == 4:
                print("opening, format and modify the file", end="\n\n")
                sample = input("csv sample: ")
                file_name[1] = sample

                flows = gt.open_csv(sample=int(sample))

                ft = Formatter(flows)
                header, flows = ft.format_flows()

                md = Modifier(flows, header)
                header, flows = md.modify_flows()
                print_flows(flows, header, 5)
                export_flows(flows, csv_path + "flows/", "flows_w" + file_name[0] + "_s" + file_name[1] + "_"
                             + file_name[2], header)

                print("completed file", end="\n\n")
            elif option == 5:
                print("cleaning nfcapd files", end="\n\n")
                gt.clean_nfcapd_files()
                print("completed cleaning", end="\n\n")
            elif option == 6:
                print("merging flows", end="\n\n")
                dataset_name = input("dataset name: ") + ".csv"
                print()

                flows = gt.open_csv()

                if not os.path.exists(csv_path + dataset_name):
                    export_flows([flows[0]], csv_path, dataset_name, mode='a')
                export_flows(flows[1:], csv_path, dataset_name, mode='a')

                print("merged flows", end="\n\n")
            elif option == 7:
                exit()
            else:
                print("Invalid option")

            print("building the dataset", end="\n\n")
            print("1 - split pcap")
            print("2 - convert pcap to nfcapd")
            print("3 - convert nfcapd to flows")
            print("4 - format and modify the flows")
            print("5 - clean nfcapd files")
            print("6 - merge flows files")
            print("7 - back to main", end="\n\n")

            option = int(input("choose an option: "))
            print()

        print("dataset built", end="\n\n")

    elif option == 2:
        try:
            print("training the model")

            gt = Gatherer(csv_path=csv_path)
            flows = gt.open_csv()

            ft = Formatter(flows)
            flows = ft.format_flows(train_model=True)[1]

            dt = Detector()

            ex = Extractor(flows)
            features = ex.extract_features()
            #features = ex.preprocessing_features(features)
            labels = ex.extract_labels()

            print("1 - visualize the dataset patterns")
            print("2 - execute the machine learning algorithms")
            print("3 - back to main", end="\n\n")

            option = int(input("choose an option: "))
            print()

            while option != 3:
                if option == 1:
                    scatter_plot(features, labels, 0, 1, "td", "ipkt", "time duration x input packets")
                    scatter_plot(features, labels, 0, 5, "td", "pps", "time duration x packets per second")
                    scatter_plot(features, labels, 0, 2, "td", "ibyt", "time duration x input bytes")
                    scatter_plot(features, labels, 0, 3, "td", "bps", "time duration x bits per second")
                    scatter_plot(features, labels, 1, 2, "ipkt", "ibyt", "input packets x input bytes")
                    scatter_plot(features, labels, 5, 3, "pps", "bps", "packets per second x bits per second")
                    scatter_plot(features, labels, 1, 5, "ipkt", "pps", "input packets x packets per second")
                    scatter_plot(features, labels, 2, 3, "ibyt", "bps", "input packets x bits per second")

                    pattern = dt.find_patterns(features)
                    scatter_plot(pattern, labels, 0, 1, 'x', 'y', "principal component analysis (pca)")

                elif option == 2:
                    methods = ["decision tree", "bernoulli naive bayes", "gaussian naive bayes",
                               "multinomial naive bayes", "k-nearest neighbors", "support vector machine",
                               "stochastic gradient descent", "passive aggressive", "perceptron",
                               "multi-layer perceptron", "online bernoulli naive bayes", "online gaussian naive bayes",
                               "online multinomial naive bayes", "online stochastic gradient descent",
                               "online passive aggressive", "online perceptron", "online multi-layer perceptron"]

                    dataset = ex.k_fold(int(input("split data in: ")), True, features, labels)
                    print()

                    param = dt.define_parameters()
                    dt.create_classifiers(param)

                    num = 1
                    for training_features, test_features, training_labels, test_labels in dataset:
                        pred, param = dt.execute_classifiers(training_features, test_features, training_labels)

                        for i in range(len(pred)):
                            evaluation_metrics(pred[i], test_labels, param[i], methods[i], num, dataset_path,
                                               "results_flows_w60_s60398.txt")

                        num += 1

                    ml_models.extend(dt.get_ma_models())
                elif option == 3:
                    exit()
                else:
                    print("Invalid option")

                print("1 - view the dataset patterns")
                print("2 - execute the machine learning algorithms")
                print("3 - back to main", end="\n\n")

                option = int(input("choose an option: "))
                print()
        except ValueError as error:
            print(error, end="\n\n")

        print("model finished", end="\n\n")

    elif option == 3:
        pass

    elif option == 4:
        exit()
    else:
        print("Invalid option")

    print("anomaly detector")
    print("1 - build the dataset")
    print("2 - train the model")
    print("3 - run the model")
    print("4 - stop", end="\n\n")

    option = int(input("choose an option: "))
    print()