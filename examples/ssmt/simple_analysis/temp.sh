export PYTHONPATH=$(pwd)/Assets/site-packages:$(pwd)/Assets/:$PYTHONPATH

pip install Assets/idmtools-1.5.0+nightly.tar.gz --force --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
pip install Assets/idmtools_platform_comps-1.5.0+nightly.tar.gz --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple

$*