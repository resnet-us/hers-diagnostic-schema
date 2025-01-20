from hers_diagnostic_output import HERSDiagnosticData
from pathlib import Path
from dimes import LinesOnly, DimensionalPlot, DisplayData
from datetime import datetime, timedelta
import plotly
from enum import Enum
from dataclasses import dataclass

color_palette = plotly.colors.qualitative.Set1


directory_path = Path("examples")
# file_paths = [file for file in directory_path.iterdir()]  # add if statement

files = [
    "base",
    "base-hvac-multiple",
    "base-hvac-air-to-air-heat-pump-1-speed",
]

file_paths = [Path(directory_path, f"{file}.json") for file in files]


def sum_lists(list1, list2):

    sum_list = []

    for value1, value2 in zip(list1, list2):

        sum_list.append(value1 + value2)

    return sum_list


class TimeFrequency(Enum):
    day = "Daily"
    hour = "Hourly"


@dataclass
class DateData:
    start_date: datetime
    end_date: datetime
    frequency: TimeFrequency


year = 2025

date_data_dict = [
    DateData(
        datetime(year, 1, 1, 0),
        datetime(year, 12, 31, 0),
        TimeFrequency.day,
    ),
    DateData(
        datetime(year, 7, 23, 0),
        datetime(year, 8, 9, 0),
        TimeFrequency.day,
    ),
    DateData(
        datetime(year, 1, 1, 0),
        datetime(year, 12, 31, 0),
        TimeFrequency.hour,
    ),
    DateData(
        datetime(year, 8, 3, 0),
        datetime(year, 8, 9, 0),
        TimeFrequency.hour,
    ),
]

january_1 = datetime(year, 1, 1, 0)

for plot_index, date_data in enumerate(date_data_dict):
    start_date = date_data.start_date
    end_date = date_data.end_date
    beginning_of_time = start_date - january_1
    time_frequency = date_data.frequency
    time_difference = end_date - start_date
    if time_frequency == TimeFrequency.day:
        number_of_days = time_difference.days + 1
        time = [start_date + timedelta(days=day) for day in range(number_of_days)]
        start_data_index = beginning_of_time.days
    else:
        number_of_hours = int(
            (time_difference.days * 24 + time_difference.seconds / 3600) + 1
        )
        time = [start_date + timedelta(hours=hour) for hour in range(number_of_hours)]
        start_data_index = int(
            (beginning_of_time.days * 24 + beginning_of_time.seconds / 3600) + 1
        )
    end_data_index = start_data_index + len(time)
    # if (start_date == datetime(year, 1, 1)) & (end_date == datetime(year, 12, 31)):
    #     subtitle = "Entire Year"
    # else:
    #     subtitle = f"""{start_date.strftime("%b %d")} - {end_date.strftime("%b %d")}"""
    plot = DimensionalPlot(
        time,
        title=f"OS-ERI<br>{time_frequency.value} Cooling System Energy Consumption<br>Denver, CO",
    )

    for color_index, file_path in enumerate(file_paths):
        name = " ".join(
            [
                (
                    sub_string.upper()
                    if sub_string.lower() == "hvac"
                    else sub_string.capitalize()
                )
                for sub_string in file_path.name.replace(".json", "").split("-")
            ]
        )
        color = color_palette[color_index]
        data = HERSDiagnosticData(file_path)
        cooling_data_hourly = [0] * 8760
        for system in data.data["rated_home_output"]["space_cooling_system_output"]:
            for index in system["energy_use"]:
                cooling_data_hourly = sum_lists(index["energy"], cooling_data_hourly)

        if time_frequency == TimeFrequency.day:
            cooling_data_daily = []
            for start_hour, end_hour in zip(range(0, 8760, 24), range(24, 8784, 24)):
                single_day_data = sum(cooling_data_hourly[start_hour:end_hour])
                cooling_data_daily.append(single_day_data)
            y_axis_data = cooling_data_daily[start_data_index:end_data_index]
        else:
            y_axis_data = cooling_data_hourly[start_data_index:end_data_index]

        plot.add_display_data(
            DisplayData(
                y_axis_data,
                line_properties=LinesOnly(
                    color=color,
                ),
                name=name,
                native_units="kBtu",
                y_axis_name="Energy Consumption",
            )
        )
    plot.write_html_plot(Path(f"test_{plot_index}.html"))
    plot.write_image_plot(Path(f"test_{plot_index}.jpeg"), scale=2, width=1, height=1)
