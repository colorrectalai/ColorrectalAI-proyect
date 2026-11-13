# ColorrectalAI-proyect

Aplicación académica construida con Vue 3, Vite y Vue Router para explorar el análisis experimental de imágenes de colonoscopia.

## Flujo de pantallas

- `/` — inicio público para visitantes.
- `/acceso` — inicio de sesión de demostración; al completar el formulario, continúa a `/inicio`.
- `/registro` — registro con nombre, correo, contraseña y confirmación; al completarlo, continúa a `/inicio`.
- `/inicio` — dashboard para consultar actividad e iniciar una interpretación.
- `/carga` → `/analizando` → `/resultados/:id` — flujo de carga y revisión de una interpretación.
- `/resultados/:id` → `/comparacion` — comparación visual de imágenes.
- `/historial` → `/historial/:id` — lista de interpretaciones y vista de detalle.

## Desarrollo local

```sh
npm install
npm run dev
```

Las clasificaciones y cifras son datos experimentales de demostración. Todavía no se integra un modelo clínico ni un backend de autenticación.
