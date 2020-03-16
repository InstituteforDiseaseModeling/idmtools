import builtins as __builtin__  # import __builtin__

try:
    # Check for @profile decorator from line_profiler package
    __builtin__.profile
except AttributeError:
    # No line_profiler; provide no-op pass-through function
    def profile(func): return func
    __builtin__.profile = profile


__all__ = ['analysis', 'demog', 'event', 'model', 'report', 'snp']
