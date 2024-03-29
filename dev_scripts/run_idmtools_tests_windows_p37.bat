if exist C:\idmtools_venv_37 rd /s /q C:\idmtools_venv_37
"C:\Python37\Scripts\virtualenv.exe" -p "C:\Python37\python.exe" C:\idmtools_venv_37
call "C:\idmtools_venv_37\Scripts\activate"
echo "Virtual Environment Activated"

pip install idm-buildtools --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
pymake setup-dev

echo "auto Login"
python dev_scripts/create_auth_token_args.py --comps_url %1 --username %2 --password %3

echo "start testing..."
pymake test-all

deactivate