import os
import subprocess


cwd = os.path.dirname(__file__)


def main() -> None:
    for fn in os.listdir(cwd):
        f_ext = fn.split('.')[-1].lower()
        if not f_ext == 'ui':
            continue
        # fp = os.path.join(cwd, fn)
        fp = fn
        out_fp = os.path.join(cwd, fn[:-len(f_ext) - 1] + '_ui.py')
        subprocess.call([
            'pyuic5',
            fp,
            '-o',
            out_fp
        ])


if __name__ == '__main__':
    main()
