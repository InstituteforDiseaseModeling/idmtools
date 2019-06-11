from abc import ABCMeta, abstractmethod
from typing import Any

from prettytable import ALL, PrettyTable

from idmtools.utils.collections import cut_iterable_to


class IDisplaySetting(metaclass=ABCMeta):
    """
    Base class for a display setting.
    The child class needs to implement the `display` method.

    Includes:
    - header: optional header for the display
    - field: if specified, the `get_object` will call getattr for this field on the object
    """

    def __init__(self, header: str = None, field: str = None):
        self.header = header
        self.field = field

    def get_object(self, obj: Any) -> Any:
        return getattr(obj, self.field) if self.field else obj

    @abstractmethod
    def display(self, obj: Any) -> str:
        """
        Displays the object.
        Note that the attribute (identified by self.field) should be handled with `self.get_object`
        Args:
            obj: The object to consider for display

        Returns: A string representing what to show
        """
        pass


class StringDisplaySetting(IDisplaySetting):
    """
    Displays the object as string
    """

    def display(self, obj):
        obj = self.get_object(obj)
        return str(obj)


class DictDisplaySetting(IDisplaySetting):
    """
    Displays a dictionary.
    """

    def __init__(self, header: str = None, field: str = None, max_items: int = 10, flat: bool = False):
        """
        Args:
            header: Optional field header
            field: Field in the object
            max_items: How many items displayed maximum
            flat: if False, display as a list, if True, display as a comma separated list
        """
        super().__init__(header=header, field=field)
        self.max_items = max_items
        self.flat = flat

    def display(self, obj: Any) -> str:
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
    Display the object as a table.
    """
    def __init__(self, columns, max_rows=5, field=None):
        """
        Args:
           columns: list of DisplaySettings
           max_rows: How many rows to display max
           field: Field of the object to consider
        """
        super().__init__(field=field)
        self.columns = columns
        self.max_rows = max_rows

    def display(self, obj):
        # Retrieve our object
        obj = super().get_object(obj)

        # Cut the rows
        slice, remaining = cut_iterable_to(obj, self.max_rows)

        # Create the table
        printout = PrettyTable([s.header for s in self.columns])
        printout.hrules = ALL
        for child in slice:
            printout.add_row([s.display(child) for s in self.columns])

        # If there are items remaining, display
        if remaining > 0:
            printout = str(printout)
            printout += f"\n... and {remaining} more"

        return printout
