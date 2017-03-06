

CLASS = 'lumberjack_class'
VPTYPE = 'viewport_type'
IDENT = 'ident'
sSRV_USERNAME = 'internal_name'
NICE_NAME = 'nice_name'
REGIONS = 'input_regions'
SERVERNAME = 'server_name'
CONFIG_NAME = 'config_name'
INTERNAL_NAME = 'internal_name'

LXfTREEITEM_ATTRIB =                    0x00000001 # Means listed under + instead of > in list.
LXfTREEITEM_EXPANDED =                  0x00000002
LXfTREEITEM_ATTREXP =                   0x00000004

LXfTREEITEM_HIDDEN =                    0x00000008

# TODO
# The FILTER flags are flags you're expected to store and return.
# They're set by the tree system.  This is all explained in the updated docs.
LXfTREEITEM_FILTERED =                  0x00000040
LXfTREEITEM_FILTER_SKIP =               0x00000080
LXfTREEITEM_FILTER_EXPANDED =           0x00000100
LXfTREEITEM_FILTER_ATTREXP =            0x00000200
LXfTREEITEM_FILTER_EXPANDED_BY_ =       0x00000400
LXfTREEITEM_FILTER_ATTREXP_BY_ =        0x00000800

LXmTREEITEM_CLIENT =                    0xFF000000 # Reserved for client use
