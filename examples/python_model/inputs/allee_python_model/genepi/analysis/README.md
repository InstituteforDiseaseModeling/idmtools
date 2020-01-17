Some example analysis of genepi model output.

#### Details

* Plotting population-level timeseries, e.g. number of infections, may be found in [`population.py`](https://github.com/edwenger/genepi/blob/master/genepi/analysis/population.py).
* Linked-genome transmission metrics are plotted in [`transmission.py`](https://github.com/edwenger/genepi/blob/master/genepi/analysis/transmission.py), including the calculation of repeated genome occurences.
* Analyses of genome relatedness are done in [`genome.py`](https://github.com/edwenger/genepi/blob/master/genepi/analysis/genome.py).

#### Dependencies

Processing and plotting use the [`seaborn`](https://pypi.python.org/pypi/seaborn), [`pandas`](https://pypi.python.org/pypi/pandas), and [`networkx`](https://pypi.python.org/pypi/networkx) packages.

Pairwise IBD segments and genome clustering are available by calling out to the [`GERMLINE`](http://www.cs.columbia.edu/~gusev/germline/) and [`DASH`](http://www.cs.columbia.edu/~gusev/dash/) executables, respectively, which are available for download from the above links and may be copied to and run from the `bin` subdirectory of this `analysis` directory.
