if exist C:\idmtools_venv_37 rd /s /q C:\idmtools_venv_37
"C:\Program Files\Python37\Scripts\virtualenv.exe" -p "C:\Program Files\Python37\python.exe" C:\idmtools_venv_37
call "C:\idmtools_venv_37\Scripts\activate"
echo "Virtual Environment Activated"

if exist data\redis-data rd /s /q data\redis-data
mkdir data\redis-data
echo "install idmtools ..."
pip install -e idmtools_core.[test] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
pip install -e idmtools_local_runner[test]
pip install -e idmtools_models_collection[test]

echo "start services..."
cd idmtools_local_runner
docker-compose down -v
docker-compose build
docker-compose up -d

echo "start testing..."
cd ..
python idmtools_core\tests\create_auth_token_args.py --comps_url %1 --username %2 --password %3
REM python idmtools_core\tests\create_auth_token_args.py --comps_url https://comps2.idmod.org --username shchen --password Password123

cd idmtools_core\tests\
python run_tests.py

deactivate