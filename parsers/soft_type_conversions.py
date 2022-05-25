"""
soft_type_conversions.py
Created:     25 May 2022
Author:      James Macey
Description: Type conversions that don't raise exceptions.
"""

def sint(x):
    try:
        return int(x)
    except ValueError:
        return None

def sfloat(x):
    try:
        return float(x)
    except ValueError:
        return None