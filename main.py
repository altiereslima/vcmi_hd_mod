#!/usr/bin/env python3
#
# MIT License
# 
# Copyright (c) 2024 Laserlicht
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QProgressBar, QFileDialog, QLabel)
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal
from extract import extract_assets
from create_mod import create_mod

class ExtractorThread(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, input_path, temp_path, output_path):
        super().__init__()
        self.input_path = input_path
        self.temp_path = temp_path
        self.output_path = output_path
        
    def run(self):
        try:
            extract_assets(self.input_path, self.temp_path)
            create_mod(self.temp_path, self.output_path)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class HOMM3Extractor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('HOMM3 Asset Extractor')
        self.setFixedSize(500, 300)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Labels to show selected paths
        self.input_label = QLabel('Input folder: Not selected')
        self.temp_label = QLabel('Temporary folder: Not selected')
        self.output_label = QLabel('Output folder: Not selected')
        
        # Directory selection buttons
        input_btn = QPushButton('Select Input Folder', self)
        input_btn.clicked.connect(lambda: self.select_folder('input'))
        
        temp_btn = QPushButton('Select Temporary Folder', self)
        temp_btn.clicked.connect(lambda: self.select_folder('temp'))
        
        output_btn = QPushButton('Select Output Folder', self)
        output_btn.clicked.connect(lambda: self.select_folder('output'))
        
        # Extract button
        self.extract_btn = QPushButton('Start Extraction', self)
        self.extract_btn.clicked.connect(self.start_extraction)
        self.extract_btn.setEnabled(False)
        
        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.hide()  # Initially hidden
        
        # Timer for progress bar animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        
        # Add widgets to layout
        layout.addWidget(self.input_label)
        layout.addWidget(input_btn)
        layout.addWidget(self.temp_label)
        layout.addWidget(temp_btn)
        layout.addWidget(self.output_label)
        layout.addWidget(output_btn)
        layout.addSpacing(20)
        layout.addWidget(self.extract_btn)
        layout.addWidget(self.progress_bar)
        
        # Initialize path variables
        self.input_path = None
        self.temp_path = None
        self.output_path = None
        self.thread = None
        
    def select_folder(self, folder_type):
        folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder:
            if folder_type == 'input':
                self.input_path = folder
                self.input_label.setText(f'Input folder: {folder}')
            elif folder_type == 'temp':
                self.temp_path = folder
                self.temp_label.setText(f'Temporary folder: {folder}')
            elif folder_type == 'output':
                self.output_path = folder
                self.output_label.setText(f'Output folder: {folder}')
                
        # Enable extract button only if all paths are selected
        if all([self.input_path, self.temp_path, self.output_path]):
            self.extract_btn.setEnabled(True)
    
    def update_progress(self):
        # Progress bar is in indeterminate mode, so no need
        # to do anything here, animation is automatic
        pass
    
    def extraction_completed(self):
        self.progress_bar.setRange(0, 100)  # Back to determinate mode
        self.progress_bar.setValue(100)
        self.extract_btn.setEnabled(True)
        self.extract_btn.setText('Start Extraction')
        
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, 'Success', 'Assets extracted and mod successfully created!')
        
        self.progress_bar.hide()
    
    def extraction_error(self, error):
        self.progress_bar.hide()
        self.extract_btn.setEnabled(True)
        self.extract_btn.setText('Start Extraction')
        
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, 'Error', f'An error occurred during extraction:\n{error}')
    
    def start_extraction(self):
        self.extract_btn.setEnabled(False)
        self.extract_btn.setText('Extracting...')
        self.progress_bar.show()
        
        # Create and start extraction thread
        self.thread = ExtractorThread(self.input_path, self.temp_path, self.output_path)
        self.thread.finished.connect(self.extraction_completed)
        self.thread.error.connect(self.extraction_error)
        self.thread.start()

def main():
    app = QApplication(sys.argv)
    
    # Application style
    app.setStyle('Fusion')
    
    ex = HOMM3Extractor()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()