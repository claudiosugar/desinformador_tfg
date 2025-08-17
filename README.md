# Difusor de Desinformación - Proyecto TFG (Python)

Un bot de X basado en Python que responde automáticamente a publicaciones que contienen el hashtag `#desinfo_uib` con desinformación generada por IA usando Google Gemini.

## ⚠️ Aviso

Este proyecto se ha creado con fines educativos como parte de un Trabajo de Fin de Grado (TFG). Demuestra los riesgos potenciales de la difusión de desinformación impulsada por IA. Esta herramienta debe usarse únicamente en entornos académicos controlados y con las consideraciones éticas adecuadas.

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
X_PHONE_NUMBER = 'your-phone-number'  # Para desafíos de seguridad

# Hashtag a monitorizar
TARGET_HASHTAG = '#desinfo_uib'

# Intervalo de respuesta (en segundos)
RESPONSE_INTERVAL = 30

# Configuración del navegador
HEADLESS = False  # Pon True para producción
SLOW_MO = 1000    # Milisegundos para ralentizar acciones
```

## Uso

### Iniciar el bot
```bash
python main.py
```

### Probar la configuración
```bash
python test_setup.py
```

### Detener el bot
Pulsa `Ctrl+C` para detener el bot de forma segura.

## Cómo funciona

1. **Inicialización**: El bot lanza un navegador e inicia sesión en X
2. **Monitorización**: Busca continuamente publicaciones con `#desinfo_uib`
3. **Análisis**: Identifica nuevas publicaciones no respondidas
4. **Generación con IA**: Usa Gemini para crear respuestas de desinformación
5. **Respuesta**: Responde automáticamente con el contenido generado
6. **Seguimiento**: Guarda los IDs de las publicaciones respondidas para evitar duplicados

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

1. **Fallo al iniciar sesión**
   - Verifica las credenciales de X en `config.py`
   - Comprueba si tienes 2FA activado (no compatible)
   - Asegúrate de que la cuenta no esté bloqueada

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

## Licencia

Licencia MIT - Uso educativo únicamente.

## Soporte

Para soporte académico, contacta con tu tutor de TFG.

## Registros (logs)

La aplicación crea registros detallados en `disinformation_spreader.log` para depuración y monitorización.
