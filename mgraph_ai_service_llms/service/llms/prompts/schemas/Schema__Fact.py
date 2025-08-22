from osbot_utils.type_safe.Type_Safe import Type_Safe

class Schema__Fact(Type_Safe):      # Represents a single extracted fact from text
    fact        : str               # The extracted fact
    confidence  : float             # Confidence level (0-1) in the fact's accuracy
    category    : str               # Category of fact (e.g., "date", "person", "location", "number", "event")

