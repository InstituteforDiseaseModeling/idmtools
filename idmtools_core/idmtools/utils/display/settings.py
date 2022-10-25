"""
defines views for different types if items.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from idmtools.utils.display.displays import DictDisplaySetting, StringDisplaySetting, TableDisplay

simulation_display_settings = [
    StringDisplaySetting(header="ID", field="uid"),
    DictDisplaySetting(header="Tags", field="tags", flat=False)]

experiment_display_settings = [
    StringDisplaySetting(header="ID", field="uid"),
    StringDisplaySetting(header="Simulation count", field="simulation_count")
]

experiment_table_display = [
    StringDisplaySetting(),
    TableDisplay(field="simulations", columns=simulation_display_settings)
]

suite_table_display = [
    StringDisplaySetting(),
    TableDisplay(field="experiments", columns=experiment_display_settings)
]
