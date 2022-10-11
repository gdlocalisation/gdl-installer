import os
import sys
import subprocess


def main(argv: list) -> int:
    cwd = os.path.dirname(__file__) or os.getcwd()
    os.chdir(cwd)
    main_path = os.path.join(cwd, 'main.py')
    files_dir = os.path.join(cwd, 'files')
    icon_path = os.path.join(files_dir, 'gdl_icon.ico')
    exe_out_path = os.path.join(cwd, 'dist', 'main.exe')
    exe_path = os.path.join(cwd, 'dist', 'GDL_Installer.exe')
    result = subprocess.call([
        'pyinstaller',
        '--onefile',
        '--uac-admin',
        '--add-data',
        'files;files',
        '-w',
        '-i',
        icon_path,
        main_path
    ] + argv)
    if result:
        print('build failed')
        return result
    if not os.path.isfile(exe_out_path):
        print('could not find output')
        return 1
    os.rename(exe_out_path, exe_path)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
