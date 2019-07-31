"idmtools_core" "idmtools_platform_local" "idmtools_platform_comps" "idmtools_models_collection"
set sources[0]="idmtools_core"
set sources[1]="idmtools_cli"
set sources[2]="idmtools_platform_local"
set sources[3]="idmtools_platform_comps"
set sources[4]="idmtools_models_collection"
set sources[5]="idmtools_test"

for /F "tokens=2 delims==" %%s in ('set sources[') do cd %%s && pip install -e .[test] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple