rmdir /Q /S build
rmdir /Q /S dist
pyi-makespec.exe -F .\hash_all_files.py --path C:\Windows\System32\downlevel 
pyinstaller --path C:\Windows\System32\downlevel  .\hash_all_files.spec