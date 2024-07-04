"""
Tämä toimii sillä tavalla, että jos tätä tarvii niin kutsu tämä:
from GlobalElements.Languages import Lang
sit sitä voi käyttää kutsumalla esim. Lang.FI
"""

from enum import IntEnum

class Lang(IntEnum):
    FI = 0
    SV = 1
    EN = 2