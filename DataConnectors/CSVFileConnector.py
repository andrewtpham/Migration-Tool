import pandas as pd
import json


class CSVFileConnector:
    def __init__(self, csvfilepath):
        self.csvFile = csvfilepath
        self.data = pd.read_csv(self.csvFile, encoding='latin-1', skiprows=1)

    def get_data(self):
        return self.data.to_json()

    def get_input_scheme(self):
        json_keys = list(json.loads(self.data.to_json()).keys())
        return json.dumps({self.csvFile[2:-4]: json_keys})
