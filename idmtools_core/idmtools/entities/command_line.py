import shlex
from typing import TypeVar, Dict, Any, List
from dataclasses import dataclass, field


@dataclass(init=False)
class CommandLine:
    """
        A class to construct command line strings from executable, options, and params
        """
    #: The executable portion of the command
    _executable: str = None
    #: Options for the command
    _options: Dict[str, Any] = field(default_factory=dict)
    #: Arguments for the command
    _args: List[Any] = field(default_factory=list)
    # Use shlex to format output
    format_output: bool = field(default=True)

    def __init__(self, executable=None, *args, **kwargs):
        # If there is a space in executable, we probably need to split it
        self._executable = executable
        self._options = kwargs or {}
        self._args = list(args) or []

    @property
    def executable(self) -> str:
        return self._executable

    @executable.setter
    def executable(self, executable):
        self._executable = executable

    def add_argument(self, arg):
        self._args.append(arg)

    def add_option(self, option, value):
        self._options[option] = value

    @property
    def options(self):
        options = []
        for k, v in self._options.items():
            # Handles spaces
            value = '"%s"' % v if ' ' in str(v) else str(v)
            if k[-1] == ':':
                options.append(k + value)  # if the option ends in ':', don't insert a space
            else:
                options.extend([k, value])  # otherwise let join (below) add a space

        return ' '.join([shlex.quote(s) for s in options if s])

    @property
    def arguments(self):
        return ' '.join([shlex.quote(s) for s in self._args if s]).strip()

    @property
    def cmd(self):
        return ' '.join([self._executable, self.options, self.arguments]).strip()

    def __str__(self):
        return self.cmd

    @staticmethod
    def from_string(command: str, format_output: bool = True) -> 'CommandLine':
        """
        Creates a command line object from string

        Args:
            command: Command
            format_output: Should we use shlex to format the command line on render?

        Returns:
            CommandLine object from string
        """
        parts = shlex.split(command.replace("\\", "/"))
        arguments = parts[1:] if len(parts) > 1else []
        cl = CommandLine(parts[0], *arguments)
        return cl


TCommandLine = TypeVar("TCommandLine", bound=CommandLine)
