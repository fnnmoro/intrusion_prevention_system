from core import pcap_path, nfcapd_path, csv_path
from model import gatherer, tools
from model.preprocessing import Formatter
from model.preprocessing import Modifier
from view import export_flows


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

        gatherer.split_pcap(path, files, int(input("\nsplit size: ")))

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
        header, flows = ft.format_flows(int(input("label number: ")))

        md = Modifier(flows, header)
        header, flows = md.modify_flows(100, True)

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
        print("invalid option")

    print("building the dataset", end="\n\n")
    option = tools.menu(["split pcap",
                         "convert pcap to nfcapd",
                         "convert nfcapd to flows",
                         "format and modify the flows",
                         "merge flows files",
                         "clean nfcapd files",
                         "back to main"])
    print()

print("dataset built", end="\n\n")
