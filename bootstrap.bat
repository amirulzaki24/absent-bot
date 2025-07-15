@echo off

REM Check if Python is installed
where python >nul 2>nul
IF ERRORLEVEL 1 (
    echo "Python not installed, please install Python before retrying."
    echo "Please refer to./Python-setup.md to install Python."
    pause
    EXIT /b 1
) ELSE (
    echo Python is already installed, version info:
    python --version
)
    

REM Check if pip is installed
python -m pip --version >nul 2>nul
IF ERRORLEVEL 1 (
    echo pip not installed, starting pip installation...
    python -m ensurepip --upgrade
    IF ERRORLEVEL 1 (
        echo pip installation failed, please check the issue.
        pause
        EXIT /b 1
    )
) ELSE (
    echo pip is already installed, version info: 
    call python -m pip --version
)


REM Install project dependencies
IF EXIST "requirements.txt" (
    echo Installing project dependencies...
    python -m pip install -r requirements.txt
    IF ERRORLEVEL 1 (
        echo Dependency installation failed, please check manually.
        pause
        EXIT /b 1
    )
) ELSE (
    echo No requirements.txt file detected, skipping dependency installation.
)
    

REM Start the project
echo Starting the project...
python main.py
