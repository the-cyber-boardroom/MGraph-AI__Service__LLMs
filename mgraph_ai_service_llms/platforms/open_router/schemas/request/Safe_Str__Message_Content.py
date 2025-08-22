import re
from osbot_utils.type_safe.primitives.safe_str.Safe_Str import Safe_Str

OPEN_ROUTER__MESSAGE__CONTENT__MAX_SIZE = 32768                                      # todo: see if this should be user controlable

class Safe_Str__Message_Content(Safe_Str):
    max_length  =  OPEN_ROUTER__MESSAGE__CONTENT__MAX_SIZE                          # currently 32k
    regex       = re.compile(r'[\x00\x01-\x08\x0B\x0C\x0E-\x1F]')                   # Only remove control chars
