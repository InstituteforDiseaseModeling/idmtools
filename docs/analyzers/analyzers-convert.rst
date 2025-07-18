===========================
Convert analyzers from |DT|
===========================

Although the use of analyzers in |DT| and |IT_s| is very similar, being aware of
some of the differences may be helpful with the conversion process. For example
some of the class and method names are different, as seen in the following diagram:

.. image:: /diagrams/analyzers-convert.png
   :alt: Analyzers Convert
   :align: center

As the previous diagram illustrates the |DT| methods, :py:func:`select_simulation_data`
and :py:func:`finalize`, have been renamed to :py:func:`map`
and :py:func:`reduce` in |IT_s|; however, the parameters are the same::

    select_simulation_data(self,data,simulation)
    map(self,data,simulation)

    finalize(self,all_data)
    reduce(self,all_data)

For additional information about the *IAnalyzer* class and methods,
see :py:class:`~idmtools.entities.ianalyzer.IAnalyzer`.

In addition, you can also see an example of a .csv analyzer created in |DT| and how
it was converted to |IT_s|. Other than the class name and some method names
changing the core code is almost the same. The primary differences can be
seen in the class import statements and the execution of the analysis within
the *if __name__ == '__main__':* block of code.

.. toctree::

   analyzers-convert-dtk
   analyzers-convert-idmt