branches
- aug28original: CCFES control repository, as-is
- main-p24-only: edit beginning 9/19, deleted all ccfes, only contains P24 control


## Upon startup
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass 
conda activate i24setup2 
cd ccfes-setup 
cd ccfes-setup-7-29
$env:PYTHONPATH="Y:\My Documents\GitHub\ccfes-control"

# if 'no module named examples'
$env:PYTHONPATH="Y:\Hasomed Code\HasomedSetup13\ScienceMode4Python"

# device manager from powershell - devmgmt.msc 

# check COM ports
# List all COM ports
Get-WmiObject Win32_SerialPort | Select-Object Name, DeviceID, Description


