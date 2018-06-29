import pandas as pd
import json
import os

class CSVFolderConnector:
    def __init__(self, csvfolderpath):
        self.csvfiles = [file for file in os.listdir(csvfolderpath) if file.endswith('.csv')]
        self.data = [pd.read_csv(csvfolderpath + csv, encoding='latin-1') for csv in self.csvfiles]

    def get_data(self):
        datadict = dict((name[:-4], frame.to_json()) for (name, frame) in zip(self.csvfiles, self.data))
        return json.dumps(datadict)

    def get_input_scheme(self):
        scheme = dict((name[:-4], list(frame)) for (name, frame) in zip(self.csvfiles, self.data))
        return json.dumps(scheme)
