import os
os.system("pyinstaller -F main.py")
os.rename("dist/main.exe", "dist/UIGF_Upgrader.exe")