# Devlog — Service Monitor

Notas de desarrollo: qué se ha hecho en cada paso, por qué, y los conceptos que han ido saliendo.

---

## Paso 1 · Esqueleto del repo y primer endpoint (19–23 nov 2026)

### Qué se hizo

- Entorno preparado: WSL 2 (Ubuntu 22.04), Docker Desktop, uv 0.13.9, VS Code con la extensión WSL.
- Proyecto creado con `uv init`, dependencias añadidas con `uv add`.
- Primer endpoint `GET /health`, con su test.
- La app corre en Docker y se levanta con `docker compose up`.
- Primer commit y repo público: github.com/zellorz/service-monitor

### Estructura

```
service-monitor/                ← raíz: config del proyecto, Docker, Git
├── pyproject.toml              ficha del proyecto + config de Ruff y pytest
├── uv.lock                     versiones exactas de todas las dependencias
├── .python-version             "3.12"
├── src/service_monitor/        ← el código Python
│   ├── main.py                 crea la app y enchufa los routers
│   ├── core/config.py          configuración leída de variables de entorno
│   └── api/routes/health.py    primer endpoint
├── tests/test_health.py
├── Dockerfile · .dockerignore · compose.yaml
├── .env.example                plantilla de variables (va a Git)
├── .env                        valores reales y secretos (NO va a Git)
└── README.md
```

Regla práctica: configuración del proyecto en la raíz; código Python en `src/service_monitor`.

### El código, archivo a archivo

- **`core/config.py`**: clase `Settings` (pydantic-settings). Cada atributo es una variable de configuración con tipo y valor por defecto; se sobrescribe desde el entorno o el `.env`. Una sola instancia, `settings`, que importa todo el código.
- **`api/routes/health.py`**: un `APIRouter` con `GET /health`, que devuelve un `HealthResponse` (modelo Pydantic). La anotación `-> HealthResponse` hace que FastAPI valide la respuesta y la documente en Swagger. Patrón que se repetirá en todos los endpoints.
- **`main.py`**: crea `app = FastAPI(...)` y le añade el router.
- **`tests/test_health.py`**: `TestClient` llama a la app en memoria (sin servidor) y comprueba código 200 y contenido.
- **`Dockerfile`**: `python:3.12-slim` + uv fijado a 0.13.9. Dos capas: primero dependencias, luego código, para que los builds sean rápidos. Arranca con `fastapi run` (producción).
- **`compose.yaml`**: servicio `api`, puerto 8000, lee `.env`. Aquí se añadirá Postgres.

### Decisiones y por qué

