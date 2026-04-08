import numpy as np
import matplotlib.pyplot as plt
from TimeSeriesDataBaseClass import TimeSeriesDataBaseClass

class ADXL345busDataBaseClass(TimeSeriesDataBaseClass):
    def __init__(self):
        super().__init__()
        self.ADXL345A = {'X': np.array([]), 'Y': np.array([]), 'Z': np.array([])}
        self.ADXL345B = {'X': np.array([]), 'Y': np.array([]), 'Z': np.array([])}
        self.ADXL345C = {'X': np.array([]), 'Y': np.array([]), 'Z': np.array([])}
        self.ADXL345D = {'X': np.array([]), 'Y': np.array([]), 'Z': np.array([])}
        
        self.AccelerometerUnits = ""
        
    def _Import(self, fileNamePrefix):
        data = self._ImportCSVnumeric(fileNamePrefix)
        if data is not None and len(data) > 0:
            self.ADXL345A['X'] = data[:, 1]
            self.ADXL345A['Y'] = data[:, 2]
            self.ADXL345A['Z'] = data[:, 3]
            self.ADXL345B['X'] = data[:, 4]
            self.ADXL345B['Y'] = data[:, 5]
            self.ADXL345B['Z'] = data[:, 6]
            self.ADXL345C['X'] = data[:, 7]
            self.ADXL345C['Y'] = data[:, 8]
            self.ADXL345C['Z'] = data[:, 9]
            self.ADXL345D['X'] = data[:, 10]
            self.ADXL345D['Y'] = data[:, 11]
            self.ADXL345D['Z'] = data[:, 12]
            self.SampleRate = self.SampleRate # trigger set method
            
    def Plot(self):
        if self.NumPackets == 0:
            raise Exception('No data to plot.')
            
        if len(self.Time) == 0:
            time = np.arange(1, self.NumPackets + 1)
        else:
            time = self.Time
            
        fig, ax = plt.subplots(4, 1, sharex=True, num=self._CreateFigName())
        
        ax[0].plot(time, self.ADXL345A['X'], 'r', label='X')
        ax[0].plot(time, self.ADXL345A['Y'], 'g', label='Y')
        ax[0].plot(time, self.ADXL345A['Z'], 'b', label='Z')
        ax[0].legend()
        ax[0].set_xlabel(self.TimeAxis)
        ax[0].set_ylabel(f"Acceleration ({self.AccelerometerUnits})")
        ax[0].set_title('ADXL345 A')
        
        ax[1].plot(time, self.ADXL345B['X'], 'r', label='X')
        ax[1].plot(time, self.ADXL345B['Y'], 'g', label='Y')
        ax[1].plot(time, self.ADXL345B['Z'], 'b', label='Z')
        ax[1].legend()
        ax[1].set_xlabel(self.TimeAxis)
        ax[1].set_ylabel(f"Acceleration ({self.AccelerometerUnits})")
        ax[1].set_title('ADXL345 B')
        
        ax[2].plot(time, self.ADXL345C['X'], 'r', label='X')
        ax[2].plot(time, self.ADXL345C['Y'], 'g', label='Y')
        ax[2].plot(time, self.ADXL345C['Z'], 'b', label='Z')
        ax[2].legend()
        ax[2].set_xlabel(self.TimeAxis)
        ax[2].set_ylabel(f"Acceleration ({self.AccelerometerUnits})")
        ax[2].set_title('ADXL345 C')
        
        ax[3].plot(time, self.ADXL345D['X'], 'r', label='X')
        ax[3].plot(time, self.ADXL345D['Y'], 'g', label='Y')
        ax[3].plot(time, self.ADXL345D['Z'], 'b', label='Z')
        ax[3].legend()
        ax[3].set_xlabel(self.TimeAxis)
        ax[3].set_ylabel(f"Acceleration ({self.AccelerometerUnits})")
        ax[3].set_title('ADXL345 D')
        
        plt.tight_layout()
        plt.show()
        return fig
