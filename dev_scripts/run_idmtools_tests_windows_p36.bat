if exist C:\idmtools_venv_36 rd /s /q C:\idmtools_venv_36
"C:\Python36\Scripts\virtualenv.exe" -p C:\Python36\python.exe C:\idmtools_venv_36
call "C:\idmtools_venv_36\Scripts\activate"
echo "Virtual Environment Activated"

if exist data\redis-data rd /s /q data\redis-data
mkdir data\redis-data
echo "install idmtools ..."
python dev_scripts/bootstrap.py

echo "start services..."
docker network create idmtools_network  nul 2> nul
"C:\Program Files\Docker\Docker\Resources\bin\docker-compose.exe" down -v
"C:\Program Files\Docker\Docker\Resources\bin\docker-compose.exe" build
"C:\Program Files\Docker\Docker\Resources\bin\docker-compose.exe" up -d

echo "start testing..."
python idmtools_platform_comps\tests\create_auth_token_args.py --comps_url %1 --username %2 --password %3

cd idmtools_core\tests\
python run_tests.py

deactivate