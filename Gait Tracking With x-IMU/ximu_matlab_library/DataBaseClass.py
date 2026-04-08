import os
import numpy as np

class DataBaseClass:
    def __init__(self):
        self.FileNameAppendage = ""
        self.NumPackets = 0
        self.PacketNumber = np.array([])
        
    def _ImportCSVnumeric(self, fileNamePrefix):
        file_name = self._CreateFileName(fileNamePrefix)
        try:
            data = np.genfromtxt(file_name, delimiter=',', skip_header=1)
            # handle case where data is 1D (only 1 row)
            if data.ndim == 1:
                data = data.reshape(1, -1)
            if data.size > 0:
                self.PacketNumber = data[:, 0]
                self.NumPackets = len(self.PacketNumber)
            return data
        except Exception as e:
            raise e

    def _ImportCSVmixed(self, fileNamePrefix, fieldSpecifier=None):
        import csv
        file_name = self._CreateFileName(fileNamePrefix)
        data = []
        with open(file_name, 'r') as fid:
            reader = csv.reader(fid)
            next(reader, None) # disregard column headings
            for row in reader:
                data.append(row)
        
        # We try to mimic MATLAB's cell returning format by storing columns
        parsed_data = list(map(list, zip(*data))) # Transpose to get columns
        if len(parsed_data) > 0:
            try:
                self.PacketNumber = np.array([float(x) for x in parsed_data[0]])
                self.NumPackets = len(self.PacketNumber)
            except ValueError:
                self.PacketNumber = parsed_data[0]
                self.NumPackets = len(self.PacketNumber)
        return parsed_data
        
    def _CreateFigName(self):
        _, name_ext = os.path.split(self.FileNameAppendage)
        name, _ = os.path.splitext(name_ext)
        return name[1:] # 2:end in Matlab

    def _CreateFileName(self, fileNamePrefix):
        file_name = fileNamePrefix + self.FileNameAppendage
        if not os.path.exists(file_name):
            raise Exception('File not found. No data was imported.')
        return file_name
