#!/usr/bin/env python3
"""Construit Rosé OS pour les TV Samsung (Tizen) : RoseOS-tizen.wgt.

    python3 tizen/build.py                 # -> RoseOS-tizen.wgt, pas encore signé
    python3 tizen/build.py --sign PROFIL   # signé avec un profil de certificat des outils Tizen de Samsung
    python3 tizen/build.py --preview       # laisse aussi les fichiers dans out/tizen/ pour les ouvrir dans un navigateur

Les TV n'installent que des paquets signés : --sign utilise `tizen package` (Tizen Studio) avec un profil créé là-bas.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import webapp  # noqa: E402

OUT = os.path.join(ROOT, 'out', 'tizen')
WGT = os.path.join(ROOT, 'RoseOS-tizen.wgt')


def tizen_cli():
    """La commande `tizen` de Samsung (Tizen Studio), ou None."""
    name = 'tizen.bat' if os.name == 'nt' else 'tizen'
    home = os.path.expanduser('~')
    for base in (os.environ.get('TIZEN_STUDIO', ''), os.path.join(home, 'tizen-studio'),
                 os.path.join(home, 'tizen-sdk'), 'C:\\tizen-studio'):
        path = os.path.join(base, 'tools', 'ide', 'bin', name)
        if base and os.path.exists(path):
            return path
    return shutil.which('tizen')


def sign(profile):
    cli = tizen_cli()
    if not cli:
        sys.exit("La signature demande les outils Tizen de Samsung (Tizen Studio). Introuvables : "
                 "définis TIZEN_STUDIO là où ils sont installés.")
    out = tempfile.mkdtemp()
    try:
        run = subprocess.run([cli, 'package', '-t', 'wgt', '-s', profile, '-o', out, '--', WGT],
                             capture_output=True, text=True)
        made = [n for n in os.listdir(out) if n.endswith('.wgt')]
        if run.returncode != 0 or not made:
            sys.exit("`tizen package` n'a pas signé le paquet :\n" + (run.stdout + run.stderr).strip())
        shutil.move(os.path.join(out, made[0]), WGT)
    finally:
        shutil.rmtree(out, ignore_errors=True)
    with zipfile.ZipFile(WGT) as z:
        names = z.namelist()
    if 'author-signature.xml' not in names or 'signature1.xml' not in names:
        sys.exit('Le paquet est revenu sans ses signatures.')


def build(preview, profile):
    with open(os.path.join(ROOT, 'tizen', 'config.xml'), encoding='utf-8') as f:
        manifest = f.read()
    app_id = re.search(r'<tizen:application id="([^"]+)"', manifest).group(1)
    version = re.search(r'<widget [^>]*version="([^"]+)"', manifest).group(1)
    app = webapp.files()
    for name in ('config.xml', 'icon.png'):
        with open(os.path.join(ROOT, 'tizen', name), 'rb') as f:
            app[name] = f.read()

    with zipfile.ZipFile(WGT, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(app):
            z.writestr(path, app[path])
    if profile:
        sign(profile)

    if preview:
        webapp.preview(app, OUT)
        print('Aperçu : ouvre out/tizen/index.html dans un navigateur.')
    print('Built %s (%s %s, %d KB, %s)' % (os.path.basename(WGT), app_id, version, os.path.getsize(WGT) // 1024,
                                           'signé avec "%s"' % profile if profile else 'non signé'))


if __name__ == '__main__':
    args = sys.argv[1:]
    build('--preview' in args, args[args.index('--sign') + 1] if '--sign' in args else None)
