import numpy as np

def SyncroniseData(*args, **kwargs):
    xIMUdata = args[0]
    # xIMUdata in MATLAB was a struct, here it will be a dict of xIMUdataClass instances
    xIMUdataObjs = list(xIMUdata.values())
    
    StartEventTimes = []
    EndEventTimes = []
    UseAX0fallingEdge = False
    
    if len(args) > 1 and isinstance(args[1], str):
        if args[1] == 'UseAX0fallingEdge':
            UseAX0fallingEdge = True
        else:
            raise Exception('Invalid argument.')
    elif len(args) > 1:
        StartEventTimes = args[1]
        if len(args) == 3:
            EndEventTimes = args[2]
            
    # Use AX0 falling edge of auxiliary port in Digital I/O mode
    if UseAX0fallingEdge:
        for obj in xIMUdataObjs:
            # find falling edges in DigitalIOdata.State['AX0']
            ax0_state = obj.DigitalIOdata.State['AX0']
            diff_state = np.diff(ax0_state)
            fallingEdgeIndexes = np.concatenate(([0], diff_state)) == -1
            fallingEdgeTimes = obj.DigitalIOdata.Time[fallingEdgeIndexes]
            
            if len(fallingEdgeTimes) > 0:
                StartEventTimes.append(fallingEdgeTimes[0])
            if len(fallingEdgeTimes) > 1:
                EndEventTimes.append(fallingEdgeTimes[-1])
                
        StartEventTimes = np.array(StartEventTimes)
        EndEventTimes = np.array(EndEventTimes)
                
    # Modify start times
    if len(StartEventTimes) != len(xIMUdataObjs):
        raise Exception('Length of StartEventTimes vector must equal number of xIMUdataClass objects')
        
    for i, obj in enumerate(xIMUdataObjs):
        if obj.DateTimeData: obj.DateTimeData.StartTime = -StartEventTimes[i]
        if obj.RawBatteryAndThermometerData: obj.RawBatteryAndThermometerData.StartTime = -StartEventTimes[i]
        if obj.CalBatteryAndThermometerData: obj.CalBatteryAndThermometerData.StartTime = -StartEventTimes[i]
        if obj.RawInertialAndMagneticData: obj.RawInertialAndMagneticData.StartTime = -StartEventTimes[i]
        if obj.CalInertialAndMagneticData: obj.CalInertialAndMagneticData.StartTime = -StartEventTimes[i]
        if obj.QuaternionData: obj.QuaternionData.StartTime = -StartEventTimes[i]
        if obj.RotationMatrixData: obj.RotationMatrixData.StartTime = -StartEventTimes[i]
        if obj.EulerAnglesData: obj.EulerAnglesData.StartTime = -StartEventTimes[i]
        if obj.DigitalIOdata: obj.DigitalIOdata.StartTime = -StartEventTimes[i]
        if obj.RawAnalogueInputData: obj.RawAnalogueInputData.StartTime = -StartEventTimes[i]
        if obj.CalAnalogueInputData: obj.CalAnalogueInputData.StartTime = -StartEventTimes[i]
        if obj.RawADXL345busData: obj.RawADXL345busData.StartTime = -StartEventTimes[i]
        if obj.CalADXL345busData: obj.CalADXL345busData.StartTime = -StartEventTimes[i]
        
    # Modify sample rate to synchronise end of window
    if len(EndEventTimes) == 0:
        return
        
    if len(EndEventTimes) != len(xIMUdataObjs):
        raise Exception('Length of EndEventTimes vector must equal number of xIMUdataClass objects')
        
    scalers = (EndEventTimes - StartEventTimes) * (1.0 / (EndEventTimes[0] - StartEventTimes[0]))
    for i in range(1, len(xIMUdataObjs)): # 2:numel in MATLAB (1-indexed) maps to 1:len in Python
        obj = xIMUdataObjs[i]
        s = scalers[i]
        t = StartEventTimes[i]
        
        def scale(h):
            if h is not None:
                h.SampleRate = s * h.SampleRate
                h.StartTime = t / s
                
        scale(obj.DateTimeData)
        scale(obj.RawBatteryAndThermometerData)
        scale(obj.CalBatteryAndThermometerData)
        scale(obj.RawInertialAndMagneticData)
        scale(obj.CalInertialAndMagneticData)
        scale(obj.QuaternionData)
        scale(obj.RotationMatrixData)
        scale(obj.EulerAnglesData)
        scale(obj.DigitalIOdata)
        scale(obj.RawAnalogueInputData)
        scale(obj.CalAnalogueInputData)
        scale(obj.RawADXL345busData)
        scale(obj.CalADXL345busData)
