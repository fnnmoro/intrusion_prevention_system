import csv


def flows_csv(header, flows, dst_path, file_name):
    """Exports flows to CSV file.

    Parameters
    ----------
    header: list
        Features description.
    flows: list
        IP flows.
    dst_path: str
        Destination path where the file will be exported.
    file_name: str
        Name of CSV file."""

    with open(f'{dst_path}{file_name}', mode='a') as file:
        writer = csv.writer(file)

        writer.writerow(header)
        for entry in flows:
            writer.writerow(entry)
