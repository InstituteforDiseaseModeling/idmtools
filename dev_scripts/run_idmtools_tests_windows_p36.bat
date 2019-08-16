if exist C:\idmtools_venv_36 rd /s /q C:\idmtools_venv_36
"C:\Python36\Scripts\virtualenv.exe" -p C:\Python36\python.exe C:\idmtools_venv_36
call "C:\idmtools_venv_36\Scripts\activate"
echo "Virtual Environment Activated"

python dev_scripts/bootstrap.py

echo "auto Login"
python dev_scripts/create_auth_token_args.py --comps_url %1 --username %2 --password %3

echo "start testing..."
pymake test-all

deactivate