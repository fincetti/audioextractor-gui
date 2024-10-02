import os
import sys
import time
import ffmpeg
import platform
import subprocess
import multiprocessing

from PyQt5 import QtGui
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QComboBox, QProgressBar, QMessageBox, QGroupBox,
    QRadioButton, QHBoxLayout, QButtonGroup, QSlider, QStyle, QSpacerItem, QSizePolicy
)





'''
>>> Metadata para versión
'''
VERSION = '1.0'





class AudioExtractorThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, video_path, output_format, output_folder, speed_option):
        super().__init__()
        self.video_path = video_path
        self.output_format = output_format
        self.output_folder = output_folder
        self.speed_option = speed_option

    def run(self):
        try:
            video_filename = os.path.basename(self.video_path)
            base_name = os.path.splitext(video_filename)[0]

            # Generar el siguiente ID
            audio_id = self.generate_next_id()

            output_filename = f"audio_{audio_id}.{self.output_format}"
            output_path = os.path.join(self.output_folder, output_filename)

            # Obtener la duración del video
            probe = ffmpeg.probe(self.video_path)
            video_duration = float(probe['format']['duration'])

            # Configurar velocidad de procesamiento
            threads = self.get_thread_count()

            # Crear el proceso de ffmpeg con progreso en tiempo real
            self.progress.emit(0)  # Iniciar progreso

            cmd = (
                ffmpeg
                .input(self.video_path)
                .output(output_path, **self.get_audio_params(), threads=threads)
                .global_args('-progress', 'pipe:1', '-nostats')
                .compile()
            )

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            while True:
                line = process.stdout.readline()
                if 'out_time=' in line:
                    # Extraer el tiempo procesado de la salida de ffmpeg
                    time_str = line.strip().split('=')[1]
                    processed_time = self.ffmpeg_time_to_seconds(time_str)
                    progress_percentage = int((processed_time / video_duration) * 100)
                    self.progress.emit(progress_percentage)
                if process.poll() is not None:
                    break

            process.wait()  # Esperar a que el proceso termine

            if process.returncode == 0:
                self.progress.emit(100)  # Finalizar progreso
                self.finished.emit(True, output_path)
            else:
                error_message = process.stderr.read()
                self.finished.emit(False, error_message)

        except Exception as e:
            self.finished.emit(False, str(e))

    def generate_next_id(self):
        """Genera el siguiente ID disponible para el archivo"""
        existing_files = os.listdir(self.output_folder)
        audio_ids = [int(f.split('_')[1].split('.')[0]) for f in existing_files if f.startswith('audio_')]
        next_id = max(audio_ids) + 1 if audio_ids else 1
        return f'{next_id:02d}'

    def get_thread_count(self):
        """Determina la cantidad de hilos a usar dependiendo de la opción seleccionada"""
        cpu_count = multiprocessing.cpu_count()
        if self.speed_option == "Normal":
            return max(1, cpu_count // 2)  # Usar el 50% de los threads
        elif self.speed_option == "Intensivo":
            return max(1, int(cpu_count * 0.8))  # Usar el 80% de los threads

    def get_audio_params(self):
        """Retorna los parámetros adecuados para el formato de audio de salida"""
        if self.output_format == "mp3":
            return {'audio_bitrate': '320k'}
        elif self.output_format == "wav":
            return {'format': 'wav', 'acodec': 'pcm_s16le'}
        return {}

    def ffmpeg_time_to_seconds(self, time_str):
        """Convierte un string de tiempo de ffmpeg (HH:MM:SS.mmm) a segundos"""
        time_parts = time_str.split(':')
        hours = float(time_parts[0])
        minutes = float(time_parts[1])
        seconds = float(time_parts[2])
        return hours * 3600 + minutes * 60 + seconds


class AudioExtractorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Definir ícono de programa y otras propiedades de ventana
        icon_r = os.path.join('Storage', 'Settings', 'Icons', 'icon_01.png')
        self.setWindowIcon(QtGui.QIcon(icon_r))
        
        self.setWindowTitle(f'Extractor de Audio de Video - v{VERSION}')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Grupo para archivo de video
        file_group = QGroupBox("Archivo de video")
        file_layout = QVBoxLayout()

        # Etiqueta de archivo seleccionado
        self.file_label = QLabel("Archivo de video: No seleccionado")
        file_layout.addWidget(self.file_label)

        # Botón para seleccionar archivo de video
        self.select_button = QPushButton('Seleccionar archivo de video')
        self.select_button.clicked.connect(self.select_video)
        file_layout.addWidget(self.select_button)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Espaciador
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Grupo de Reproductor de video (oculto por defecto)
        self.video_player_group = QGroupBox("Reproductor de video")
        video_player_layout = QVBoxLayout()

        # QVideoWidget para mostrar el video (oculto por defecto)
        self.video_widget = QVideoWidget()
        self.video_player = QMediaPlayer()
        self.video_player.setVideoOutput(self.video_widget)

        video_player_layout.addWidget(self.video_widget)

        # Controles de reproducción
        self.play_button = QPushButton("Reproducir")
        self.play_button.clicked.connect(self.toggle_video_playback)
        video_player_layout.addWidget(self.play_button)

        self.video_slider = QSlider(Qt.Horizontal)
        self.video_slider.setRange(0, 0)
        self.video_slider.sliderMoved.connect(self.set_video_position)
        video_player_layout.addWidget(self.video_slider)

        self.video_player.positionChanged.connect(self.update_video_position)
        self.video_player.durationChanged.connect(self.update_video_duration)

        self.video_player_group.setLayout(video_player_layout)
        layout.addWidget(self.video_player_group)

        # Ocultar todo el grupo del reproductor de video por defecto
        self.video_player_group.hide()

        # Espaciador
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Grupo para formato de salida
        format_group = QGroupBox("Formato de salida")
        format_layout = QHBoxLayout()

        self.format_combobox = QComboBox()
        self.format_combobox.addItems(['mp3', 'wav'])
        format_layout.addWidget(self.format_combobox)

        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        # Espaciador
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Grupo para velocidad de procesamiento
        speed_group = QGroupBox("Velocidad de procesamiento")
        speed_layout = QVBoxLayout()

        self.normal_radio = QRadioButton("Normal (50% de threads)")
        self.intense_radio = QRadioButton("Intensivo (80% de threads)")
        self.normal_radio.setChecked(True)

        speed_layout.addWidget(self.normal_radio)
        speed_layout.addWidget(self.intense_radio)

        self.speed_button_group = QButtonGroup()
        self.speed_button_group.addButton(self.normal_radio)
        self.speed_button_group.addButton(self.intense_radio)

        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)

        # Espaciador
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Layout horizontal para los botones
        button_layout = QHBoxLayout()

        # Botón para iniciar la extracción
        self.extract_button = QPushButton('Extraer Audio')
        self.extract_button.clicked.connect(self.extract_audio)
        self.extract_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout.addWidget(self.extract_button)

        # Nuevo botón "Ver audios extraídos"
        self.view_audios_button = QPushButton('Ver audios extraídos')
        self.view_audios_button.setStyleSheet("background-color: #006fc1; color: white;")
        self.view_audios_button.clicked.connect(self.open_audio_folder)
        self.view_audios_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout.addWidget(self.view_audios_button)

        layout.addLayout(button_layout)

        # Barra de progreso
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Espaciador
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Grupo del Reproductor de audio (oculto por defecto)
        self.audio_player_group = QGroupBox("Reproductor de audio extraído")
        audio_player_layout = QVBoxLayout()

        self.audio_player = QMediaPlayer()
        self.play_audio_button = QPushButton("Reproducir audio extraído")
        self.play_audio_button.setEnabled(False)
        self.play_audio_button.clicked.connect(self.toggle_audio_playback)
        audio_player_layout.addWidget(self.play_audio_button)

        self.audio_slider = QSlider(Qt.Horizontal)
        self.audio_slider.setRange(0, 0)
        self.audio_slider.sliderMoved.connect(self.set_audio_position)
        audio_player_layout.addWidget(self.audio_slider)

        self.audio_player.positionChanged.connect(self.update_audio_position)
        self.audio_player.durationChanged.connect(self.update_audio_duration)

        self.audio_player_group.setLayout(audio_player_layout)
        layout.addWidget(self.audio_player_group)

        # Ocultar todo el grupo del reproductor de audio por defecto
        self.audio_player_group.hide()

        self.setLayout(layout)

        # Aplicar el modo oscuro
        self.apply_dark_mode()

    def open_audio_folder(self):
        output_folder = os.path.join(os.getcwd(), 'Storage', 'Audios')
        
        # Crear la carpeta si no existe
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Detectar el sistema operativo
        system_platform = platform.system()

        try:
            if system_platform == "Linux":
                # Usar xdg-open para abrir la carpeta en Linux
                subprocess.run(["xdg-open", output_folder], check=True)
            elif system_platform == "Darwin":  # macOS
                # Usar open para abrir la carpeta en macOS
                subprocess.run(["open", output_folder], check=True)
            elif system_platform == "Windows":
                # Usar explorer para abrir la carpeta en Windows
                subprocess.run(["explorer", output_folder], check=True)
            else:
                # Sistema operativo no soportado
                raise OSError(f"Sistema operativo no soportado: {system_platform}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el explorador de archivos: {str(e)}")

    def apply_dark_mode(self):
        dark_style = """
        QWidget {
            background-color: #2E2E2E;
            color: #F0F0F0;
        }
        QGroupBox {
            border: 1px solid #707070;
            margin-top: 10px;
            background-color: #3E3E3E;
            font-weight: bold;
            color: #F0F0F0;
        }
        QPushButton {
            background-color: #4C4C4C;
            border: 1px solid #707070;
            padding: 5px;
            color: #F0F0F0;
        }
        QPushButton:pressed {
            background-color: #5C5C5C;
        }
        QSlider::groove:horizontal {
            background: #4C4C4C;
            height: 8px;
        }
        QSlider::handle:horizontal {
            background: #707070;
            width: 18px;
            margin: -5px 0;
        }
        QProgressBar {
            background-color: #4C4C4C;
            border: 1px solid #707070;
        }
        QProgressBar::chunk {
            background-color: #707070;
        }
        QComboBox, QLabel, QRadioButton {
            background-color: #3E3E3E;
            color: #F0F0F0;
        }
        """
        self.setStyleSheet(dark_style)

    def select_video(self):
        # Abrir diálogo para seleccionar archivo de video
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo de video", "",
                                                   "Videos (*.mp4 *.mov *.mkv);;Todos los archivos (*)", options=options)
        if file_path:
            self.file_label.setText(f"Archivo de video: {os.path.basename(file_path)}")
            self.video_path = file_path

            # Mostrar el grupo del reproductor de video
            self.video_player_group.show()

            # Cargar video en el reproductor
            self.video_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.video_player.play()

    def extract_audio(self):
        if not hasattr(self, 'video_path'):
            QMessageBox.warning(self, 'Error', 'Por favor selecciona un archivo de video primero.')
            return

        output_format = self.format_combobox.currentText()

        # Carpeta de salida
        output_folder = os.path.join(os.getcwd(), 'Storage', 'Audios')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Obtener opción de velocidad
        if self.normal_radio.isChecked():
            speed_option = "Normal"
        elif self.intense_radio.isChecked():
            speed_option = "Intensivo"

        # Crear un hilo para la extracción
        self.thread = AudioExtractorThread(self.video_path, output_format, output_folder, speed_option)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_extraction_finished)
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_extraction_finished(self, success, result):
        if success:
            QMessageBox.information(self, 'Éxito', f'Audio extraído correctamente: {result}')
            self.play_audio_button.setEnabled(True)
            self.audio_player.setMedia(QMediaContent(QUrl.fromLocalFile(result)))

            # Mostrar el grupo del reproductor de audio
            self.audio_player_group.show()
        else:
            QMessageBox.critical(self, 'Error', f'Ocurrió un error: {result}')

    # Reproductor de video
    def toggle_video_playback(self):
        if self.video_player.state() == QMediaPlayer.PlayingState:
            self.video_player.pause()
            self.play_button.setText("Reproducir")
        else:
            self.video_player.play()
            self.play_button.setText("Pausar")

    def set_video_position(self, position):
        self.video_player.setPosition(position)

    def update_video_position(self, position):
        self.video_slider.setValue(position)

    def update_video_duration(self, duration):
        self.video_slider.setRange(0, duration)

    # Reproductor de audio
    def toggle_audio_playback(self):
        if self.audio_player.state() == QMediaPlayer.PlayingState:
            self.audio_player.pause()
            self.play_audio_button.setText("Reproducir audio extraído")
        else:
            self.audio_player.play()
            self.play_audio_button.setText("Pausar audio")

    def set_audio_position(self, position):
        self.audio_player.setPosition(position)

    def update_audio_position(self, position):
        self.audio_slider.setValue(position)

    def update_audio_duration(self, duration):
        self.audio_slider.setRange(0, duration)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    extractor = AudioExtractorApp()
    extractor.show()
    sys.exit(app.exec_())
