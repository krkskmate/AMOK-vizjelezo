from PyQt6 import uic
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QRect, QPoint, QSize
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon, QPixmap
from PIL import Image, ImageEnhance
import sys
import os
import ctypes
import platform

current_version = "1.4.0"

output_directory = ""  # Set output directory

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(__file__)

app = None


def load_font(font_path):
    # If the operating system is not Windows, return
    if platform.system() != 'Windows':
        return

    # AddFontResource expects a path without the drive letter
    font_path = os.path.splitdrive(font_path)[1].lstrip(os.sep)
    ctypes.windll.gdi32.AddFontResourceW(font_path)


load_font('AMArialRDBD.ttf')


class Worker(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(object)

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        result = self.func(self, *self.args)
        self.result.emit(result)


class MyGUI(QMainWindow):

    def __init__(self):
        super(MyGUI, self).__init__()
        uic.loadUi(os.path.join(base_dir, 'watermarker.ui'), self)
        self.show()

        self.setWindowIcon(QIcon(os.path.join(base_dir, 'logo.ico')))
        self.setWindowTitle("ÁMÖK vízjelező")

        # self.setFixedSize(850, 540)+

        # Watermark tab
        self.selectWorkingDirectory.clicked.connect(self.set_working_directory)
        self.selectOutputDirectory.clicked.connect(self.set_output_directory)

        # Index picture tab
        self.selectIndexPicture.clicked.connect(self.set_index_picture_input)

        # Main submit button
        self.submitButton.clicked.connect(self.start_processing)

        self.originalFileName.stateChanged.connect(
            self.on_checkbox_state_changed)
        self.progressBar.setValue(0)

        self.version.setText(
            f"<html><head/><body><p><span style='color:#676767;'>Verzió: {current_version}</span></p></body></html>")

    def on_checkbox_state_changed(self):
        if self.originalFileName.isChecked():
            self.outputPicName.setEnabled(False)
        else:
            self.outputPicName.setEnabled(True)

    def set_working_directory(self):
        dir_path = QFileDialog.getExistingDirectory(None, "Select Folder")
        if dir_path:
            os.chdir(dir_path)
            # Updateing working directories
            self.workingDirectory.setText(f"{dir_path}")
            print(f"Working directory set to {dir_path}")

    def set_output_directory(self):
        global output_directory
        dir_path = QFileDialog.getExistingDirectory(None, "Select Folder")
        if dir_path:
            output_directory = dir_path
            # Updateing output directories
            self.outputDirectory.setText(f"{dir_path}")
            print(f"Output directory set to {dir_path}")

    def set_index_picture_input(self):
        # Not implemented yet, display message box
        message = QMessageBox()
        message.setIcon(QMessageBox.Icon.Information)
        message.setWindowTitle("DEV")
        message.setText("Ez a funkció jelenleg nincs implementálva")
        message.exec()
        return # Remove this line when implemented

        file_path, _ = QFileDialog.getOpenFileName(
            None, "Select Picture", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.indexPicInput.setText(f"{file_path}")
            print(f"Index picture set to {file_path}")

            self.scene = QGraphicsScene(self)
            self.croppingView.setScene(self.scene)

            self.pixmap = QPixmap(file_path)

            # Scale the pixmap to fit the size of the graphics view
            view_size = self.croppingView.size()
            # scaled_pixmap = self.pixmap
            scaled_pixmap = self.pixmap.scaled(view_size.width(), view_size.height(
            ), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            self.pixmap_item = DraggablePixmapItem(scaled_pixmap)
            self.scene.addItem(self.pixmap_item)

            view = QGraphicsView(self.scene)
            view.show()

    # Start the processing
    def start_processing(self):
        # Check if the tab is on the first tab
        if self.tabWidget.currentIndex() == 0:
            self.watermark_and_progress()

        else:
            # Index pic processing
            self.index_pic_processing()

    def index_pic_processing(self):
        # Check if input file exists and its a picture
        if self.indexPicInput.text() == "":
            message = QMessageBox()
            message.setIcon(QMessageBox.Icon.Warning)
            message.setWindowTitle("Hiba")
            message.setText("Nincs kép kiválasztva")
            message.exec()
            return

        if not os.path.exists(self.indexPicInput.text()):
            message = QMessageBox()
            message.setIcon(QMessageBox.Icon.Warning)
            message.setWindowTitle("Hiba")
            message.setText("A fájl nem létezik")
            message.exec()
            return

        if not self.indexPicInput.text().endswith(('.png', '.jpg', '.jpeg')):
            message = QMessageBox()
            message.setIcon(QMessageBox.Icon.Warning)
            message.setWindowTitle("Hiba")
            message.setText("A fájl nem kép")
            message.exec()
            return

        # Display message box -> not implemented yet
        message = QMessageBox()
        message.setIcon(QMessageBox.Icon.Information)
        message.setWindowTitle("DEV")
        message.setText("Ez a funkció jelenleg nincs implementálva")
        message.exec()

    def watermark_and_progress(self):
        # Check if working directory and output directory is set and the input is not empty
        if (self.workingDirectory.text() == "" or self.outputDirectory.text() == ""):
            message = QMessageBox()
            message.setIcon(QMessageBox.Icon.Warning)
            message.setWindowTitle("Hiba")
            message.setText("Nincs mappa kiválasztva")
            message.exec()
            return

        # Check if the directorys are correct
        if not os.path.exists(self.workingDirectory.text()) or not os.path.exists(self.outputDirectory.text()):
            message = QMessageBox()
            message.setIcon(QMessageBox.Icon.Warning)
            message.setWindowTitle("Hiba")
            message.setText("A mappa nem létezik")
            message.exec()
            return

        self.progressBar.setValue(0)
        QApplication.processEvents()
        project_name = self.outputPicName.text()

        self.worker = Worker(watermark, project_name,
                             self.subfolderOn.isChecked(), self.originalFileName.isChecked())
        self.worker.progress.connect(self.progressBar.setValue)
        self.worker.result.connect(self.on_worker_finished)
        self.worker.start()

    def on_worker_finished(self, result):
        if result:
            # Show message box
            message = QMessageBox()
            message.setIcon(QMessageBox.Icon.Information)
            message.setWindowTitle("Siker")
            message.setText("A vízjelezés befejeződött")
            message.exec()

        # Open the output directory
        if self.openOutputFolder.isChecked():
            os.startfile(output_directory)


class DraggablePixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, parent=None):
        super().__init__(pixmap)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.rubberBand = QRubberBand(QRubberBand.Shape.Rectangle, parent)
        self.origin = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.pos().toPoint()
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.rubberBand.setGeometry(
                QRect(self.origin, event.pos().toPoint()).normalized())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.rubberBand.hide()
            rect = self.rubberBand.geometry()
            self.cropImage(rect)
        super().mouseReleaseEvent(event)

    def cropImage(self, rect):
        # Convert rubber band geometry to scene coordinates
        scene_rect = self.mapToScene(rect).boundingRect().toRect()

        # Ensure the coordinates are within the pixmap bounds
        scene_rect = scene_rect.intersected(self.pixmap().rect())

        # Crop the image using the scene coordinates
        cropped_pixmap = self.pixmap().copy(scene_rect)
        self.setPixmap(cropped_pixmap)


def main():
    global app
    app = QApplication(sys.argv)
    window = MyGUI()

    sys.exit(app.exec())


def watermark(worker, project_name, subfolderOn, originalFileName):

    global app
    try:
        global output_directory
        global base_dir
        print("Watermarking...")

        directory = os.getcwd()
        watermark_image_path = os.path.join(base_dir, 'watermark.png')

        if subfolderOn:
            images = []
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    if filename.endswith(('.png', '.jpg', '.jpeg', '.JPG', '.JPEG', '.PNG')):
                        images.append(os.path.join(dirpath, filename))
        else:
            images = [f for f in os.listdir(directory) if f.endswith(
                ('.png', '.jpg', '.jpeg', '.JPG', '.JPEG', '.PNG'))]

        progress_length = len(images)

        i = 0

        # Scale watermark
        watermark = Image.open(watermark_image_path).convert("RGBA")

        # Create an enhancer for the alpha channel
        enhancer = ImageEnhance.Brightness(watermark.split()[3])

        # Reduce the brightness of the alpha channel to make the watermark 50% transparent
        watermark.putalpha(enhancer.enhance(0.5))

        for filename in images:

            i += 1
            image_path = os.path.join(directory, filename)
            image = Image.open(image_path).convert("RGBA")

            # Check for EXIF data (only available for .jpg)
            if 'exif' in image.info and filename.lower().endswith(('.jpg', '.jpeg')):
                exif_data = image.getexif()
                if exif_data:
                    for tag, value in exif_data.items():
                        if tag == 274:  # 274 is the tag for Orientation
                            if value == 3:  # Rotated 180 degrees
                                image = image.rotate(180)
                            elif value == 6:  # Rotated 90 degrees to the right
                                image = image.rotate(-180)
                                image = image.transpose(
                                    Image.Transpose.ROTATE_90)
                            elif value == 8:  # Rotated 90 degrees to the left
                                image = image.rotate(+180)
                                image = image.transpose(
                                    Image.Transpose.ROTATE_270)

            # Define the percentage of the image dimensions to use for the watermark size
            watermark_percentage = 0.13  # 13% of the image dimensions

            # Get the image dimensions
            image_width, image_height = image.size

            # Calculate the watermark size based on the smaller dimension
            smaller_dimension = min(image_width, image_height)
            watermark_size = int(smaller_dimension * watermark_percentage)

            # Maintain aspect ratio of the watermark
            aspect_ratio = watermark.width / watermark.height
            watermark_width = watermark_size
            watermark_height = int(watermark_size / aspect_ratio)

            # Resize the watermark
            watermark = watermark.resize((watermark_width, watermark_height), Image.LANCZOS)

            if originalFileName:
                outputFileName = filename.split('.')[0]
            else:
                if project_name == "":
                    project_name = "watermarked"
                outputFileName = f"{project_name}-{i}"

            if platform.system() == 'Darwin':  # If the operating system is macOS
                # Set watermark image name for macOS
                converted_image_path = f"{output_directory}/{outputFileName}.{filename.split('.')[1]}"
            else:
                # Set watermark image name for other operating systems
                converted_image_path = f"{output_directory}\\{outputFileName}.{filename.split('.')[1]}"

            # Change position if needed
            width, height = image.size
            watermark_width, watermark_height = watermark.size

            # Define the offset as a percentage of the image dimensions
            offset_percentage = 0.005  # 0.5% of the image dimensions

            # Calculate the offset
            offset_x = int(width * offset_percentage)
            offset_y = int(height * offset_percentage * -2)

            # Calculate position for bottom right corner
            position = (width - watermark_width - offset_x, height - watermark_height - offset_y)
            image.paste(watermark, position, watermark)

            rgb_image = image.convert("RGB")
            rgb_image.save(converted_image_path)
            worker.progress.emit(round((i + 1) / progress_length * 100))

        print("Watermarking complete")

        QApplication.processEvents()
        return True
    except Exception as e:
        print(e)
        message = QMessageBox()
        message.setIcon(QMessageBox.Icon.Critical)
        message.setWindowTitle("Hiba")
        message.setText("Hiba történt a vízjelezés közben")
        message.exec()
        return False


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        message = QMessageBox()
        message.setIcon(QMessageBox.Icon.Critical)
        message.setWindowTitle("Fatal Error")
        message.setText(
            "A program futása közben hiba történt. Kérlek, próbáld újra. Ha a probléma továbbra is fennáll, jelezd légyszi a fejlesztőnek!")
        message.exec()
        sys.exit(1)
