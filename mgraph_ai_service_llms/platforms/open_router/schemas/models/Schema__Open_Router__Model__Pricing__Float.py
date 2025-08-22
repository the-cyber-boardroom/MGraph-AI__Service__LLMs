from decimal import Decimal

from osbot_utils.type_safe.primitives.safe_float.Safe_Float import Safe_Float


class Schema__Open_Router__Model__Pricing__Float(Safe_Float):

    # note this is used by Schema__Open_Router__Model__Pricing
    # todo, see if this should not be renamed .json()
    def to_original_string(self) -> str:             # Convert back to original price string format
        if self == 0:
            return "0"


        d = Decimal(str(self))                      # Use Decimal to maintain precision


        formatted = format(d, 'f')                  # Format without scientific notation

        # Remove trailing zeros after decimal point
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')

        return formatted if formatted else "0"