- **Estructura `src/`** (la genera uv 0.13 por defecto): el código se instala como paquete en el `.venv`, así `from service_monitor...` funciona igual en tests, Docker y terminal. Es la estructura recomendada por la guía oficial de empaquetado de Python.
- **`uv.lock` en Git, `.venv` fuera**: el lock garantiza las mismas versiones en todas partes; el `.venv` se regenera en cada máquina.
- **`.env` fuera de Git, `.env.example` dentro**: los secretos se quedan en cada máquina; la plantilla documenta qué variables existen.
- **`.dockerignore`**: evita meter el `.venv` local o el `.env` en la imagen.
- **Docker desde el día 1**: requisito del proyecto (`git clone` + `docker compose up`); más fácil mantenerlo desde el principio que adaptarlo al final.
- **Ruff y tests desde el primer endpoint**: el código nace limpio y comprobado; GitHub Actions solo tendrá que repetir lo mismo.
- **Conventional Commits** (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`): historial legible.

---

## Conceptos clave

### Endpoint
Una dirección de la API que responde a una petición concreta: **método + ruta**. Como las ventanillas de una oficina, cada una atiende un trámite.

| Método | Significa | Ejemplo |
|---|---|---|
| GET | leer | `GET /services` — listar servicios |
| POST | crear | `POST /services` — dar de alta uno |
| PUT / PATCH | modificar | `PATCH /services/5` |
| DELETE | borrar | `DELETE /services/5` |

En el código, cada endpoint es una función con un decorador (`@router.get("/health")`). Swagger (`/docs`) muestra la lista.

Códigos de respuesta habituales: **200** OK · **404** no existe · **422** datos inválidos · **500** error en mi código.

### Imagen y contenedor (Docker)
Como componente maestro e instancias en Figma:
- **Dockerfile** → las instrucciones para construir el maestro.
- **Imagen** → el maestro construido y congelado (Linux + Python + librerías + mi código). Se crea con `docker build`.
- **Contenedor** → una instancia de la imagen en marcha. Se crea con `docker run` / `docker compose up`.

Si cambio código, hay que reconstruir la imagen (`--build`).

### "Entorno" significa tres cosas distintas
1. **Variables de entorno**: pares `NOMBRE=valor` que el sistema entrega a un programa al arrancar.
2. **`.env`**: archivo de texto con esas variables apuntadas. Compose lo lee y se las pasa al contenedor.
3. **"Entorno local / producción"**: dónde corre la app (mi PC, el servidor...).

Y además:
- **`Settings`** (`config.py`): el código que lee las variables, valida su tipo y las ofrece a la app.
- **`.venv`** ("virtual environment"): nada que ver con lo anterior. Carpeta con Python y las librerías de este proyecto.

Cadena: `.env` → variables de entorno → `Settings` → mi código.

### Por qué `.env` es secreto
Ahí irán la contraseña de la base de datos, la clave del JWT (quien la tenga puede fabricarse un login de admin) y el token de Telegram. El repo es público, hay bots que rastrean GitHub buscando claves, y Git guarda el historial aunque se borre el archivo. Además, cada máquina tiene sus propios valores.

### `0.0.0.0` vs `127.0.0.1`
`127.0.0.1` (= `localhost`) significa "solo esta máquina". Dentro de un contenedor, eso es solo el contenedor: no se podría entrar desde fuera. `0.0.0.0` significa "acepta conexiones de cualquier sitio".

---

## Chuleta de comandos

### Proyecto (desde la raíz)
```bash
uv add <paquete>                              # añadir dependencia
uv add --dev <paquete>                        # dependencia solo de desarrollo
uv sync                                       # instalar todo según uv.lock (p. ej. en el portátil)
uv run fastapi dev src/service_monitor/main.py   # servidor en desarrollo (recarga sola)
uv run pytest -v                              # tests
uv run ruff check --fix .                     # lint y arreglos automáticos
uv run ruff format .                          # formatear
```

### Docker
```bash
docker compose up --build      # construir y arrancar
docker compose up -d           # en segundo plano
docker compose logs -f         # ver logs
docker compose down            # parar
docker compose config          # ver la config final (con .env aplicado)
```

### Git
```bash
git status                     # qué ha cambiado
git add .                      # preparar cambios
git commit -m "tipo: mensaje"  # guardar
git push                       # subir a GitHub
git log --oneline              # historial
```

### Terminal
- **Tab** autocompleta · **↑/↓** comandos anteriores · **Ctrl+L** limpia
- **Ctrl+C** cancela (no copia; copiar = Ctrl+Shift+C)
- `rm` borra sin papelera
- `cp origen destino` copia · `cat archivo` muestra contenido · `pwd` dónde estoy

### VS Code
- **Ctrl+P** buscar archivo · **Ctrl+Shift+P** paleta de comandos
- **Ctrl+ñ** terminal · papelera = cerrar terminal, X = solo ocultar
- **Ctrl+Shift+M** panel de problemas · **Ctrl+Shift+V** vista previa Markdown
- Punto blanco en la pestaña = sin guardar

### Lecciones del paso 1
- Mirar el prompt antes de ejecutar (`~$` vs `service-monitor$`).
- Archivo sin guardar ≠ archivo en disco. Auto Save activado.
- Los comandos van en la terminal; el contenido, en los archivos.
- Ctrl+C solo funciona con el foco en la terminal.
- En YAML, la indentación es la sintaxis (2 espacios, nunca tabuladores).

---

## Próximo paso
**Paso 2 · Base de datos**: PostgreSQL en compose, SQLAlchemy 2, primer modelo (servicios a monitorizar), primera migración con Alembic.
