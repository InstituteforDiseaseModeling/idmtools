if exist C:\idmtools_venv_37 rd /s /q C:\idmtools_venv_37
"C:\Python37\Scripts\virtualenv.exe" -p "C:\Python37\python.exe" C:\idmtools_venv_37
call "C:\idmtools_venv_37\Scripts\activate"
echo "Virtual Environment Activated"

if exist data\redis-data rd /s /q data\redis-data
mkdir data\redis-data
echo "install idmtools ..."
python dev_scripts/bootstrap.py

echo "start testing..."
python idmtools_core\tests\create_auth_token_args.py --comps_url %1 --username %2 --password %3
REM python idmtools_core\tests\create_auth_token_args.py --comps_url https://comps2.idmod.org --username shchen --password Password123

cd idmtools_core\tests\
python run_tests.py

deactivate