# Login Flask + MySQL (`desarrollo_web`)

- Guarda usuarios en la tabla `desarrollo_web.usuarios` con **password hasheado**.
- Si no existe la BD o la tabla, se crean automáticamente.
- Se crea el usuario **admin/admin** si no existe.

## Pasos
```bash
python -m venv venv
# Windows
.env\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
# (opcional) copia .env.example a .env y ajusta credenciales
python run.py
```
Abre: http://127.0.0.1:5000

## SQL útil
```sql
DESCRIBE usuarios;
SELECT id, usuario, rol, LEFT(password, 25) AS hash_muestra FROM usuarios ORDER BY id DESC LIMIT 10;
```