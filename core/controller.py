import time
from model import gatherer, tools
from model.preprocessing import Formatter
from model.preprocessing import Modifier
from model.preprocessing import Extractor
from model.detection import Detector
from view import export_flows, evaluation_metrics, scatter_plot


dataset_path = "/home/flmoro/research_project/dataset/"
pcap_path = "/home/flmoro/research_project/dataset/pcap/"
nfcapd_path = "/home/flmoro/research_project/dataset/nfcapd/"
csv_path = "/home/flmoro/research_project/dataset/csv/"

result_name = "test_result3.csv"

print("anomaly detector")
option = tools.menu(["build the dataset",
                     "train the model",
                     "execute the model",
                     "stop"])
print()

tools.check_path_exist(pcap_path, nfcapd_path, csv_path)

dt = Detector()

while option != 4:

    if option == 1:
        print("building the dataset", end="\n\n")

        option = tools.menu(["split pcap",
                             "convert pcap to nfcapd",
                             "convert nfcapd to flows",
                             "format and modify the flows",
                             "merge flows files",
                             "clean nfcapd files",
                             "back to main"])
        print()

        while option != 7:
            if option == 1:
                print("splitting file", end="\n\n")

                # gets the path and the list of files
                path, files = tools.directory_content(pcap_path)

                gatherer.split_pcap(path, files, int(input("split size: ")))

                print("split file", end="\n\n")

            elif option == 2:
                print("converting pcap to nfcapd", end="\n\n")

                # gets the path and the list of files
                path, files = tools.directory_content(pcap_path)

                gatherer.convert_pcap_nfcapd(path, files, nfcapd_path)

                print("converted pcap files", end="\n\n")

            elif option == 3:
                print("converting nfcapd to flows")

                path, files = tools.directory_content(nfcapd_path)

                gatherer.convert_nfcapd_csv(path, files, csv_path)

                print("converted nfcapd files", end="\n\n")

            elif option == 4:
                print("opening, format and modify the file", end="\n\n")

                path, files = tools.directory_content(csv_path + "raw_flows/")

                sample = input("\ncsv sample: ")

                flows, file_name = gatherer.open_csv(path, files, int(sample))

                ft = Formatter(flows)
                header, flows = ft.format_flows()

                md = Modifier(flows, header)
                header, flows = md.modify_flows()

                export_flows(flows, csv_path + "flows/",
                             file_name.split(".csv")[0] + "_w60"
                             + "_s" + sample + ".csv",
                             header)

                print("completed file", end="\n\n")

            elif option == 5:
                print("merging flows", end="\n\n")

                dataset_name = input("dataset name: ") + ".csv"
                print()

                path, files = tools.directory_content(csv_path + "flows/")

                print()
                start_idx = int(input("choose initial csv file: "))-1
                final_idx = int(input("choose final csv file: "))-1
                print()

                for idx in range(start_idx, final_idx + 1):
                    flows = gatherer.open_csv(path, files[idx],
                                              execute_model=True)[0]

                    if idx == start_idx:
                        export_flows(flows, csv_path,
                                     dataset_name, mode='a')
                    else:
                        export_flows(flows[1:], csv_path,
                                     dataset_name, mode='a')

                print("merged flows", end="\n\n")

            elif option == 6:
                print("cleaning nfcapd files", end="\n\n")

                tools.clean_files(nfcapd_path, csv_path)

                print("completed cleaning", end="\n\n")

            elif option == 7:
                break
            else:
                print("Invalid option")

            print("building the dataset", end="\n\n")
            option = tools.menu(["split pcap", "convert pcap to nfcapd", "convert nfcapd to flows",
                           "format and modify the flows", "merge flows files", "clean nfcapd files", "back to main"])
            print()

        print("dataset built", end="\n\n")

    elif option == 2:
        try:
            print("training the model")

            path, files = tools.directory_content(csv_path)

            flows = gatherer.open_csv(path, files)[0]

            ft = Formatter(flows)
            header, flows = ft.format_flows(True)

            ex = Extractor(header, flows)
            header_features, features = ex.extract_features([10, 15])
            labels = ex.extract_labels()

            features = ex.preprocessing_features(features, 0)

            option = tools.menu(["visualize the dataset patterns",
                                 "execute the machine learning algorithms",
                                 "back to main"])
            print()

            while option != 3:
                if option == 1:
                    for x_column, x_lbl in enumerate(header_features[0]):
                        for y_column, y_lbl in enumerate(header_features[0]):
                            if y_column != x_column:
                                scatter_plot(features, labels,
                                             x_column, y_column,
                                             x_lbl, y_lbl)

                    pattern = dt.find_patterns(features)
                    scatter_plot(pattern, labels, 0, 1, 'x', 'y')

                elif option == 2:
                    kf = ex.k_fold(int(input("split data in: ")), True)
                    print()

                    dataset = ex.train_test_split(features, labels, 0.30)

                    num_clf = dt.choose_classifiers([0, 5])

                    for idx in range(num_clf):
                        dt.tuning_hyperparameters(kf, idx)

                        pred, param, date, duration = dt.execute_classifiers(
                                dataset[0], dataset[1], dataset[2], idx)

                        _ = evaluation_metrics(dataset[3], pred, param,
                                           [date, dt.methods[idx], duration],
                                           dataset_path + result_name, idx)

                elif option == 3:
                    break
                else:
                    print("Invalid option")

                option = tools.menu(["visualize the dataset patterns",
                                     "execute the machine learning algorithms",
                                     "back to main"])
                print()
        except ValueError as error:
            print(error, end="\n\n")

        print("model finished", end="\n\n")

    elif option == 3:

        process = gatherer.nfcapd_collector(nfcapd_path, 60)

        time.sleep(5)
        try:
            num = 0
            while True:
                path, files = tools.directory_content(nfcapd_path)

                skip = gatherer.convert_nfcapd_csv(path, files, csv_path, True)

                if skip == 0:
                    path, files = tools.directory_content(csv_path, True)

                    flows = gatherer.open_csv(path, files, -1, True)

                    tools.clean_files(True)

                    ft = Formatter(flows)
                    header, flows = ft.format_flows()

                    md = Modifier(flows, header)
                    header, flows = md.modify_flows(True)

                    ex = Extractor(flows)
                    features = ex.extract_features(8, 16)
                    features = ex.preprocessing_features(features)

                    pred = dt.execute_classifiers(test_features=features,
                                                  execute_model=True)[0]

                    for idx, entry in enumerate(flows):
                        entry[-1] = pred[0][idx]

                    export_flows(flows, csv_path + "flows/", "flows_w" + str(60) + "_"
                                 + result_name, header)

                    print("ok")

                time.sleep(1)
        finally:
            process.kill()

    elif option == 4:
        exit()
    else:
        print("invalid option")

    print("anomaly detector")
    option = tools.menu(["build the dataset",
                         "train the model",
                         "execute the model",
                         "stop"])
    print()