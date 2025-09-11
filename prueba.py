
import time
import json
import requests

BASE_URL = "http://127.0.0.1:5000"

def pretty(title, obj):
    print(f"\n=== {title} ===")
    if isinstance(obj, (dict, list)):
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    else:
        print(obj)

def main():
    # 1) /test_db
    try:
        r = requests.get(f"{BASE_URL}/test_db", timeout=5)
        r.raise_for_status()
        pretty("Tablas encontradas (/test_db)", r.json())
    except Exception as e:
        pretty("Error llamando /test_db", str(e))
        return

    # 2) /agregar_json con email único
    email = f"demo_{int(time.time())}@example.com"
    payload = {"nombre": "Demo", "email": email, "password": "secreto"}
    try:
        r = requests.post(f"{BASE_URL}/agregar_json", json=payload, timeout=5)
        r.raise_for_status()
        data = r.json()
        pretty("Resultado de /agregar_json", data)
        user_id = data.get("id_usuario")
    except Exception as e:
        pretty("Error llamando /agregar_json", str(e))
        return

    # 3) /login con las mismas credenciales
    try:
        r = requests.post(f"{BASE_URL}/login", json={"email": email, "password": "secreto"}, timeout=5)
        r.raise_for_status()
        pretty("Resultado de /login", r.json())
    except Exception as e:
        pretty("Error llamando /login", str(e))

    # 4) /eliminar/<id>
    if user_id:
        # Primero intentamos DELETE; si el servidor no lo soporta en tu config, probamos GET
        try:
            r = requests.delete(f"{BASE_URL}/eliminar/{user_id}", timeout=5)
            # algunos navegadores/servidores devuelven 405, así que no forzamos raise_for_status aquí
            try:
                data = r.json()
            except Exception:
                data = r.text
            pretty("Resultado de DELETE /eliminar/<id>", data)
        except Exception as e:
            pretty("Error con DELETE /eliminar/<id>", str(e))

        # Fallback con GET (si DELETE no está habilitado)
        try:
            r = requests.get(f"{BASE_URL}/eliminar/{user_id}", timeout=5)
            r.raise_for_status()
            pretty("Resultado de GET /eliminar/<id>", r.json())
        except Exception as e:
            pretty("Error con GET /eliminar/<id>", str(e))

if __name__ == "__main__":
    main()
