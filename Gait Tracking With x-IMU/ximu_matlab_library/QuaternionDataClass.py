import numpy as np
from TimeSeriesDataBaseClass import TimeSeriesDataBaseClass

class QuaternionDataClass(TimeSeriesDataBaseClass):
    def __init__(self, *args):
        super().__init__()
        self.FileNameAppendage = '_Quaternion.csv'
        self.Quaternion = np.array([])
        
        if len(args) >= 1:
            fileNamePrefix = args[0]
            for i in range(1, len(args), 2):
                if args[i] == 'SampleRate':
                    self.SampleRate = args[i+1]
                else:
                    raise Exception('Invalid argument.')
            
            data = self._ImportCSVnumeric(fileNamePrefix)
            if data is not None and len(data) > 0:
                self.Quaternion = data[:, 1:5]
                self.SampleRate = self.SampleRate # call set method to create time vector
                
    def Plot(self):
        raise Exception('This method is unimplemented.')
