from ADXL345busDataBaseClass import ADXL345busDataBaseClass

class RawADXL345busDataClass(ADXL345busDataBaseClass):
    def __init__(self, *args):
        super().__init__()
        self.FileNameAppendage = '_RawADXL345bus.csv'
        
        if len(args) >= 1:
            fileNamePrefix = args[0]
            for i in range(1, len(args), 2):
                if args[i] == 'SampleRate':
                    self.SampleRate = args[i+1]
                else:
                    raise Exception('Invalid argument.')
            
            self._Import(fileNamePrefix)
            
            self.AccelerometerUnits = 'g'
