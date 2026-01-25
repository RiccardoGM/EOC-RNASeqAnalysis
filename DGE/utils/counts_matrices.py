import os
import pandas as pd
import numpy as np


def create_counts_matrices(counts_data_dir, metadata_dir, line_name, counts_mat_dir, batch=None):
    # load metadata
    metadata_file = f"{line_name}_metadata.csv"
    metadata_path = os.path.join(metadata_dir, metadata_file)
    metadata = pd.read_csv(metadata_path, header=0, index_col=0, sep=";")

    # initialize data list to store the count data
    data_list = {}

    # loop through metadata to read the count files
    count_data = None
    for i, name in enumerate(metadata.index):
        condition_name = metadata['name'].iloc[i]

        # find the corresponding file name
        file_list = [f for f in os.listdir(counts_data_dir) if name in f]
        if file_list:
            file_path = os.path.join(counts_data_dir, file_list[0])

            # read the count data
            count_data = pd.read_csv(file_path, header=None, index_col=0, sep="\t")

            # filter for rows with "ENSG0" in their index
            count_data = count_data[count_data.index.str.contains("ENSG0")]

            # store the filtered data in the data list
            data_list[condition_name] = count_data

    if count_data is None:
        print(f"ERROR: no count data found for {line_name}, or wrong format.")
        exit()

    # create the counts matrix
    count_matrix = np.full((len(count_data), len(metadata)), np.nan)

    for i, condition_name in enumerate(data_list):
        count_matrix[:, i] = data_list[condition_name].iloc[:, 0].values

    # set row names of the matrix
    rownames = data_list[condition_name].index

    # convert the matrix into a DataFrame
    count_matrix_df = pd.DataFrame(count_matrix, index=rownames, columns=metadata.index)

    # export the matrix to a file
    if batch:
        export_file_name = f"{line_name}_{batch}_counts_matrix.txt"
    export_file_name = f"{line_name}_counts_matrix.txt"
    export_path = os.path.join(counts_mat_dir, export_file_name)
    count_matrix_df.to_csv(export_path, sep="\t", header=False, index=True)
