import os
import glob
from xIMUdataClass import xIMUdataClass

def ImportDirectory(directory):
    # list all *_*.csv files in directory
    search_path = os.path.join(directory, '*_*.csv')
    listing = glob.glob(search_path)
    
    # list unique file name prefixes (e.g. name_*.csv)
    file_name_prefixes = []
    for f in listing:
        basename = os.path.basename(f)
        prefix = basename.split('_')[0]
        if prefix not in file_name_prefixes:
            file_name_prefixes.append(prefix)
            
    xIMUdataObjs = []
    
    for prefix in file_name_prefixes:
        try:
            full_prefix = os.path.join(directory, prefix)
            obj = xIMUdataClass(full_prefix)
            xIMUdataObjs.append(obj)
        except Exception as e:
            pass
            
    if len(xIMUdataObjs) == 0:
        raise Exception('No data was imported.')
        
    xIMUdataStruct = {}
    try:
        # try using device IDs as structure field names
        for obj in xIMUdataObjs:
            # dec2hex behavior
            device_id_dec = int(obj.RegisterData.GetValueAtAddress(2))
            field_name = 'ID_' + hex(device_id_dec)[2:].upper()
            xIMUdataStruct[field_name] = obj
            
    except Exception:
        # otherwise use file name prefix (alpha-numeric characters only)
        xIMUdataStruct = {} # Reset
        for i, obj in enumerate(xIMUdataObjs):
            prefix = file_name_prefixes[i]
            alphanum_prefix = ''.join(c for c in prefix if c.isalnum())
            field_name = 'FILE_' + alphanum_prefix
            xIMUdataStruct[field_name] = obj
            
    # sort dict by keys
    xIMUdataStruct = dict(sorted(xIMUdataStruct.items()))
    return xIMUdataStruct
