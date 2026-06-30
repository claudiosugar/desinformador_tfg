# Difusor de Desinformación - Proyecto TFG (Python)

Un bot de X basado en Python que responde automáticamente a publicaciones que contienen el hashtag `#desinfo_uib` con desinformación generada por IA usando Google Gemini.

## ⚠️ Aviso

Este proyecto se ha creado con fines educativos como parte de un Trabajo de Fin de Grado (TFG). Demuestra los riesgos potenciales de la difusión de desinformación impulsada por IA. Esta herramienta debe usarse únicamente en entornos académicos controlados y con las consideraciones éticas adecuadas.

![Demostración del bot: búsqueda del hashtag y respuesta automática](assets/demo.gif)

*El bot busca el hashtag `#desinfo_uib`, detecta una publicación y genera y publica automáticamente una respuesta con desinformación.*

## Funcionalidades

- 🤖 **Respuestas con IA**: Utiliza Google Gemini para generar respuestas de desinformación convincentes
- 📱 **Automatización de X**: Inicio de sesión e interacción automatizados con Playwright
- 🔍 **Monitorización de hashtag**: Supervisa continuamente el hashtag `#desinfo_uib`
- 💾 **Seguimiento de respuestas**: Evita duplicados registrando las publicaciones ya respondidas
- 🛡️ **Limitación de velocidad**: Retrasos incorporados para evitar la detección en X
- 📊 **Registro (logging)**: Registro detallado para monitorización y depuración
- 🐍 **Implementación en Python**: Uso de patrones modernos async/await para un funcionamiento eficiente

## Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Cuenta de X con credenciales configuradas en `config.py`

## Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd desinformador-tfg
   ```

2. **Instalar dependencias de Python**
   ```bash
   pip install -r requirements.txt
   ```

3. **Instalar navegadores de Playwright**
   ```bash
   playwright install chromium
   ```

4. **Probar la instalación**
   ```bash
   python test_setup.py
   ```

## Configuración

**Importante**: El archivo `config.py` contiene información sensible y no se rastrea en git. Usa `config_template.py` como punto de partida.

1. **Copiar la plantilla**:
   ```bash
   cp config_template.py config.py
   ```

2. **Edita `config.py`** con tus credenciales:

```python
# Clave de API de Gemini
GEMINI_API_KEY = 'your-gemini-api-key'

# Credenciales de X
X_USERNAME = 'your-x-username'
X_PASSWORD = 'your-x-password'

# Hashtag a monitorizar
TARGET_HASHTAG = '#desinfo_uib'

# Intervalo de respuesta (en segundos)
RESPONSE_INTERVAL = 30

# Configuración del navegador
HEADLESS = False  # Pon True para producción
SLOW_MO = 1000    # Milisegundos para ralentizar acciones

