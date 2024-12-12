build_name="./build"
dist_path="./dist"
app_name="TextureUnpacker"
pyinstaller --workpath=${build_name} \
--distpath=${dist_path} \
--name=${app_name} \
--additional-hooks-dir=. \
--onefile --windowed app/main.py