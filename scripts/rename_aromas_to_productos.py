import os, shutil
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src = os.path.join(BASE, "app", "data", "aromas.db")
dst = os.path.join(BASE, "app", "data", "productos.db")
if not os.path.exists(src):
    print("No se encontró app/data/aromas.db (¿ya está renombrada?).")
elif os.path.exists(dst):
    print("Ya existe app/data/productos.db. No se sobreescribe.")
else:
    shutil.move(src, dst)
    print("Renombrado: aromas.db -> productos.db")
