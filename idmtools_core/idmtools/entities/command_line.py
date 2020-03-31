from typing import TypeVar, Dict, Any, List
from dataclasses import dataclass, field


@dataclass(init=False)
class CommandLine:
    _executable: str = None
    _options: Dict[str, Any] = field(default_factory=dict)
    _args: List[Any] = field(default_factory=list)

    """
    A class to construct command line strings from executable, options, and params
    """

    def __init__(self, executable=None, *args, **kwargs):
        self._executable = executable
        self._options = kwargs or {}
        self._args = args or []

    @property
    def executable(self):
        return self._executable

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

        return ' '.join(options)

    @property
    def arguments(self):
        return ' '.join(self._args)

    @property
    def cmd(self):
        return ' '.join(filter(None, [self.executable, self.options, self.arguments]))

    def __str__(self):
        return self.cmd


TCommandLine = TypeVar("TCommandLine", bound=CommandLine)
