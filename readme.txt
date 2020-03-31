Steps to install.  Clone repository from GitHub, from command prompt git clone
git@github.com:bbeens/Easy_Wire_test_runner.git or use the link to download a .zip
https://github.com/bbeens/Easy_Wire_test_runner/archive/master.zip   From command line create virtual env with
'python -m venv venv'.  Activate the venv with 'venv\Scripts\Activate.bat'.  Once the virtual env is active run
'pip install -r requirements.txt'.

Basic use case.  From a python prompt you can from Easy_Wire_test_runner import EasyWire.  Instantiate a new EasyWire
object, then call the methods test_lv_only() or test_lv_hv().  Note I changed the default test Category names.  You may
need to edit to work in your env.