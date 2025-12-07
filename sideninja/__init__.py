
import os
import xml.etree.ElementTree as ET
import argparse
import shutil

PYSIDE2, PYQT5, PYSIDE6, PYQT6 = range(4)

def get_class(path):
    tree = ET.parse(path)
    root = tree.getroot()
    item = root.find('class')
    return item.text

def replace_ext(path, ext):
    return os.path.splitext(path)[0] + ext

def generate_build_file(cwd, flavour):

    if flavour == PYQT5:
        uic_exe = 'pyuic5'
        rcc_exe = 'pyrcc5'
    elif flavour == PYSIDE2:
        uic_exe = 'pyside2-uic'
        rcc_exe = 'pyside2-rcc'
    elif flavour == PYSIDE6:
        uic_exe = 'pyside6-uic'
        rcc_exe = 'pyside6-rcc'
    elif flavour == PYQT6:
        uic_exe = 'pyuic6'
        rcc_exe = 'pyrcc6'

    RULES = f"""rule uic
    command = {uic_exe} $in -o $out
rule rcc
    command = {rcc_exe} $in -o $out
"""
    with open(os.path.join(cwd, 'build.ninja'), 'w', encoding='utf-8') as file:
        print(RULES, file=file)
        for root, dirs, files in os.walk(cwd):
            for f in files:
                _, ext = os.path.splitext(f)
                if ext == '.ui':
                    p = os.path.join(root, f)
                    c = get_class(p)
                    src = os.path.relpath(p, cwd)
                    dst = os.path.relpath(os.path.join(root, "Ui_{}.py".format(c)))
                    print("build {}: uic {}".format(dst, src), file=file)
                elif ext == '.qrc':
                    p = os.path.join(root, f)
                    src = os.path.relpath(p, cwd)
                    dst = replace_ext(src, '.py')
                    print("build {}: rcc {}".format(dst, src), file=file)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pyside2", action='store_true')
    parser.add_argument("--pyqt5", action='store_true')
    parser.add_argument("--pyside6", action='store_true')
    parser.add_argument("--pyqt6", action='store_true')

    args = parser.parse_args()
    if args.pyside2 or args.pyqt5 or args.pyside6 or args.pyqt6:
        if args.pyside2:
            flavour = PYSIDE2
        elif args.pyqt5:
            flavour = PYQT5
        elif args.pyside6:
            flavour = PYSIDE6
        elif args.pyqt6:
            flavour = PYQT6
    else:
        pyuic5 = shutil.which('pyuic5')
        pyuic6 = shutil.which('pyuic6')
        pyside6_uic = shutil.which('pyside6-uic')
        pyside2_uic = shutil.which('pyside2-uic')
        if pyside6_uic:
            flavour = PYSIDE6
        elif pyuic6:
            flavour = PYQT6
        elif pyside2_uic:
            flavour = PYSIDE2
        elif pyuic5:
            flavour = PYQT5
        else:
            flavour = PYSIDE6

    cwd = os.getcwd()
    generate_build_file(cwd, flavour)