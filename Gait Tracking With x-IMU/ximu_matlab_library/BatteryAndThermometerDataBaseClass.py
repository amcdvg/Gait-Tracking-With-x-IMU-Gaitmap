import numpy as np
import matplotlib.pyplot as plt
from TimeSeriesDataBaseClass import TimeSeriesDataBaseClass

class BatteryAndThermometerDataBaseClass(TimeSeriesDataBaseClass):
    def __init__(self):
        super().__init__()
        self.Battery = np.array([])
        self.Thermometer = np.array([])
        
        self.ThermometerUnits = ""
        self.BatteryUnits = ""
        
    def _Import(self, fileNamePrefix):
        data = self._ImportCSVnumeric(fileNamePrefix)
        if data is not None and len(data) > 0:
            self.Battery = data[:, 1]
            self.Thermometer = data[:, 2]
            self.SampleRate = self.SampleRate # trigger set method
            
    def Plot(self):
        if self.NumPackets == 0:
            raise Exception('No data to plot.')
            
        if len(self.Time) == 0:
            time = np.arange(1, self.NumPackets + 1)
        else:
            time = self.Time
            
        fig, ax = plt.subplots(2, 1, sharex=True, num=self._CreateFigName())
        
        ax[0].plot(time, self.Battery)
        ax[0].set_xlabel(self.TimeAxis)
        ax[0].set_ylabel(f"Voltage ({self.BatteryUnits})")
        ax[0].set_title('Battery Voltmeter')
        
        ax[1].plot(time, self.Thermometer)
        ax[1].set_xlabel(self.TimeAxis)
        ax[1].set_ylabel(f"Temperature ({self.ThermometerUnits})")
        ax[1].set_title('Thermometer')
        
        plt.tight_layout()
        plt.show()
        return fig
