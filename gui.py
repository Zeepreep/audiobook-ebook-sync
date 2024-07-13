import os
import sys
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QTextEdit, QVBoxLayout, \
    QHBoxLayout, QWidget, QMessageBox, QProgressBar, QListWidgetItem, QListWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, Qt, QTimer, QTime
from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor

from mutagen.mp4 import MP4, MP4Cover

class AudiobookSyncApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()

    def run(self):
        self.window.show()
        sys.exit(self.app.exec_())


class AudiobookItemWidget(QWidget):
    def __init__(self, title, artist, album, artwork_data):
        super().__init__()
        layout = QHBoxLayout()

        # Artwork
        self.artwork_label = QLabel(self)
        if artwork_data:
            pixmap = QPixmap()
            pixmap.loadFromData(artwork_data)
            self.artwork_label.setPixmap(pixmap.scaledToHeight(50, Qt.SmoothTransformation))
        else:
            self.artwork_label.setPixmap(QPixmap('default_cover.png').scaledToHeight(50, Qt.SmoothTransformation))
        layout.addWidget(self.artwork_label)

        # Metadata
        metadata_layout = QVBoxLayout()
        self.title_label = QLabel(title)
        self.artist_label = QLabel(artist)
        self.album_label = QLabel(album)
        metadata_layout.addWidget(self.title_label)
        metadata_layout.addWidget(self.artist_label)
        metadata_layout.addWidget(self.album_label)
        layout.addLayout(metadata_layout)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Audiobook Sync')
        self.setGeometry(100, 100, 1000, 800)

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        self.setStyleSheet("background-color: #000000; color: #FFFFFF; font-family: Arial, sans-serif;")

        layout = QVBoxLayout()

        # Control buttons with styling
        button_layout = QHBoxLayout()

        self.load_audio_button = QPushButton('Load Audiobook', self)
        self.load_audio_button.clicked.connect(self.load_audiobook)
        self.load_audio_button.setStyleSheet("QPushButton { background-color: #1DB954; color: #FFFFFF; border: 2px solid #FFFFFF; border-radius: 5px; padding: 10px; }"
                                             "QPushButton:hover { background-color: #1ED760; }")
        button_layout.addWidget(self.load_audio_button)

        self.convert_button = QPushButton('Convert to Text', self)
        self.convert_button.clicked.connect(self.convert_audio)
        self.convert_button.setEnabled(False)
        self.convert_button.setStyleSheet("QPushButton { background-color: #1DB954; color: #FFFFFF; border: 2px solid #FFFFFF; border-radius: 5px; padding: 10px; }"
                                          "QPushButton:hover { background-color: #1ED760; }")
        button_layout.addWidget(self.convert_button)

        # Add a button for selecting a folder
        self.select_folder_button = QPushButton('Select Audiobook Folder', self)
        self.select_folder_button.setStyleSheet(
            "QPushButton { background-color: #1DB954; color: #FFFFFF; border: 2px solid #FFFFFF; border-radius: 5px; padding: 10px; }"
            "QPushButton:hover { background-color: #1ED760; }")
        self.select_folder_button.clicked.connect(self.select_audiobook_folder)
        button_layout.addWidget(self.select_folder_button)

        layout.addLayout(button_layout)

        # Text display area
        self.text_display = QTextEdit(self)
        self.text_display.setStyleSheet("background-color: #1E1E1E; color: #FFFFFF;")
        layout.addWidget(self.text_display)

        # Status bar and progress bar
        status_layout = QHBoxLayout()

        self.status_label = QLabel('Status: Waiting for input...', self)
        status_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        status_layout.addWidget(self.progress_bar)

        layout.addLayout(status_layout)

        # Bottom bar Start
        bottom_bar_layout = QHBoxLayout()
        layout.addLayout(bottom_bar_layout)

        # Metadata and cover art layout
        metadata_layout = QHBoxLayout()

        # Cover art
        self.cover_label = QLabel(self)
        self.cover_label.setPixmap(QPixmap('resources/default_cover.png').scaledToHeight(70, Qt.SmoothTransformation))
        metadata_layout.addWidget(self.cover_label)

        # Text labels layout
        text_layout = QVBoxLayout()
        self.title_label = QLabel('Title', self)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.artist_label = QLabel('Artist', self)
        self.album_label = QLabel('Album', self)

        # Adding text labels to the vertical layout
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.artist_label)
        text_layout.addWidget(self.album_label)

        # Adding the text layout to the metadata layout
        metadata_layout.addLayout(text_layout)

        # Adjusting the stretch factors to control space distribution
        metadata_layout.setStretchFactor(self.cover_label, 1)
        metadata_layout.setStretchFactor(text_layout, 11)


        # Adjusting playback_layout to QVBoxLayout for vertical stacking
        playback_layout = QVBoxLayout()

        self.play_button = QPushButton('Play Audiobook', self)
        self.play_button.clicked.connect(self.play_audiobook)
        self.play_button.setEnabled(False)
        self.play_button.setStyleSheet(
            "QPushButton { background-color: #1DB954; color: #FFFFFF; border: 2px solid #FFFFFF; border-radius: 5px; padding: 10px; }"
            "QPushButton:hover { background-color: #1ED760; }")
        playback_layout.addWidget(self.play_button)


        # Playback information layout
        playback_info_layout = QHBoxLayout()

        # Time played label
        self.time_played_label = QLabel('00:00', self)
        self.time_played_label.setStyleSheet("font-size: 12px; color: #FFFFFF;")
        playback_info_layout.addWidget(self.time_played_label)

        # Playback progress bar
        self.playback_bar = QProgressBar(self)
        self.playback_bar.setTextVisible(False)
        self.playback_bar.setStyleSheet("QProgressBar {border: 2px solid #FFFFFF; border-radius: 5px;}"
                                        "QProgressBar::chunk {background-color: #1DB954;}")

        # Adjusting the playback bar style
        self.playback_bar.setStyleSheet("QProgressBar {border: 2px solid #FFFFFF; border-radius: 5px;}"
                                        "QProgressBar::chunk {background-color: #1DB954;}")
        playback_info_layout.addWidget(self.playback_bar)

        # Total time label
        self.total_time_label = QLabel('00:00', self)
        self.total_time_label.setStyleSheet("font-size: 12px; color: #FFFFFF;")
        playback_info_layout.addWidget(self.total_time_label)

        # Insert the playback information layout into the main layout
        playback_layout.insertLayout(layout.indexOf(self.text_display), playback_info_layout)

        # Adding the metadata layout to the main layout
        bottom_bar_layout.addLayout(metadata_layout)

        bottom_bar_layout.addLayout(playback_layout)
        bottom_bar_layout.setStretchFactor(playback_layout, 1)



        # Set the main layout
        main_widget.setLayout(layout)

        # Media player initialization
        self.media_player = QMediaPlayer()
        self.media_player.positionChanged.connect(self.update_playback_bar)

        self.playback_timer = QTimer(self)
        self.playback_timer.timeout.connect(self.update_playback_position)
        self.playback_timer.start(1000)

        self.audiobookListWidget = QListWidget(self)
        self.populateAudiobookLibrary("path/to/your/audiobook/directory")
        layout.addWidget(self.audiobookListWidget)

        # Connect the item clicked signal to a method to handle the selection
        self.audiobookListWidget.itemClicked.connect(self.audiobookSelected)






    def load_audiobook(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open Audiobook File', '', 'Audio Files (*.mp3 *.wav *.m4a *.m4b);;All Files (*)', options=options)
        if file_path:
            self.display_audiobook_metadata(file_path)
            self.status_label.setText(f'Loaded Audiobook: {file_path}')
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.play_button.setEnabled(True)
            self.convert_button.setEnabled(True)
            self.progress_bar.setValue(0)
            self.playback_bar.setValue(0)

    def display_audiobook_metadata(self, file_path):
        metadata = self.extract_metadata(file_path)
        if metadata:
            title = metadata.get("title", "Unknown Title")
            artist = metadata.get("artist", "Unknown Artist")
            album = metadata.get("album", "Unknown Album")

            artwork_data = metadata.get("artwork", None)

            self.title_label.setText(title)
            self.artist_label.setText(artist)
            self.album_label.setText(album)

            if artwork_data:
                pixmap = QPixmap()
                pixmap.loadFromData(artwork_data)
                self.cover_label.setPixmap(pixmap.scaledToHeight(70, Qt.SmoothTransformation))
            else:
                self.cover_label.setPixmap(QPixmap('default_cover.png').scaledToHeight(70, Qt.SmoothTransformation))

    def extract_metadata(self, file_path):
        try:
            audio = MP4(file_path)
            metadata = {
                "title": audio.tags.get("\xa9nam", ["Unknown Title"])[0],
                "artist": audio.tags.get("\xa9ART", ["Unknown Artist"])[0],
                "album": audio.tags.get("\xa9alb", ["Unknown Album"])[0],
            }

            if "covr" in audio.tags:
                artwork = audio.tags["covr"][0]
                artwork_data = artwork if isinstance(artwork, bytes) else artwork.data
                metadata["artwork"] = artwork_data
            else:
                metadata["artwork"] = None

            return metadata
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return {}

    def convert_audio(self):
        file_path = self.media_player.currentMedia().canonicalUrl().toLocalFile()
        self.status_label.setText(f'Converting Audiobook: {file_path}')
        self.progress_bar.setValue(0)
        thread = threading.Thread(target=self.process_audio_conversion, args=(file_path,))
        thread.start()

    def process_audio_conversion(self, file_path):
        try:
            from audio_processor import convert_audio_to_text
            transcript = convert_audio_to_text(file_path, progress_callback=self.update_progress)
            self.text_display.setPlainText(transcript)
            self.status_label.setText(f'Conversion complete for: {file_path}')
        except Exception as e:
            self.status_label.setText('Status: Conversion failed')
            QMessageBox.critical(self, "Error", f"Failed to convert audiobook: {e}")

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def play_audiobook(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_button.setText('Play Audiobook')
        else:
            self.media_player.play()
            self.play_button.setText('Pause Audiobook')

    def update_playback_bar(self, position):
        duration = self.media_player.duration()
        if duration > 0:
            self.playback_bar.setMaximum(duration)
            self.playback_bar.setValue(position)

            # Update time played and total time labels
            currentTime = QTime(0, 0).addMSecs(position)
            totalTime = QTime(0, 0).addMSecs(duration)
            self.time_played_label.setText(currentTime.toString("mm:ss"))
            self.total_time_label.setText(totalTime.toString("mm:ss"))

    def update_playback_position(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            position = self.media_player.position()
            self.playback_bar.setValue(position)


    def select_audiobook_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Audiobook Folder")
        if folder_path:
            self.populateAudiobookLibrary(folder_path)

    def populateAudiobookLibrary(self, rootDir):
        self.audiobookListWidget.clear()  # Clear existing items
        audiobooks = {}  # Dictionary to hold album names and their file paths

        for root, dirs, files in os.walk(rootDir):
            for file in files:
                if file.endswith(('.mp3', '.wav', '.m4a', '.m4b')):
                    file_path = os.path.join(root, file)
                    metadata = self.extract_metadata(file_path)
                    album = metadata['album']
                    if album not in audiobooks:
                        audiobooks[album] = {
                            'title': metadata['title'],
                            'artist': metadata['artist'],
                            'album': album,
                            'artwork': metadata.get('artwork'),
                            'files': [file_path]
                        }
                    else:
                        audiobooks[album]['files'].append(file_path)

        for album, details in audiobooks.items():
            audiobook_widget = AudiobookItemWidget(details['title'], details['artist'], details['album'], details.get('artwork'))
            listItem = QListWidgetItem()
            listItem.setSizeHint(audiobook_widget.sizeHint())
            self.audiobookListWidget.addItem(listItem)
            self.audiobookListWidget.setItemWidget(listItem, audiobook_widget)
            listItem.setData(Qt.UserRole, details['files'])  # Store list of file paths in the item's data

    def audiobookSelected(self, item):
        audiobookPaths = item.data(Qt.UserRole)
        if isinstance(audiobookPaths, list) and audiobookPaths:
            # For simplicity, load the first file. You might want to extend this to handle multiple files.
            firstFilePath = audiobookPaths[0]
            self.load_audiobook_file(firstFilePath)
            self.status_label.setText(f'Selected Audiobook: {firstFilePath}')
            self.play_button.setEnabled(True)
            self.convert_button.setEnabled(True)
            self.progress_bar.setValue(0)
            self.playback_bar.setValue(0)
            self.play_button.setText('Play Audiobook')

    def load_audiobook_file(self, file_path):
        self.display_audiobook_metadata(file_path)
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))

# Assuming the rest of your application setup remains the same
if __name__ == "__main__":
    app = AudiobookSyncApp()
    app.run()