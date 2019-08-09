if exist C:\idmtools_venv_36 rd /s /q C:\idmtools_venv_36
"C:\Python36\Scripts\virtualenv.exe" -p C:\Python36\python.exe C:\idmtools_venv_36
call "C:\idmtools_venv_36\Scripts\activate"
echo "Virtual Environment Activated"

if exist data\redis-data rd /s /q data\redis-data
mkdir data\redis-data
echo "install idmtools ..."
pip install -e idmtools_core.[test,3.6] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
pip install -e idmtools_local_runner[test]
pip install -e idmtools_models[test]

echo "start services..."
cd idmtools_local_runner
docker network create idmtools_network  nul 2> nul
docker-compose down -v
docker-compose build
docker-compose up -d

echo "start testing..."
cd ..
python idmtools_core\tests\create_auth_token_args.py --comps_url %1 --username %2 --password %3

cd idmtools_core\tests\
python run_tests.py

deactivate