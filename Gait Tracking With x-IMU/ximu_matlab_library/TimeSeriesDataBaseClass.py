import numpy as np
from DataBaseClass import DataBaseClass

class TimeSeriesDataBaseClass(DataBaseClass):
    def __init__(self):
        super().__init__()
        self._Time = np.array([])
        self._SampleRate = 0
        self._StartTime = 0
        self.TimeAxis = ""
        
    @property
    def Time(self):
        return self._Time
        
    @property
    def SamplePeriod(self):
        if self._SampleRate == 0:
            return 0
        else:
            return 1.0 / self._SampleRate
            
    @property
    def SampleRate(self):
        return self._SampleRate
        
    @SampleRate.setter
    def SampleRate(self, sampleRate):
        self._SampleRate = sampleRate
        if self._SampleRate == 0:
            self._Time = np.array([])
            self.TimeAxis = 'Sample'
        elif self.NumPackets != 0:
            self._Time = np.arange(0, self.NumPackets) * (1.0 / self._SampleRate) + self._StartTime
            self.TimeAxis = 'Time (s)'
            
    @property
    def StartTime(self):
        return self._StartTime
        
    @StartTime.setter
    def StartTime(self, startTime):
        self._StartTime = startTime
        self.SampleRate = self._SampleRate # Trigger sample rate setter logic
        
    def Plot(self):
        pass # Abstract in MATLAB
