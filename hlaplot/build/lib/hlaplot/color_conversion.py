"""
ColorConversion
    Convert colors between [0,255] and [0.0,1.0].  

Afonso Haruo Carnielli Mukai (FAC - LNLS)

2013-11-22: v0.1
"""

DEFAULT_BACKGROUND_COLOR = (246, 244, 242, 255)
DEFAULT_AXIS_BACKGROUND_COLOR = (255, 255, 255, 255) # white
DEFAULT_AXIS_ELEMENTS_COLOR = (0, 0, 0, 255) # black
MAX_RGB = 255


class RgbRangeException(Exception):
    pass


def _check_normalized_range(rgb_value):
    if not 0.0 <= rgb_value <= 1.0:
        raise RgbRangeException()

def _check_unnormalized_range(rgb_value):
    if not 0 <= rgb_value <= MAX_RGB:
        raise RgbRangeException() 

def _normalize_rgb_value(value):
    return float(value) / float(MAX_RGB)

def _denormalize_rgb_value(value):
    denormalized_float = float(MAX_RGB) * value
    return round(denormalized_float)

def _normalize_rgb_tuple(initial_rgb_tuple):
    normalized_rgb_list = []
    for i in range(len(initial_rgb_tuple)):
        _check_unnormalized_range(initial_rgb_tuple[i])
        value = _normalize_rgb_value(initial_rgb_tuple[i])
        normalized_rgb_list.append(value)
        
    return tuple(normalized_rgb_list)

def _denormalize_rgb_tuple(initial_rgb_tuple):
    denormalized_rgb_list = []
    for i in range(len(initial_rgb_tuple)):
        _check_normalized_range(initial_rgb_tuple[i])
        value = _denormalize_rgb_value(initial_rgb_tuple[i])
        denormalized_rgb_list.append(round(value))
        
    return tuple(denormalized_rgb_list)

def _is_string(s):
    return isinstance(s, str)

def normalize_color(color):
    """
    Return string or color in range [0.0,1.0].
    Raises RgbRangeException if elements of color are not in range.
    
    color -- string or RGB+alpha tuple in range [0,255]
    """
    if _is_string(color):
        return color
    else:
        return _normalize_rgb_tuple(color)
        
def denormalize_color(color):
    """
    Return string or color in range [0,255].
    Raises RgbRangeException if elements of color are not in range.
    
    color -- string or RGB+alpha tuple in range [0.0,1.0]
    """
    if _is_string(color):
        return color
    else:
        return _denormalize_rgb_tuple(color)
