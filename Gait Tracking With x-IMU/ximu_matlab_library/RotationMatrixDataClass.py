import numpy as np
import matplotlib.pyplot as plt
from TimeSeriesDataBaseClass import TimeSeriesDataBaseClass

class RotationMatrixDataClass(TimeSeriesDataBaseClass):
    def __init__(self, *args):
        super().__init__()
        self.FileNameAppendage = '_RotationMatrix.csv'
        self.RotationMatrix = np.array([])
        
        if len(args) >= 1:
            fileNamePrefix = args[0]
            for i in range(1, len(args), 2):
                if args[i] == 'SampleRate':
                    self.SampleRate = args[i+1]
                else:
                    raise Exception('Invalid argument.')
            
            data = self._ImportCSVnumeric(fileNamePrefix)
            if data is not None and len(data) > 0:
                self.RotationMatrix = np.zeros((3, 3, self.NumPackets))
                self.RotationMatrix[0, 0, :] = data[:, 1]
                self.RotationMatrix[0, 1, :] = data[:, 2]
                self.RotationMatrix[0, 2, :] = data[:, 3]
                self.RotationMatrix[1, 0, :] = data[:, 4]
                self.RotationMatrix[1, 1, :] = data[:, 5]
                self.RotationMatrix[1, 2, :] = data[:, 6]
                self.RotationMatrix[2, 0, :] = data[:, 7]
                self.RotationMatrix[2, 1, :] = data[:, 8]
                self.RotationMatrix[2, 2, :] = data[:, 9]
                self.SampleRate = self.SampleRate # call set method to create time vector
                
    def Plot(self):
        raise Exception('This method is unimplemented.')
