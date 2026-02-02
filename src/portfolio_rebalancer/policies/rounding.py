"""Rounding policies for integer share quantities."""

from enum import Enum


class RoundingPolicy(Enum):
    """Policy for rounding quantity changes to integer shares.
    
    Attributes:
        FLOOR: Round down (conservative for purchases)
        ROUND: Round to nearest integer (mathematical rounding)
        CEIL: Round up (aggressive for purchases)
    
    Note:
        After rounding, cash flow may not be exactly zero and
        post-rebalancing weights may deviate slightly from targets.
        These deviations are acceptable and reported to the user.
    """
    
    FLOOR = "floor"
    ROUND = "round"
    CEIL = "ceil"
