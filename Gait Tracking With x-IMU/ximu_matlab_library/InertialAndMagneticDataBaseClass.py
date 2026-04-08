import numpy as np
import matplotlib.pyplot as plt
from TimeSeriesDataBaseClass import TimeSeriesDataBaseClass

class InertialAndMagneticDataBaseClass(TimeSeriesDataBaseClass):
    def __init__(self):
        super().__init__()
        self.Gyroscope = {'X': np.array([]), 'Y': np.array([]), 'Z': np.array([])}
        self.Accelerometer = {'X': np.array([]), 'Y': np.array([]), 'Z': np.array([])}
        self.Magnetometer = {'X': np.array([]), 'Y': np.array([]), 'Z': np.array([])}
        
        self.GyroscopeUnits = ""
        self.AccelerometerUnits = ""
        self.MagnetometerUnits = ""
        
    def _Import(self, fileNamePrefix):
        data = self._ImportCSVnumeric(fileNamePrefix)
        if data is not None and len(data) > 0:
            self.Gyroscope['X'] = data[:, 1]
            self.Gyroscope['Y'] = data[:, 2]
            self.Gyroscope['Z'] = data[:, 3]
            self.Accelerometer['X'] = data[:, 4]
            self.Accelerometer['Y'] = data[:, 5]
            self.Accelerometer['Z'] = data[:, 6]
            self.Magnetometer['X'] = data[:, 7]
            self.Magnetometer['Y'] = data[:, 8]
            self.Magnetometer['Z'] = data[:, 9]
            self.SampleRate = self.SampleRate
            
    def Plot(self):
        if self.NumPackets == 0:
            raise Exception('No data to plot.')
            
        if len(self.Time) == 0:
            time = np.arange(1, self.NumPackets + 1)
        else:
            time = self.Time
            
        fig, ax = plt.subplots(3, 1, sharex=True, num=self._CreateFigName())
        
        ax[0].plot(time, self.Gyroscope['X'], 'r', label='X')
        ax[0].plot(time, self.Gyroscope['Y'], 'g', label='Y')
        ax[0].plot(time, self.Gyroscope['Z'], 'b', label='Z')
        ax[0].legend()
        ax[0].set_xlabel(self.TimeAxis)
        ax[0].set_ylabel(f"Angular rate ({self.GyroscopeUnits})")
        ax[0].set_title('Gyroscope')
        
        ax[1].plot(time, self.Accelerometer['X'], 'r', label='X')
        ax[1].plot(time, self.Accelerometer['Y'], 'g', label='Y')
        ax[1].plot(time, self.Accelerometer['Z'], 'b', label='Z')
        ax[1].legend()
        ax[1].set_xlabel(self.TimeAxis)
        ax[1].set_ylabel(f"Acceleration ({self.AccelerometerUnits})")
        ax[1].set_title('Accelerometer')
        
        ax[2].plot(time, self.Magnetometer['X'], 'r', label='X')
        ax[2].plot(time, self.Magnetometer['Y'], 'g', label='Y')
        ax[2].plot(time, self.Magnetometer['Z'], 'b', label='Z')
        ax[2].legend()
        ax[2].set_xlabel(self.TimeAxis)
        ax[2].set_ylabel(f"Flux ({self.MagnetometerUnits})")
        ax[2].set_title('Magnetometer')
        
        plt.tight_layout()
        plt.show()
        return fig
