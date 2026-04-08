import numpy as np
import datetime
from TimeSeriesDataBaseClass import TimeSeriesDataBaseClass

class DateTimeDataClass(TimeSeriesDataBaseClass):
    def __init__(self, *args):
        super().__init__()
        self.FileNameAppendage = '_DateTime.csv'
        self.String = []
        self.Vector = np.array([])
        self.Serial = np.array([])
        
        if len(args) >= 1:
            fileNamePrefix = args[0]
            for i in range(1, len(args), 2):
                if args[i] == 'SampleRate':
                    self.SampleRate = args[i+1]
                else:
                    raise Exception('Invalid argument.')
            
            data = self._ImportCSVnumeric(fileNamePrefix)
            if data is not None and len(data) > 0:
                self.Vector = data[:, 1:7]
                
                # Convert to datetimes and strings
                self.String = []
                self.Serial = np.zeros(self.Vector.shape[0])
                for i in range(self.Vector.shape[0]):
                    try:
                        y, m, d, h, mn, s = self.Vector[i]
                        dt = datetime.datetime(int(y), int(m), int(d), int(h), int(mn), int(s))
                        self.String.append(dt.strftime('%d-%b-%Y %H:%M:%S'))
                        # Approximate datenum (days since year 0000) simply using ordinal + fraction
                        self.Serial[i] = dt.toordinal() + 366 + dt.hour/24.0 + dt.minute/1440.0 + dt.second/86400.0
                    except ValueError:
                        self.String.append("")
                        self.Serial[i] = 0
                
                self.SampleRate = self.SampleRate # Call set method to create time vector
                
    def Plot(self):
        raise Exception('This method is unimplemented.')