# Conectar a un Chrome que tú mismo hayas lanzado con depuración remota
# activada. Déjalo así para usar el puerto por defecto; ponlo a None para
# que el bot lance su propio Chromium (menos fiable - el anti-bot de X
# puede bloquear el inicio de sesión).
CHROME_CDP_URL = 'http://localhost:9222'
```

## Uso

X detecta el Chromium lanzado por Playwright y bloquea silenciosamente el
formulario de inicio de sesión. El bot lo soluciona conectándose por CDP a
una instancia de Chrome que tú mismo lanzas, así hereda tu sesión real ya
iniciada.

### 1. Lanzar Chrome con depuración remota

Windows:
```powershell
"C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  --user-data-dir="<repo>\chrome_profile"
```

macOS / Linux: equivalente `chrome --remote-debugging-port=9222
--user-data-dir=./chrome_profile`.

### 2. Iniciar sesión en X manualmente en esa ventana de Chrome

Ve a https://x.com/i/flow/login e inicia sesión. Resuelve cualquier
captcha o desafío de teléfono a mano. Las cookies de sesión se guardan en
`chrome_profile/` así que solo tendrás que hacerlo una vez.

### 3. Iniciar el bot
```bash
python main.py
```

El bot se conectará a tu Chrome por CDP, detectará la sesión existente y
empezará a monitorizar el hashtag.

### Probar la configuración
```bash
python test_setup.py
```

### Detener el bot
Pulsa `Ctrl+C` para detener el bot de forma segura.

## Cómo funciona

1. **Conectar con Chrome**: Se conecta por CDP (puerto 9222) al Chrome que
   has lanzado tú. Salta el formulario de login si detecta una sesión
   activa.
2. **Monitorización**: Busca el hashtag objetivo mediante el cuadro de
   búsqueda interno (pestaña "Top" por defecto, donde aparecen las
   publicaciones de cuentas nuevas).
3. **Filtrado**: Descarta publicaciones cuyo texto no contenga el hashtag
   objetivo, para evitar responder a contenido viral no relacionado.
4. **Generación con IA**: Usa Gemini (`gemini-2.5-flash`) para crear una
   respuesta de desinformación en el idioma de la publicación.
5. **Respuesta**: Responde a cada publicación que pase el filtro mediante
   la UI de respuesta de X.
6. **Seguimiento**: Guarda los IDs de publicaciones respondidas para
   evitar duplicados.

## Estructura del proyecto

```
desinformador-tfg/
├── src/
│   ├── __init__.py        # Inicialización del paquete
│   ├── gemini_ai.py       # Integración con Gemini AI
│   └── x_bot.py          # Lógica de automatización de X
├── main.py               # Punto de entrada de la aplicación
├── config.py            # Configuración
├── requirements.txt     # Dependencias de Python
├── test_setup.py       # Script de verificación de la instalación
└── README.md           # Este archivo
```

## Dependencias

- **playwright**: Automatización de navegador para interactuar con X
- **google-generativeai**: Integración con la API de Google Gemini
- **python-dotenv**: Gestión de variables de entorno
- **requests**: Solicitudes HTTP para llamadas a API
- **beautifulsoup4**: Análisis de HTML
- **selenium**: Automatización de navegador alternativa (respaldo)

## Medidas de seguridad

- **Limitación de velocidad**: Retrasos entre acciones
- **Prevención de duplicados**: Registro de publicaciones respondidas
- **Manejo de errores**: Recuperación ante fallos
- **Apagado controlado**: Limpieza adecuada al salir
- **Suplantación de agente de usuario**: Evita detección básica de bots
- **Operaciones asíncronas**: Ejecución eficiente no bloqueante

## Consideraciones éticas

Este proyecto demuestra:
- El potencial de la desinformación impulsada por IA
- La importancia de la alfabetización mediática
- La necesidad de un desarrollo responsable de IA
- Los riesgos de la automatización en redes sociales

## Resolución de problemas

### Problemas comunes

1. **Inicio de sesión / "sesión no encontrada"**
   - Asegúrate de haber lanzado Chrome con `--remote-debugging-port=9222`
     antes de ejecutar `main.py`
   - Confirma que http://localhost:9222/json/version responde
   - Inicia sesión en X una vez a mano en esa ventana de Chrome; las
     cookies persisten en `chrome_profile/`
   - NO uses tu perfil de Chrome habitual; el bot espera un
     `--user-data-dir` dedicado

2. **Fallo al generar respuestas con IA**
   - Verifica que la clave de la API de Gemini sea válida
   - Comprueba la conexión a internet
   - Revisa los límites de uso de la API

3. **Problemas con el navegador**
   - Asegúrate de haber instalado Playwright: `playwright install chromium`
   - Prueba a ejecutar en modo headless cambiando `HEADLESS = True` en `config.py`

4. **Problemas con la versión de Python**
   - Asegúrate de tener Python 3.8+
   - Compruébalo con: `python --version`

### Modo de depuración

La aplicación registra automáticamente tanto en consola como en archivo (`disinformation_spreader.log`).

Para depurar adicionalmente, modifica las opciones de lanzamiento del navegador en `src/x_bot.py`:

```python
self.browser = await self.playwright.chromium.launch(
    headless=False,
    slow_mo=1000,
    devtools=True  # Abre las herramientas de desarrollador
)
```

## Desarrollo

### Ejecutar tests
```bash
python test_setup.py
```

### Estructura del código
- **Async/Await**: Patrones asíncronos modernos de Python para un funcionamiento eficiente
- **Manejo de errores**: Bloques try/except con registro estructurado
- **Logging**: Registro estructurado con distintos niveles
- **Configuración**: Gestión centralizada de configuración

## Contribución

Este es un proyecto académico. Solo para fines educativos.

## Asistencia con IA

Partes de la implementación (conexión por CDP para evitar la detección
anti-bot de X, búsqueda en la pestaña "Top" + filtrado por contenido del
hashtag, auto-lanzamiento de Chrome y actualizaciones de modelo de
Gemini) fueron desarrolladas con la asistencia de Claude (Anthropic).
Toda la lógica de la herramienta y las decisiones de diseño son
responsabilidad del autor del TFG.

## Licencia

Licencia MIT - Uso educativo únicamente.

## Soporte

Para soporte académico, contacta con tu tutor de TFG.

## Registros (logs)

La aplicación crea registros detallados en `disinformation_spreader.log` para depuración y monitorización.
