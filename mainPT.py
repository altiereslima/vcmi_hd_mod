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

#!/usr/bin/env python3
# encoding: utf-8

import sys
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QProgressBar, QFileDialog, QLabel)
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal
from extract import extract_assets
from create_mod import create_mod

class ThreadExtrator(QThread):
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

class ExtratorHOMM3(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Extrator de Assets HOMM3')
        self.setFixedSize(500, 300)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Labels para mostrar os caminhos selecionados
        self.label_entrada = QLabel('Pasta de entrada: Não selecionada')
        self.label_temp = QLabel('Pasta temporária: Não selecionada')
        self.label_saida = QLabel('Pasta de saída: Não selecionada')
        
        # Botões para selecionar diretórios
        btn_entrada = QPushButton('Selecionar Pasta de Entrada', self)
        btn_entrada.clicked.connect(lambda: self.selecionar_pasta('entrada'))
        
        btn_temp = QPushButton('Selecionar Pasta Temporária', self)
        btn_temp.clicked.connect(lambda: self.selecionar_pasta('temp'))
        
        btn_saida = QPushButton('Selecionar Pasta de Saída', self)
        btn_saida.clicked.connect(lambda: self.selecionar_pasta('saida'))
        
        # Botão para iniciar extração
        self.btn_extrair = QPushButton('Iniciar Extração', self)
        self.btn_extrair.clicked.connect(self.iniciar_extracao)
        self.btn_extrair.setEnabled(False)
        
        # Barra de progresso
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)  # Modo indeterminado
        self.progress_bar.hide()  # Inicialmente escondida
        
        # Timer para animação da barra de progresso
        self.timer = QTimer()
        self.timer.timeout.connect(self.atualizar_progresso)
        
        # Adiciona widgets ao layout
        layout.addWidget(self.label_entrada)
        layout.addWidget(btn_entrada)
        layout.addWidget(self.label_temp)
        layout.addWidget(btn_temp)
        layout.addWidget(self.label_saida)
        layout.addWidget(btn_saida)
        layout.addSpacing(20)
        layout.addWidget(self.btn_extrair)
        layout.addWidget(self.progress_bar)
        
        # Inicializa variáveis para os caminhos
        self.input_path = None
        self.temp_path = None
        self.output_path = None
        self.thread = None
        
    def selecionar_pasta(self, tipo):
        pasta = QFileDialog.getExistingDirectory(self, 'Selecionar Pasta')
        if pasta:
            if tipo == 'entrada':
                self.input_path = pasta
                self.label_entrada.setText(f'Pasta de entrada: {pasta}')
            elif tipo == 'temp':
                self.temp_path = pasta
                self.label_temp.setText(f'Pasta temporária: {pasta}')
            elif tipo == 'saida':
                self.output_path = pasta
                self.label_saida.setText(f'Pasta de saída: {pasta}')
                
        # Habilita o botão de extração apenas se todos os caminhos estiverem selecionados
        if all([self.input_path, self.temp_path, self.output_path]):
            self.btn_extrair.setEnabled(True)
    
    def atualizar_progresso(self):
        # A barra já está no modo indeterminado, então não precisamos
        # fazer nada aqui, a animação é automática
        pass
    
    def extracao_concluida(self):
        self.progress_bar.setRange(0, 100)  # Volta para o modo determinado
        self.progress_bar.setValue(100)
        self.btn_extrair.setEnabled(True)
        self.btn_extrair.setText('Iniciar Extração')
        
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, 'Sucesso', 'Extração concluída e mod criado com sucesso!')
        
        self.progress_bar.hide()
    
    def erro_extracao(self, erro):
        self.progress_bar.hide()
        self.btn_extrair.setEnabled(True)
        self.btn_extrair.setText('Iniciar Extração')
        
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, 'Erro', f'Ocorreu um erro durante a extração:\n{erro}')
    
    def iniciar_extracao(self):
        self.btn_extrair.setEnabled(False)
        self.btn_extrair.setText('Extraindo...')
        self.progress_bar.show()
        
        # Cria e inicia a thread de extração
        self.thread = ThreadExtrator(self.input_path, self.temp_path, self.output_path)
        self.thread.finished.connect(self.extracao_concluida)
        self.thread.error.connect(self.erro_extracao)
        self.thread.start()

def main():
    app = QApplication(sys.argv)
    
    # Estilo para a aplicação
    app.setStyle('Fusion')
    
    ex = ExtratorHOMM3()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()