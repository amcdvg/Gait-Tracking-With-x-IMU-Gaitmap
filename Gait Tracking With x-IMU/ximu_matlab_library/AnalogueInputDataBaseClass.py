import numpy as np
import matplotlib.pyplot as plt
from TimeSeriesDataBaseClass import TimeSeriesDataBaseClass

class AnalogueInputDataBaseClass(TimeSeriesDataBaseClass):
    def __init__(self):
        super().__init__()
        self.AX0 = np.array([])
        self.AX1 = np.array([])
        self.AX2 = np.array([])
        self.AX3 = np.array([])
        self.AX4 = np.array([])
        self.AX5 = np.array([])
        self.AX6 = np.array([])
        self.AX7 = np.array([])
        
        self.ADCunits = ""
        
    def _Import(self, fileNamePrefix):
        data = self._ImportCSVnumeric(fileNamePrefix)
        if data is not None and len(data) > 0:
            self.AX0 = data[:, 1]
            self.AX1 = data[:, 2]
            self.AX2 = data[:, 3]
            self.AX3 = data[:, 4]
            self.AX4 = data[:, 5]
            self.AX5 = data[:, 6]
            self.AX6 = data[:, 7]
            self.AX7 = data[:, 8]
            self.SampleRate = self.SampleRate # trigger set method
            
    def Plot(self):
        if self.NumPackets == 0:
            raise Exception('No data to plot.')
            
        if len(self.Time) == 0:
            time = np.arange(1, self.NumPackets + 1)
        else:
            time = self.Time
            
        fig, ax = plt.subplots(1, 1, num=self._CreateFigName())
        
        ax.plot(time, self.AX0, 'r', label='AX0')
        ax.plot(time, self.AX1, 'g', label='AX1')
        ax.plot(time, self.AX2, 'b', label='AX2')
        ax.plot(time, self.AX3, 'k', label='AX3')
        ax.plot(time, self.AX4, ':r', label='AX4')
        ax.plot(time, self.AX5, ':g', label='AX5')
        ax.plot(time, self.AX6, ':b', label='AX6')
        ax.plot(time, self.AX7, ':k', label='AX7')
        
        ax.set_xlabel(self.TimeAxis)
        ax.set_ylabel(f"Voltage ({self.ADCunits})")
        ax.set_title('Analogue Input')
        
        plt.tight_layout()
        plt.show()
        return fig
