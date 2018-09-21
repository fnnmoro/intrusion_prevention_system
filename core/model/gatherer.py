import os
import csv
import subprocess


def split_pcap(pcap_path, pcap_files, size=0):
    try:
        # avoids to split if there isn't necessary
        if size != 0:

            # creates the split temporary folder
            if not os.path.exists(pcap_path + "split/"):
                os.system("mkdir {0}split/".format(pcap_path))

            print()
            start_idx = int(input("choose the initial pcap file: "))-1
            final_idx = int(input("choose the final pcap file: "))-1
            print()

            # loop to split multiple pcap files
            for i in range(start_idx, final_idx+1):
                file_name = pcap_files[i].split(".pcap")[0]

                # executes tcpdump program to split the pcap files
                subprocess.run("tcpdump -r {0}{1} -w {0}split/{2} -C {3}"
                               .format(pcap_path, pcap_files[i], file_name, size), shell=True,
                               check=True)

                print(pcap_path + pcap_files[i], end="\n\n")

            # renames all split pcap files
            for file in sorted(os.listdir(pcap_path + "split/")):
                os.rename(pcap_path + "split/" + file, "{0}{1}.pcap".format(pcap_path + "split/", file))
    except subprocess.CalledProcessError as error:
        print()
        print(error, end="\n\n")
    except ValueError as error:
        print()
        print(error, end="\n\n")
    except IndexError as error:
        print()
        print(error, end="\n\n")


def convert_pcap_nfcapd(pcap_path, pcap_files, nfcapd_path, win_time=60):
    try:
        print()
        start_idx = int(input("choose the initial pcap file: "))-1
        final_idx = int(input("choose the final pcap file: "))-1
        print()

        # loop to read the pcap files to convert to nfcapd files
        for i in range(start_idx, final_idx+1):
            print()
            print(pcap_path + pcap_files[i], end="\n\n")
            subprocess.run("nfpcapd -t {0} -T 10,11,64 -r {1}{2} -l {3}"
                           .format(win_time, pcap_path, pcap_files[i], nfcapd_path), shell=True, check=True)
    except subprocess.CalledProcessError as error:
        print()
        print(error, end="\n\n")
    except ValueError as error:
        print()
        print(error, end="\n\n")
    except IndexError as error:
        print()
        print(error)


def convert_nfcapd_csv(nfcapd_path, nfcapd_files, csv_path, execute_model=False):
    try:
        start_idx = 0
        final_idx = 0
        name = "execute"

        if execute_model == False:
            csv_path = csv_path + "raw_flows/"

            print()
            start_idx = int(input("choose the initial nfcapd file: "))-1
            final_idx = int(input("choose the final nfcapd file: "))-1
            print()

            name = input("csv name: ")
            print()
        else:
            csv_path = csv_path + "tmp_flows/"

        # time to complete the file name
        start_time = nfcapd_files[start_idx].split("nfcapd.")[1]
        final_time = nfcapd_files[final_idx].split("nfcapd.")[1]
        file_name = name + "_" + start_time + "-" + final_time + ".csv"

        skip = 1
        if "current" not in nfcapd_files[start_idx]:
            print(nfcapd_path + nfcapd_files[start_idx] + ":"
                  + nfcapd_files[final_idx], end="\n\n")

            # read the nfcapd files and convert to csv files
            subprocess.run("nfdump -O tstart -o csv -6 -R {0}{1}:{2} > {3}{4}"
                           .format(nfcapd_path, nfcapd_files[start_idx], nfcapd_files[final_idx],
                                   csv_path, file_name), shell=True, check=True)
            skip = 0
        return skip
    except subprocess.CalledProcessError as error:
        print()
        print(error, end="\n\n")
    except ValueError as error:
        print()
        print(error, end="\n\n")
    except IndexError as error:
        print()
        print(error, end="\n\n")


def open_csv(csv_path, csv_files, sample=-1, execute_model=False):
    """Opens a CSV file containing raw flows"""
    try:
        if execute_model == False:
            print()
            idx = int(input("choose csv file: "))-1
            print()

            csv_files = csv_files[idx]

            print(csv_path + csv_files, end="\n\n")

        with open(csv_path + csv_files, mode='r') as file:
            csv_file = csv.reader(file)
            flows = []
            count = 0

            for line in csv_file:
                # checks if the core number has been reached
                if count != sample:
                    # checks if is not the last line
                    if "Summary" not in line[0]:
                        flows.append(line)
                        count += 1
                    # break if the last line was found
                    else:
                        break
                # break if the core was reached
                else:
                    break
            return flows, csv_files
    except IndexError as error:
        print()
        print(error, end="\n\n")


def nfcapd_collector(nfcapd_path, win_time=0):
    try:
        process = subprocess.Popen(["nfcapd", "-t", str(win_time), "-T",
                                    "all", "-b", "127.0.0.1", "-p", "7777",
                                    "-l", nfcapd_path, "-D"])
        return process
    except subprocess.CalledProcessError as error:
        print()
        print(error, end="\n\n")
