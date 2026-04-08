from DataBaseClass import DataBaseClass
import numpy as np

class PWMoutputDataClass(DataBaseClass):
    def __init__(self, fileNamePrefix):
        super().__init__()
        self.FileNameAppendage = '_PWMoutput.csv'
        self.AX0 = np.array([])
        self.AX2 = np.array([])
        self.AX4 = np.array([])
        self.AX6 = np.array([])
        
        data = self._ImportCSVnumeric(fileNamePrefix)
        if data is not None and len(data) > 0:
            self.AX0 = data[:, 1]
            self.AX2 = data[:, 2]
            self.AX4 = data[:, 3]
            self.AX6 = data[:, 4]
