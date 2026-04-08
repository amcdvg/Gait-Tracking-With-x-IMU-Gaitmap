import numpy as np
import matplotlib.pyplot as plt
from TimeSeriesDataBaseClass import TimeSeriesDataBaseClass

class DigitalIODataClass(TimeSeriesDataBaseClass):
    def __init__(self, *args):
        super().__init__()
        self.FileNameAppendage = '_DigitalIO.csv'
        self.Direction = {'AX0': np.array([]), 'AX1': np.array([]), 'AX2': np.array([]), 'AX3': np.array([]),
                          'AX4': np.array([]), 'AX5': np.array([]), 'AX6': np.array([]), 'AX7': np.array([])}
        self.State = {'AX0': np.array([]), 'AX1': np.array([]), 'AX2': np.array([]), 'AX3': np.array([]),
                      'AX4': np.array([]), 'AX5': np.array([]), 'AX6': np.array([]), 'AX7': np.array([])}
        
        if len(args) >= 1:
            fileNamePrefix = args[0]
            for i in range(1, len(args), 2):
                if args[i] == 'SampleRate':
                    self.SampleRate = args[i+1]
                else:
                    raise Exception('Invalid argument.')
            
            data = self._ImportCSVnumeric(fileNamePrefix)
            if data is not None and len(data) > 0:
                self.Direction['AX0'] = data[:, 1]
                self.Direction['AX1'] = data[:, 2]
                self.Direction['AX2'] = data[:, 3]
                self.Direction['AX3'] = data[:, 4]
                self.Direction['AX4'] = data[:, 5]
                self.Direction['AX5'] = data[:, 6]
                self.Direction['AX6'] = data[:, 7]
                self.Direction['AX7'] = data[:, 8]
                self.State['AX0'] = data[:, 9]
                self.State['AX1'] = data[:, 10]
                self.State['AX2'] = data[:, 11]
                self.State['AX3'] = data[:, 12]
                self.State['AX4'] = data[:, 13]
                self.State['AX5'] = data[:, 14]
                self.State['AX6'] = data[:, 15]
                self.State['AX7'] = data[:, 16]
                self.SampleRate = self.SampleRate # call set method to create time vector
                
    def Plot(self):
        if self.NumPackets == 0:
            raise Exception('No data to plot.')
            
        if len(self.Time) == 0:
            time = np.arange(1, self.NumPackets + 1)
        else:
            time = self.Time
            
        fig, ax = plt.subplots(1, 1, num=self._CreateFigName())
        
        ax.plot(time, self.State['AX0'], 'r', label='AX0')
        ax.plot(time, self.State['AX1'], 'g', label='AX1')
        ax.plot(time, self.State['AX2'], 'b', label='AX2')
        ax.plot(time, self.State['AX3'], 'k', label='AX3')
        ax.plot(time, self.State['AX4'], ':r', label='AX4')
        ax.plot(time, self.State['AX5'], ':g', label='AX5')
        ax.plot(time, self.State['AX6'], ':b', label='AX6')
        ax.plot(time, self.State['AX7'], ':k', label='AX7')
        
        ax.set_title('Digital I/O')
        ax.set_xlabel(self.TimeAxis)
        ax.set_ylabel('State (Binary)')
        ax.legend()
        
        plt.tight_layout()
        plt.show()
        return fig
