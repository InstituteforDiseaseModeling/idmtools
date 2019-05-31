class CommandLine:
    """
    A class to construct command line strings from executable, options, and params
    """

    def __init__(self, executable, *args, **kwargs):
        self._executable = executable
        self._options = kwargs or {}
        self._args = args or []

    @property
    def executable(self):
        return self._executable

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