# Extractor de Audio de Video

Este es un programa escrito en Python que permite extraer el audio de archivos de video en formatos como `.mp4`, `.mov`, `.mkv`, entre otros. La aplicación ofrece una interfaz gráfica (GUI) construida con PyQt5, permite seleccionar diferentes formatos de salida de audio (`mp3` y `wav`), y optimiza el procesamiento utilizando diferentes niveles de intensidad según los recursos del sistema.

## Características

- **Extracción de audio**: Extrae el audio de archivos de video en los formatos `mp3` o `wav`.
- **Interfaz gráfica (GUI)**: Usa PyQt5 para proporcionar una interfaz de usuario interactiva.
- **Opciones de velocidad**: Permite elegir entre un procesamiento normal (50% de threads) o intensivo (80% de threads).
- **Reproducción**: Incorpora reproductores para tanto el video de origen como el audio extraído.
- **Soporte de múltiples formatos de video**: Admite videos en formatos como `.mp4`, `.mov`, `.mkv`, entre otros.

## Instalación

Sigue los siguientes pasos para instalar y ejecutar la aplicación.

### Requisitos previos

1. **Python 3.x**: Asegúrate de tener instalado Python 3. Puedes descargarlo desde [python.org](https://www.python.org/downloads/).
2. **FFmpeg**: Es necesario tener FFmpeg instalado en tu sistema para manejar el procesamiento de medios.

   - En sistemas **Linux** (Debian/Ubuntu):

     ```bash
     sudo apt update
     ```
     ```bash
     sudo apt install build-essential git libssl-dev libfaac-dev libmp3lame-dev libx264-dev libxvidcore-dev libvorbis-dev libtheora-dev
     ```
     ```bash
     sudo apt install ffmpeg
     ```

   - En sistemas **Windows**:
     - Descarga FFmpeg desde la [página oficial](https://ffmpeg.org/download.html).
     - Descomprime el archivo descargado y agrega la ruta `bin` de FFmpeg a las variables de entorno del sistema.
   
   - En sistemas **macOS**:

     ```bash
     brew install ffmpeg
     ```

### Instalación de dependencias

1. Clona este repositorio en tu máquina local:

   ```bash
   git clone https://github.com/fincetti/audioextractor-gui.git
   cd audioextractor-gui
   ```

2. Instala las dependencias necesarias utilizando `pip`:

   ```bash
   pip install -r DOCs/requirements.txt
   ```

3. Asegúrate de tener instalado **multiprocessing** (que debería venir preinstalado con Python estándar).

### Ejecución de la aplicación

Una vez que hayas instalado todas las dependencias, puedes ejecutar la aplicación usando el siguiente comando:

```bash
python3 main.py
```

## Uso

1. Al abrir la aplicación, selecciona un archivo de video desde tu sistema.
2. Elige el formato de audio de salida (`mp3` o `wav`).
3. Selecciona la velocidad de procesamiento (`Normal` o `Intensivo`).
4. Haz clic en el botón **Extraer Audio** para iniciar el proceso.
5. Una vez completado, puedes reproducir el audio extraído directamente desde la aplicación.

## Estructura del proyecto

```plaintext
.
├── main.py                    # Archivo principal del programa
├── DOCs/requirements.txt      # Dependencias del proyecto
├── Storage/                   # Directorio donde se almacenan audios extraídos
│   └── Audios/
│   └── Settings/
│       └── Icons/              # Iconos de la aplicación
└── README.md                   # Este archivo
```

## Compilación de programa
Este programa ya cuenta con compilaciones hechas previamente las cuales están disponibles en la sección de releases, puedes descargar la tuya y no tener que ejecutar el comando:

```bash
pyinstaller --name extractor_audio --onefile --windowed --add-data "/usr/bin/ffmpeg:." main.py
```

Goodbye world!
