import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel
)

app = QApplication(sys.argv)

janela = QWidget()
janela.setWindowTitle("Fábrica de Vídeos — Arquivo Restrito")
janela.resize(900, 550)

layout = QVBoxLayout()

titulo = QLabel("FÁBRICA DE VÍDEOS")
titulo.setStyleSheet("""
    font-size: 30px;
    font-weight: bold;
    color: #D4AF37;
""")

subtitulo = QLabel("Ambiente gráfico iniciado com sucesso!")

layout.addWidget(titulo)
layout.addWidget(subtitulo)

janela.setLayout(layout)
janela.show()

sys.exit(app.exec())