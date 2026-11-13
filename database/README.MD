   ```
   O en **pgAdmin**: abrir la base `colorrectalai` → *Query Tool* → abrir `schema.sql` → ejecutar.
4. Comprobar que se creó todo (deben aparecer 17 tablas):
   ```sql
   SELECT table_name FROM information_schema.tables
   WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
   ORDER BY table_name;
   ```

## Conectar la API

En `backend/.env` agregar la variable `DATABASE_URL`:

```env
DATABASE_URL=postgresql+psycopg://postgres:TU_CLAVE@localhost:5432/colorrectalai
```

- El nombre de la base **distingue mayúsculas**: debe coincidir con el que se creó.
- **Nunca** subir el archivo `.env` al repositorio (ya está en `.gitignore`).
- En producción (Render), `DATABASE_URL` se define como variable de entorno secreta del servicio.

## Pendiente

- **Datos iniciales (`seed.sql`)**: la API busca en la base los códigos de error, la clase
  detectada y la versión del modelo (por su SHA-256). Mientras no existan esos registros,
  la API funciona pero no guarda las solicitudes.
- **Roles de acceso** (API / investigador / consulta): se crean aparte porque requieren
  contraseñas definidas por el equipo.
- **Purga automática a 90 días**: se configura aparte (por ejemplo con `pg_cron`).

La sección Pendiente deja claro qué falta, para que nadie piense que con esto la API ya guarda registros. Cuando suban el seed.sql, se agrega a la tabla de "Contenido" y se quita de "Pendiente".