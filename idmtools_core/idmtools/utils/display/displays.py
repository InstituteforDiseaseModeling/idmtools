"""
Tools around displays and formatting.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from abc import ABCMeta, abstractmethod
from typing import Any
from tabulate import tabulate

from idmtools.utils.collections import cut_iterable_to


class IDisplaySetting(metaclass=ABCMeta):
    """
    Base class for a display setting.

    The child class needs to implement the :meth:`display` method.

    Includes:

    - header: Optional header for the display.
    - field: If specified, the :meth:`get_object` will call :attr:`getattr` for this field on the object.
    """

    def __init__(self, header: str = None, field: str = None):
        """
        Initialize our IDisplaySetting.

        Args:
            header: Header for display
            field: Optional field to display instead of object
        """
        self.header = header
        self.field = field

    def get_object(self, obj: Any) -> Any:
        """
        Get object or field depending if field is set.

        Args:
            obj: Object to get

        Returns:
            Either obj.field or obj depending if self.field is set
        """
        return getattr(obj, self.field) if self.field else obj

    @abstractmethod
    def display(self, obj: Any) -> str:
        """
        Display the object.

        Note that the attribute (identified by self.field) should be handled with :meth:`get_object`.

        Args:
            obj: The object to consider for display.

        Returns:
            A string representing what to show.
        """
        pass


class StringDisplaySetting(IDisplaySetting):
    """
    Class that displays the object as string.
    """

    def display(self, obj):
        """
        Display object.

        Args:
            obj: Object to display

        Returns:
            String of object
        """
        obj = self.get_object(obj)
        return str(obj)


class DictDisplaySetting(IDisplaySetting):
    """
    Class that displays a dictionary.
    """

    def __init__(self, header: str = None, field: str = None, max_items: int = 10, flat: bool = False):
        """
        DictDisplay.

        Args:
            header: Optional field header.
            field: The field in the object to consider.
            max_items: The maximum number of items to display.
            flat: If False, display as a list; if True, display as a comma-separated list.
        """
        super().__init__(header=header, field=field)
        self.max_items = max_items
        self.flat = flat

    def display(self, obj: Any) -> str:
        """
        Display a dictionary.

        Args:
            obj: Object to display

        Returns:
            String display of object
        """
        # Retrieve our object
        obj = self.get_object(obj)

        # Slice the dictionary depending on the `max_items`
        slice, remaining = cut_iterable_to(obj, self.max_items)
        printout = ""

        # Different display depending on `flat`
        if self.flat:
            printout = ", ".join(f"{k}:{v}" for k, v in slice.items())
        else:
            for k, v in slice.items():
                printout += f"- {k}:{v}\n"
            printout = printout.strip()

        # If there are items remaining, display
        if remaining > 0:
            printout = str(printout)
            printout += f"\n... and {remaining} more"

        return printout


class TableDisplay(IDisplaySetting):
    """
    Class that displays the object as a table.
    """

    def __init__(self, columns, max_rows=5, field=None):
        """
        Initialize our TableDisplay.

        Args:
           columns: A list of display settings.
           max_rows: The maximum number of rows to display.
           field: The field of the object to consider.
        """
        super().__init__(field=field)
        self.columns = columns
        self.max_rows = max_rows

    def display(self, obj) -> str:
        """
        Display our object as a table.

        Args:
            obj: Object to display

        Returns:
            Table represented as a string of the object
        """
        # Retrieve our object
        obj = super().get_object(obj)

        # Cut the rows
        slice, remaining = cut_iterable_to(obj, self.max_rows)

        # Create the table
        rows = []
        for child in slice:
            rows.append([s.display(child) for s in self.columns])

        printout = tabulate(rows, headers=[s.header for s in self.columns], tablefmt='psql', showindex=False)

        # If there are items remaining, display
        if remaining > 0:
            printout = str(printout)
            printout += f"\n... and {remaining} more"

        return printout
