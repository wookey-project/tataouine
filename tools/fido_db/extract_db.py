# For parsing JSON
import glob
import json
import binascii
import sys, os, inspect
FILENAME = inspect.getframeinfo(inspect.currentframe()).filename
SCRIPT_PATH = os.path.dirname(os.path.abspath(FILENAME)) + "/"
sys.path.append(SCRIPT_PATH + "../images")
import rle_utils

EXISTING_APPID_PATH = SCRIPT_PATH
# Get all our existing relying parties
all_dicts = []
for rp_json in glob.glob(EXISTING_APPID_PATH + "*.json"):
    with open(rp_json, 'rb') as f:        
        icon = os.path.splitext(rp_json)[0]+".png"
        if os.path.isfile(icon) == False:
            icon = None
        all_dicts.append((json.load(f), icon))

print("u2f_rp_database = [")
for (a, icon) in all_dicts:
    try:
        for i in range(0, len(a['u2f'])):
            if icon != None:
                with open(icon, 'rb') as f:
                    encoded_icon = binascii.hexlify(f.read()).decode('latin-1')
                    print("{'name': '%s', 'url': '%s', 'appid': '%s', 'logo': b'%s'}," % (a['name'], a['u2f'][i]['label'], a['u2f'][i]['app_id'], encoded_icon))
            else:
                print("{'name': '%s', 'url': '%s', 'appid': '%s', 'logo': b'%s'}," % (a['name'], a['u2f'][i]['label'], a['u2f'][i]['app_id'], ""))
    except:
        #print("Error for %s: no U2F" % a['name'])
        pass
print("]")
