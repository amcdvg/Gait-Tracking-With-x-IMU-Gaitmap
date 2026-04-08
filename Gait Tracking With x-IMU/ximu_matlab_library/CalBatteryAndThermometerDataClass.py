from BatteryAndThermometerDataBaseClass import BatteryAndThermometerDataBaseClass

class CalBatteryAndThermometerDataClass(BatteryAndThermometerDataBaseClass):
    def __init__(self, *args):
        super().__init__()
        self.FileNameAppendage = '_CalBattAndTherm.csv'
        
        if len(args) >= 1:
            fileNamePrefix = args[0]
            for i in range(1, len(args), 2):
                if args[i] == 'SampleRate':
                    self.SampleRate = args[i+1]
                else:
                    raise Exception('Invalid argument.')
            
            self._Import(fileNamePrefix)
            
            self.ThermometerUnits = '$^\\circ$C'
            self.BatteryUnits = 'V'
