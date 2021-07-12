===========================
Frequently asked questions
===========================

As you get started with |IT_s|, you may have questions. The most common
questions are answered below. If you are using |IT_s| with |EMODPY_s|
packages, see the FAQs from those packages for additional guidance.


Why am I receiving the error: "ImportError: DLL load failed: The specified module could not be found."?
   This error can be caused when using Microsoft Visual C++ runtime version
   14.0.24151.1 and running analyzers, such as test_ssmt_platforanalysis.py.
   Workarounds are to either use ``pip install msvc-runtime`` to install the
   latest Microsoft Visual C++ runtime version or to install the latest Microsoft
   Build Tools.

Why am I getting an "ImportError: cannot import name 'NoReturn'" error when importing |IT_s|?
   Because you have a version of Python that is less than |Python_supp|
   installed somewhere and you are running with that, perhaps accidentally.

How do I specify the number of cores? 

   You can specify the **num_cores** parameter in :py:class:`~idmtools_platform_comps.comps_platform.COMPSPlatform`.
   It is not an |EMOD_s| configuration parameter.
