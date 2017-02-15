# Text Colors
RED = markup('c', bitwise_rgb(255, 0, 0))
BLUE = markup('c', bitwise_hex('#0e76b7'))
GRAY = markup('c', '4113')

# Font Styles
FONT_DEFAULT = markup('f', 'FONT_DEFAULT')
FONT_NORMAL = markup('f', 'FONT_NORMAL')
FONT_BOLD = markup('f', 'FONT_BOLD')
FONT_ITALIC = markup('f', 'FONT_ITALIC')

REGIONS = [
    '(anywhere)', # 0 is reserved ".anywhere" region index
    'batchTask', #1
    'taskParam', #2
    'taskParamMulti', #3
    'taskParamSub', #4
    'addNode', #5
    'null', #6
    'batchFile', #7
    'addTask', #8
    'addParam', #9
    'addToList', #10
    'addToDict' #11
]

COL_NAME = "Name"
COL_VALUE = "Value"
IMAGE_FORMAT = 'image_format'
SCENE_PATH = "scene"
