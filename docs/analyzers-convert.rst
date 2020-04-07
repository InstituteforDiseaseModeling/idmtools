=====================================
Convert analyzers from |DT| to |IT_s|
=====================================

Although the use of analyzers in |DT| and |IT_s| is very similar, being aware of some of the differences may be helpful with the conversion process. For example some of the class and method names are different, as seen in the following diagram:

@startuml
note top of BaseAnalyzer
  <b>DTK-Tools</b>
end note
class BaseAnalyzer {
    initialize()
    per_experiment()
    filter()
    select_simulation_data()
    finalize()
    destroy()
    }
note top of IAnalyzer
  <b>IDM-Tools</b>
end note
class IAnalyzer {
    initialize()
    per_group()
    filter()
    map()
    reduce()
    destroy()
    }
IAnalyzer -left[hidden]-> BaseAnalyzer
@enduml

For additional information about the *IAnalyzer* class and methods, see :py:class:`~idmtools.entities.ianalyzer.IAnalyzer`.

In addition, you can also an example of a .csv analyzer created in |DT| and how it was converted to |IT_s|. Other than the class name and some method names changing the core code is almost the same. The primary differences can be seen in the class import statements and the execution of the analysis within the *if __name__ == '__main__':* block of code.

.. toctree::

   analyzers-convert-dtk
   analyzers-convert-idmt   