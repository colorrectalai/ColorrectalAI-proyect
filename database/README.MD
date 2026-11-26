# Base de datos de ColorrectalAI (PostgreSQL)

La base guarda el registro operacional anónimo de la API (una fila por solicitud, sin imágenes), el
catálogo de experimentos y modelos, y las cuentas de usuario de la interfaz web (contraseña con hash
scrypt, nunca en texto plano). Es opcional: sin `DATABASE_URL` la API funciona igual, pero no guarda
registros y el registro e inicio de sesión responden `503 BASE_NO_DISPONIBLE`.

## Contenido

| Archivo | Qué hace |
|---|---|
| `backend/db/01_esquema.sql` | 18 tablas, índices y 4 vistas de consulta. Idempotente (`IF NOT EXISTS`). |
| `backend/db/02_datos_iniciales.sql` | Catálogo de errores, clase `polipo`, métricas, centros de PolypGen, partición por centro y el experimento baseline con sus métricas reales (`entrenamiento/registro_experimento.json`). Idempotente. |

Los archivos están dentro de `backend/` para que entren en la imagen Docker del servicio.

## Cómo se crea

**No hay que ejecutar nada a mano.** Al arrancar, la API (`api/db.py`, función `preparar`):

1. aplica `01_esquema.sql` y `02_datos_iniciales.sql` dentro de una transacción con bloqueo, y
2. registra en `version_modelo` el modelo que cargó, identificado por el SHA-256 de sus pesos, como
   `activo`; el modelo activo anterior pasa a `retirado`.

El resultado se ve en `GET /api/v1/salud` → `"base_datos": "conectada"`. Si la base falla, la API
sigue respondiendo y solo deja el aviso en el log.

También se pueden aplicar a mano (por ejemplo en pgAdmin o con `psql -f`), en el mismo orden.

## Configuración

### Local

1. Crear la base: `CREATE DATABASE colorrectalai;`
2. En `backend/.env`:
   ```env
   DATABASE_URL=postgresql+psycopg://postgres:TU_CLAVE@localhost:5432/colorrectalai
   TOKEN_SECRETO=un-valor-largo-y-aleatorio
   ```
3. Arrancar la API: `uvicorn api.main:app --reload`.

El nombre de la base distingue mayúsculas. **Nunca** subir el `.env` al repositorio.

### Railway (producción)

1. En el proyecto de Railway: **+ New → Database → PostgreSQL**.
2. En el servicio de la API, pestaña **Variables**:
   - `DATABASE_URL` = `${{Postgres.DATABASE_URL}}` (referencia a la base, no copiar la clave).
   - `TOKEN_SECRETO` = valor largo y aleatorio (por ejemplo `python -c "import secrets;print(secrets.token_urlsafe(48))"`).
3. Redesplegar la API y comprobar `/api/v1/salud`.

## Usuarios (DEF-11)

| Endpoint | Uso |
|---|---|
| `POST /api/v1/usuarios` | Crea la cuenta (`nombre`, `correo`, `contrasena` ≥ 8, `acepta_aviso`) y devuelve la sesión. 409 si el correo ya existe. |
| `POST /api/v1/sesiones` | Inicia sesión. 401 `CREDENCIALES_INVALIDAS` si el correo o la contraseña no coinciden. |
| `GET /api/v1/usuarios/yo` | Datos del usuario con `Authorization: Bearer <token>`. |

El token se firma con HMAC-SHA256 usando `TOKEN_SECRETO` y vence a las `TOKEN_HORAS` horas (8 por
defecto). El navegador guarda solo el token, el nombre y el correo.

## Pruebas

```bash
TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/colorrectalai_test pytest
```

Las pruebas de `tests/test_usuarios_bd.py` borran y recrean el esquema de esa base, así que debe ser
una base solo de pruebas. Sin `TEST_DATABASE_URL` se saltan; el CI las ejecuta con un PostgreSQL 16.

## Pendiente

- **Roles de acceso** (API / investigador / consulta): requieren contraseñas definidas por el equipo.
- **Purga automática a 90 días** del registro operacional (por ejemplo con `pg_cron`).
- **Recuperación de contraseña**: el enlace de la pantalla de acceso aún no tiene flujo propio.
