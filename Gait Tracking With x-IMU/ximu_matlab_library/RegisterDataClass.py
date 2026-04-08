from DataBaseClass import DataBaseClass
import numpy as np

class RegisterDataClass(DataBaseClass):
    def __init__(self, fileNamePrefix):
        super().__init__()
        self.FileNameAppendage = '_Registers.csv'
        self.Address = np.array([])
        self.Value = np.array([])
        self.FloatValue = np.array([])
        self.Name = []
        
        data = self._ImportCSVmixed(fileNamePrefix, '%f %f %f %f %s')
        if len(data) >= 5:
            self.Address = np.array([float(x) for x in data[1]])
            self.Value = np.array([float(x) for x in data[2]])
            self.FloatValue = np.array([float(x) for x in data[3]])
            self.Name = data[4]
            
    def GetValueAtAddress(self, address):
        return self._ValueAtIndexes(self._IndexesOfAddress(address))
        
    def GetFloatValueAtAddress(self, address):
        return self._FloatValueAtIndexes(self._IndexesOfAddress(address))
        
    def GetValueAtName(self, name):
        return self._ValueAtIndexes(self._IndexesOfName(name))
        
    def GetFloatValueAtName(self, name):
        return self._FloatValueAtIndexes(self._IndexesOfName(name))
        
    # Private methods
    def _IndexesOfAddress(self, address):
        indexes = np.where(self.Address == address)[0]
        if len(indexes) == 0:
            raise Exception('Register address not found.')
        return indexes
        
    def _IndexesOfName(self, name):
        indexes = np.where(np.array(self.Name) == name)[0]
        if len(indexes) == 0:
            raise Exception('Register name not found.')
        return indexes
        
    def _ValueAtIndexes(self, indexes):
        unique_vals = np.unique(self.Value[indexes])
        if len(unique_vals) > 1:
            raise Exception('Conflicting register values exist.')
        return self.Value[indexes[0]]
        
    def _FloatValueAtIndexes(self, indexes):
        unique_vals = np.unique(self.FloatValue[indexes])
        if len(unique_vals) > 1:
            raise Exception('Conflicting register values exist.')
        return self.FloatValue[indexes[0]]
