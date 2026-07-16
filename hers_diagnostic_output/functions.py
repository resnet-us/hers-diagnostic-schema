from typing import List

from .definitions import FuelType, fossil_fuel_types


def to_upper_case(string: str):
    return string.upper()


def get_annual_data(list_8760: List[float]) -> float:
    return sum(list_8760)


def get_fuel_conversion(fuel_type: FuelType):
    # If fuel type is a fossil fuel, return 0.4, else return 1

    if fuel_type in fossil_fuel_types:
        return 0.4
    return 1.0


def product_lists(list1: List[float], list2: List[float]) -> List[float]:
    return_list: List[float] = [0.0] * len(list1)
    for index, (value1, value2) in enumerate(zip(list1, list2)):
        return_list[index] = value1 * value2

    return return_list


def sum_lists(list1: List[float], list2: List[float]) -> List[float]:
    return_list: List[float] = [0.0] * len(list1)
    for index, (value1, value2) in enumerate(zip(list1, list2)):
        return_list[index] = value1 + value2

    return return_list
