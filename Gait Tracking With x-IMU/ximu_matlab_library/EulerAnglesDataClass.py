import numpy as np
import matplotlib.pyplot as plt
from TimeSeriesDataBaseClass import TimeSeriesDataBaseClass

class EulerAnglesDataClass(TimeSeriesDataBaseClass):
    def __init__(self, *args):
        super().__init__()
        self.FileNameAppendage = '_EulerAngles.csv'
        self.Phi = np.array([])
        self.Theta = np.array([])
        self.Psi = np.array([])
        
        if len(args) >= 1:
            fileNamePrefix = args[0]
            for i in range(1, len(args), 2):
                if args[i] == 'SampleRate':
                    self.SampleRate = args[i+1]
                else:
                    raise Exception('Invalid argument.')
            
            data = self._ImportCSVnumeric(fileNamePrefix)
            if data is not None and len(data) > 0:
                self.Phi = data[:, 1]
                self.Theta = data[:, 2]
                self.Psi = data[:, 3]
                self.SampleRate = self.SampleRate # call set method to create time vector
                
    def Plot(self):
        if self.NumPackets == 0:
            raise Exception('No data to plot.')
            
        if len(self.Time) == 0:
            time = np.arange(1, self.NumPackets + 1)
        else:
            time = self.Time
            
        fig, ax = plt.subplots(1, 1, num=self._CreateFigName())
        
        ax.plot(time, self.Phi, 'r', label='$\\phi$')
        ax.plot(time, self.Theta, 'g', label='$\\theta$')
        ax.plot(time, self.Psi, 'b', label='$\\psi$')
        ax.set_title('Euler angles')
        ax.set_xlabel(self.TimeAxis)
        ax.set_ylabel('Angle (degrees)')
        ax.legend()
        
        plt.tight_layout()
        plt.show()
        return fig
