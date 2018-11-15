from common_utils import *

# The partition types
partitions_types = {
    'FW1'      : 0,
    'FW2'      : 1,
    'DFU1'     : 2,
    'DFU2'     : 3,
    'SHR'      : 4,
}

# Infer from the size of the local key bag if we use a SIG token or not
# [RB] FIXME: this is a bit hardcoded, we should use a more flexible way of dealing
# with this.
def is_sig_token_used(encrypted_platform_bin_file):
    data = read_in_file(encrypted_platform_bin_file)
    if(len(data) > 400):
        return False
    else:
        return True
