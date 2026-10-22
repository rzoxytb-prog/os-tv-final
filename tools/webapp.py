"""Ce que les paquets LG (webos/build.py) et Samsung (tizen/build.py) ont en commun : les fichiers de l'interface web."""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def files():
    """Les fichiers de web/ : {chemin dans l'appli: octets}."""
    out = {}
    web = os.path.join(ROOT, 'web')
    for base, _dirs, names in os.walk(web):
        for name in sorted(names):
            path = os.path.join(base, name)
            with open(path, 'rb') as f:
                out[os.path.relpath(path, web).replace(os.sep, '/')] = f.read()
    return out


def preview(app, out_dir):
    """Laisse les fichiers dans out_dir pour ouvrir index.html dans un navigateur."""
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    for path, content in app.items():
        target = os.path.join(out_dir, path)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, 'wb') as f:
            f.write(content)
