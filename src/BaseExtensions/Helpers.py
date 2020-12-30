
from types import FunctionType, MethodType
from typing import Union





__all__ = [
        'CalculateOffset', 'RoundFloat',
        'IsMethod', 'IsFunction',
        ]


def RoundFloat(Float: float, Precision: int) -> str:
    """ Rounds the Float to the given Precision and returns It as string. """
    return f"{Float:.{Precision}f}"

def CalculateOffset(starting: Union[int, float], *args: Union[int, float]) -> int:
    """
        Example: WrapLength = ScreenWidth * Widget.Parent.relwidth * Widget.relwidth * offset

    :param starting: starting value (such as width or height)
    :param args: a list of float or integers to be cumulatively multiplied together.
    :return:
    """
    for arg in args:
        if not isinstance(arg, (int, float)): arg = float(arg)
        starting *= arg
    return int(starting)





def IsMethod(o) -> bool:
    """
        Checks if passed object is a method

        https://stackoverflow.com/questions/37455426/advantages-of-using-methodtype-in-python
    :param o: object being checked
    :type o: any
    :return: weather it is a method
    :rtype: bool
    """
    return isinstance(o, MethodType)
def IsFunction(o) -> bool:
    """
        Checks if passed object is a function

        https://stackoverflow.com/questions/37455426/advantages-of-using-methodtype-in-python
    :param o: object being checked
    :type o: any
    :return: weather it is a method
    :rtype: bool
    """
    return isinstance(o, FunctionType)
