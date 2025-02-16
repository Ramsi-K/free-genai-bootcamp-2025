@echo off
echo Checking MSYS2 installation...

if not exist C:\msys64\usr\bin\pacman.exe (
    echo MSYS2 is not installed!
    echo Please download and install MSYS2 from https://www.msys2.org/
    echo After installation, run this script again.
    exit /b 1
)

echo Updating MSYS2 packages...
C:\msys64\usr\bin\pacman.exe -Syu --noconfirm

echo Installing required packages...
C:\msys64\usr\bin\pacman.exe -S --noconfirm mingw-w64-x86_64-gcc make

echo Adding MinGW-w64 to PATH...
setx PATH "%PATH%;C:\msys64\mingw64\bin" /M

echo Setup complete! Please restart your terminal and run:
echo make setup 