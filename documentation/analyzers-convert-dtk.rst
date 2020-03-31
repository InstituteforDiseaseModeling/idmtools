=====================
|DT| example analyzer
=====================

The following |DT| example performs analysis on simulation ouput data in InsetChart.json and plots the results using the Matplotlib plotting libary::

        from simtools.Analysis.BaseAnalyzers import BaseAnalyzer
        from simtools.Analysis.AnalyzeManager import AnalyzeManager


        class PopulationAnalyzer(BaseAnalyzer):
            def __init__(self):
                super().__init__(filenames=['output\\InsetChart.json'])

            def select_simulation_data(self, data, simulation):
                return data[self.filenames[0]]["Channels"]["Statistical Population"]["Data"]

            def finalize(self, all_data):
                import matplotlib.pyplot as plt
                for pop in list(all_data.values()):
                    plt.plot(pop)
                plt.legend([s.id for s in all_data.keys()])
                plt.show()


        if __name__ == "__main__":
            am = AnalyzeManager('latest', analyzers=PopulationAnalyzer())
            am.analyze()