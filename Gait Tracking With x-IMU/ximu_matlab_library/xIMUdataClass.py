# Imports of all modules
from ErrorDataClass import ErrorDataClass
from CommandDataClass import CommandDataClass
from RegisterDataClass import RegisterDataClass
from DateTimeDataClass import DateTimeDataClass
from RawBatteryAndThermometerDataClass import RawBatteryAndThermometerDataClass
from CalBatteryAndThermometerDataClass import CalBatteryAndThermometerDataClass
from RawInertialAndMagneticDataClass import RawInertialAndMagneticDataClass
from CalInertialAndMagneticDataClass import CalInertialAndMagneticDataClass
from QuaternionDataClass import QuaternionDataClass
from RotationMatrixDataClass import RotationMatrixDataClass
from EulerAnglesDataClass import EulerAnglesDataClass
from DigitalIODataClass import DigitalIODataClass
from RawAnalogueInputDataClass import RawAnalogueInputDataClass
from CalAnalogueInputDataClass import CalAnalogueInputDataClass
from PWMoutputDataClass import PWMoutputDataClass
from RawADXL345busDataClass import RawADXL345busDataClass
from CalADXL345busDataClass import CalADXL345busDataClass

import math

class xIMUdataClass:
    def __init__(self, *args, **kwargs):
        self.FileNamePrefix = args[0]
        self.ErrorData = None
        self.CommandData = None
        self.RegisterData = None
        self.DateTimeData = None
        self.RawBatteryAndThermometerData = None
        self.CalBatteryAndThermometerData = None
        self.RawInertialAndMagneticData = None
        self.CalInertialAndMagneticData = None
        self.QuaternionData = None
        self.RotationMatrixData = None
        self.EulerAnglesData = None
        self.DigitalIOdata = None
        self.RawAnalogueInputData = None
        self.CalAnalogueInputData = None
        self.PWMoutputData = None
        self.RawADXL345busData = None
        self.CalADXL345busData = None
        
        dataImported = False
        
        try: self.ErrorData = ErrorDataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        try: self.CommandData = CommandDataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        try: self.RegisterData = RegisterDataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        try: self.DateTimeData = DateTimeDataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        try: self.RawBatteryAndThermometerData = RawBatteryAndThermometerDataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        try: self.CalBatteryAndThermometerData = CalBatteryAndThermometerDataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        try: self.RawInertialAndMagneticData = RawInertialAndMagneticDataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        try: self.CalInertialAndMagneticData = CalInertialAndMagneticDataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        try: self.QuaternionData = QuaternionDataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        try: self.EulerAnglesData = EulerAnglesDataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        try: self.RotationMatrixData = RotationMatrixDataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        try: self.DigitalIOdata = DigitalIODataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        try: self.RawAnalogueInputData = RawAnalogueInputDataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        try: self.CalAnalogueInputData = CalAnalogueInputDataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        try: self.PWMoutputData = PWMoutputDataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        try: self.RawADXL345busData = RawADXL345busDataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        try: self.CalADXL345busData = CalADXL345busDataClass(self.FileNamePrefix); dataImported = True; 
        except Exception: pass
        
        if not dataImported:
            raise Exception('No data was imported.')
            
        # Apply SampleRate from register data
        def apply_sr_reg(attr, addr):
            try:
                if getattr(self, attr) and self.RegisterData:
                    getattr(self, attr).SampleRate = self._SampleRateFromRegValue(self.RegisterData.GetValueAtAddress(addr))
            except Exception: pass
            
        apply_sr_reg('DateTimeData', 67)
        apply_sr_reg('RawBatteryAndThermometerData', 68)
        apply_sr_reg('CalBatteryAndThermometerData', 68)
        apply_sr_reg('RawInertialAndMagneticData', 69)
        apply_sr_reg('CalInertialAndMagneticData', 69)
        apply_sr_reg('QuaternionData', 70)
        apply_sr_reg('RotationMatrixData', 70)
        apply_sr_reg('EulerAnglesData', 70)
        apply_sr_reg('DigitalIOdata', 78)
        apply_sr_reg('RawAnalogueInputData', 80)
        apply_sr_reg('CalAnalogueInputData', 80)
        apply_sr_reg('RawADXL345busData', 85)
        apply_sr_reg('CalADXL345busData', 85)
        
        # Apply SampleRate if specified as argument
        for i in range(1, len(args), 2):
            key = args[i]
            val = args[i+1]
            if key == 'DateTimeSampleRate':
                try: self.DateTimeData.SampleRate = val; 
                except Exception: pass
            elif key == 'BattThermSampleRate':
                try: self.RawBatteryAndThermometerData.SampleRate = val; 
                except Exception: pass
                try: self.CalBatteryAndThermometerData.SampleRate = val; 
                except Exception: pass
            elif key == 'InertialMagneticSampleRate':
                try: self.RawInertialAndMagneticData.SampleRate = val; 
                except Exception: pass
                try: self.CalInertialAndMagneticData.SampleRate = val; 
                except Exception: pass
            elif key == 'QuaternionSampleRate':
                try: self.QuaternionData.SampleRate = val; 
                except Exception: pass
                try: self.RotationMatrixData.SampleRate = val; 
                except Exception: pass
                try: self.EulerAnglesData.SampleRate = val; 
                except Exception: pass
            elif key == 'DigitalIOSampleRate':
                try: self.DigitalIOdata.SampleRate = val; 
                except Exception: pass
            elif key == 'AnalogueInputSampleRate':
                try: self.RawAnalogueInputData.SampleRate = val; 
                except Exception: pass
                try: self.CalAnalogueInputData.SampleRate = val; 
                except Exception: pass
            elif key == 'ADXL345SampleRate':
                try: self.RawADXL345busData.SampleRate = val; 
                except Exception: pass
                try: self.CalADXL345busData.SampleRate = val; 
                except Exception: pass
            else:
                raise Exception('Invalid argument.')
                
    def Plot(self):
        try: self.RawBatteryAndThermometerData.Plot(); 
        except Exception: pass
        try: self.CalBatteryAndThermometerData.Plot(); 
        except Exception: pass
        try: self.RawInertialAndMagneticData.Plot(); 
        except Exception: pass
        try: self.CalInertialAndMagneticData.Plot(); 
        except Exception: pass
        try: self.QuaternionData.Plot(); 
        except Exception: pass
        try: self.EulerAnglesData.Plot(); 
        except Exception: pass
        try: self.RotationMatrixData.Plot(); 
        except Exception: pass
        try: self.DigitalIOdata.Plot(); 
        except Exception: pass
        try: self.RawAnalogueInputData.Plot(); 
        except Exception: pass
        try: self.CalAnalogueInputData.Plot(); 
        except Exception: pass
        try: self.RawADXL345busData.Plot(); 
        except Exception: pass
        try: self.CalADXL345busData.Plot(); 
        except Exception: pass

    def _SampleRateFromRegValue(self, value):
        return math.floor(2**(value-1))
