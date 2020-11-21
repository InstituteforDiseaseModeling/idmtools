===========================
Frequently asked questions
===========================


Why receiving error: "ImportError: DLL load failed: The specified module could not be found."?
    This error can be caused when using Microsoft Visual C++ runtime version 14.0.24151.1 and running analyzers, such as test_ssmt_platforanalysis.py. Workarounds are to either use ``pip install msvc-runtime`` to install latest Microsoft Visual C++ runtime version or to install latest Microsoft Build Tools.