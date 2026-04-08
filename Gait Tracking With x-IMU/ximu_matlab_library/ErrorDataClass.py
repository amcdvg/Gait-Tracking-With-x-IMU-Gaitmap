import numpy as np
from DataBaseClass import DataBaseClass

class ErrorDataClass(DataBaseClass):
    def __init__(self, fileNamePrefix):
        super().__init__()
        self.FileNameAppendage = '_Errors.csv'
        self.Code = np.array([])
        self.Message = []
        
        data = self._ImportCSVmixed(fileNamePrefix, '%f %f %s')
        if len(data) >= 3:
            self.Code = np.array([float(x) for x in data[1]])
            self.Message = data[2]
