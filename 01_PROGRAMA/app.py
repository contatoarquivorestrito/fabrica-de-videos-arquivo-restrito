
import sys
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QStackedWidget, QProgressBar, QSizePolicy
)


class Card(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")

        self.layout_card = QVBoxLayout(self)
        self.layout_card.setContentsMargins(14, 12, 14, 12)
        self.layout_card.setSpacing(10)

        heading = QLabel(title)
        heading.setObjectName("CardTitle")
        self.layout_card.addWidget(heading)

    def add_content(self, widget):
        self.layout_card.addWidget(widget)


class RecordingPage(QWidget):
    def __init__(self):
        super().__init__()

        main = QVBoxLayout(self)
        main.setContentsMargins(22, 15, 22, 18)
        main.setSpacing(13)

        title = QLabel("▣  Estúdio de Gravação")
        title.setObjectName("PageTitle")
        main.addWidget(title)

        # Primeira linha
        top = QHBoxLayout()
        top.setSpacing(14)

        camera = Card("PRÉ-VISUALIZAÇÃO DA CÂMERA")

        preview = QFrame()
        preview.setObjectName("CameraPreview")
        preview_layout = QVBoxLayout(preview)

        live = QLabel("●  CÂMERA — AGUARDANDO CONEXÃO")
        live.setObjectName("LiveLabel")
        preview_layout.addWidget(live)

        camera_text = QLabel("PRÉ-VISUALIZAÇÃO")
        camera_text.setObjectName("PreviewText")
        camera_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(camera_text, 1)

        resolution = QLabel("16:9   |   1080p   |   30 fps")
        resolution.setObjectName("Muted")
        preview_layout.addWidget(resolution)

        camera.add_content(preview)
        camera.setMinimumHeight(265)

        audio = Card("ÁUDIO")
        audio_status = QLabel("●  Aguardando dispositivo")
        audio_status.setObjectName("Muted")
        audio.add_content(audio_status)

        meter = QProgressBar()
        meter.setRange(0, 100)
        meter.setValue(0)
        meter.setTextVisible(False)
        meter.setObjectName("AudioMeter")
        audio.add_content(meter)

        audio.setMaximumWidth(175)
        audio.setMinimumHeight(265)

        stories = Card("HISTÓRIAS DA SESSÃO")
        story_status = QLabel("Nenhuma história inserida.")
        story_status.setObjectName("Muted")
        stories.add_content(story_status)

        add_story = QPushButton("+  Inserir Histórias")
        add_story.setObjectName("SecondaryButton")
        stories.add_content(add_story)
        stories.setMinimumWidth(220)
        stories.setMinimumHeight(265)

        top.addWidget(camera, 5)
        top.addWidget(audio, 1)
        top.addWidget(stories, 3)
        main.addLayout(top)

        # Estrutura da gravação
        structure = Card("ESTRUTURA DA GRAVAÇÃO")
        stages = QHBoxLayout()

        self.stage_buttons = []

        for name in ["Início", "Relato 1", "Relato 2",
                     "Adicionar Relato", "Final"]:
            button = QPushButton(name)
            button.setObjectName("StageButton")
            button.setMinimumHeight(65)
            stages.addWidget(button)
            self.stage_buttons.append(button)

        stages.itemAt(1).widget().setObjectName("ActiveStage")
        structure.add_content_widget = None
        structure.layout_card.addLayout(stages)
        main.addWidget(structure)

        # Leitura e monitoramento
        bottom = QHBoxLayout()
        bottom.setSpacing(14)

        reading = Card("▤  LEITURA ASSISTIDA")
        paragraph = QLabel(
            "Aguardando seleção de uma história para iniciar a leitura."
        )
        paragraph.setObjectName("ReadingText")
        paragraph.setWordWrap(True)
        reading.add_content(paragraph)

        monitoring = Card("MONITORAMENTO DA NARRAÇÃO (IA)")

        for item in [
            "●  Acompanhando o texto",
            "●  Detectando releituras",
            "●  Identificando possíveis erros",
            "●  Selecionando a melhor leitura"
        ]:
            label = QLabel(item)
            label.setObjectName("Muted")
            monitoring.add_content(label)

        bottom.addWidget(reading, 3)
        bottom.addWidget(monitoring, 2)
        main.addLayout(bottom)

        # Controles
        controls = QHBoxLayout()
        controls.setSpacing(14)

        start = QPushButton("●  Iniciar Gravação")
        start.setObjectName("PrimaryButton")

        pause = QPushButton("Ⅱ  Pausar")
        pause.setObjectName("SecondaryButton")

        finish = QPushButton("■  Encerrar Sessão")
        finish.setObjectName("SecondaryButton")

        controls.addWidget(start, 2)
        controls.addWidget(pause, 1)
        controls.addWidget(finish, 1)

        main.addLayout(controls)


class PlaceholderPage(QWidget):
    def __init__(self, name, description):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 25, 28, 25)

        title = QLabel(name)
        title.setObjectName("PageTitle")

        description_label = QLabel(description)
        description_label.setObjectName("Muted")
        description_label.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description_label)
        layout.addStretch()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ARQUIVO RESTRITO — Fábrica de Vídeos")
        self.resize(1500, 900)
        self.setMinimumSize(1100, 700)

        root = QWidget()
        self.setCentralWidget(root)

        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # CABEÇALHO FIXO
        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(105)

        header_layout = QVBoxLayout(header)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


        # IMAGEM OFICIAL DO CABEÇALHO
        header_image = QLabel()
        image_path = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "header_arquivo_restrito.png"
        )
        header_image.setPixmap(QPixmap(image_path))
        header_image.setScaledContents(True)
        header_image.setFixedHeight(105)
        header_image.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        header_layout.addWidget(header_image)


        main_layout.addWidget(header)

        # ÁREA CENTRAL
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # MENU LATERAL FIXO
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(255)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(9, 18, 9, 15)
        sidebar_layout.setSpacing(9)

        # PÁGINAS
        self.pages = QStackedWidget()
        self.pages.setObjectName("ContentArea")

        menu_items = [
            ("⌂", "Home", "Painel geral do sistema."),
            ("▦", "Biblioteca de Histórias",
             "Gerenciamento de histórias e relatos."),
            ("◉", "Gravação", ""),
            ("⚒", "Edição Automática",
             "Ferramentas de edição e montagem."),
            ("⊕", "Cortes (Reels/Shorts)",
             "Criação de vídeos curtos."),
            ("♧", "Microdocumentários",
             "Produção de documentários."),
            ("▱", "Projetos",
             "Gerenciamento de projetos."),
            ("⚙", "Configurações",
             "Configurações gerais do sistema.")
        ]

        self.navigation_buttons = []

        for index, (icon, name, description) in enumerate(menu_items):

            if name == "Gravação":
                page = RecordingPage()
            else:
                page = PlaceholderPage(name, description)

            self.pages.addWidget(page)

            button = QPushButton(f"{icon}   {name}")
            button.setObjectName("NavButton")
            button.setMinimumHeight(53)
            button.setCursor(Qt.CursorShape.PointingHandCursor)

            button.clicked.connect(
                lambda checked=False, i=index: self.change_page(i)
            )

            sidebar_layout.addWidget(button)
            self.navigation_buttons.append(button)

        sidebar_layout.addStretch()

        body.addWidget(sidebar)
        body.addWidget(self.pages, 1)

        main_layout.addLayout(body, 1)

        # RODAPÉ
        footer = QFrame()
        footer.setObjectName("Footer")
        footer.setFixedHeight(36)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(18, 0, 18, 0)

        status = QLabel("●  SISTEMA INICIADO")
        status.setObjectName("StatusLabel")

        footer_layout.addWidget(status)
        footer_layout.addStretch()

        main_layout.addWidget(footer)

        self.change_page(2)

    def change_page(self, index):
        self.pages.setCurrentIndex(index)

        for i, button in enumerate(self.navigation_buttons):
            button.setObjectName(
                "ActiveNav" if i == index else "NavButton"
            )
            button.style().unpolish(button)
            button.style().polish(button)


STYLESHEET = """
QMainWindow, QWidget {
    background-color: #080D12;
    color: #E8E9EC;
    font-family: Segoe UI;
    font-size: 14px;
}

QLabel {
    background-color: transparent;
    color: #E8E9EC;
}

#Header {
    background-color: #101820;
    border-bottom: 2px solid #8F171B;
}

#Brand {
    color: #F4F1EE;
    font-size: 32px;
    font-weight: 900;
    letter-spacing: 3px;
}

#BrandSubtitle {
    color: #C5C7CB;
    font-size: 13px;
    font-weight: bold;
}

#Sidebar {
    background-color: #0C131B;
    border-right: 1px solid #27313B;
}

#NavButton {
    background-color: transparent;
    color: #D1D5DA;
    border: none;
    border-radius: 9px;
    text-align: left;
    padding-left: 15px;
    font-weight: bold;
}

#NavButton:hover {
    background-color: #202A34;
}

#ActiveNav {
    background-color: #351619;
    color: #FFBFC0;
    border: 1px solid #671B20;
    border-radius: 9px;
    text-align: left;
    padding-left: 15px;
    font-weight: bold;
}

#ContentArea {
    background-color: #080D12;
}

#PageTitle {
    color: #F0F0F0;
    font-size: 25px;
    font-weight: bold;
}

#Card {
    background-color: #111A23;
    border: 1px solid #303C49;
    border-radius: 12px;
}

#CardTitle {
    color: #FFFFFF;
    font-size: 16px;
    font-weight: bold;
    padding-bottom: 5px;
}

#CameraPreview {
    background-color: #05080C;
    border: 1px solid #263440;
    border-radius: 9px;
}

#PreviewText {
    color: #737F8B;
    font-size: 22px;
    font-weight: bold;
}

#LiveLabel {
    color: #65D68A;
    font-weight: bold;
}

#Muted {
    color: #A7B0BB;
}

#ReadingText {
    background-color: #282115;
    color: #F5E5B8;
    border: 1px solid #765B25;
    border-radius: 7px;
    padding: 14px;
    font-size: 15px;
}

#AudioMeter {
    min-height: 130px;
    max-width: 35px;
}

#AudioMeter::chunk {
    background-color: #20CA58;
}

#StageButton, #SecondaryButton {
    background-color: #19232D;
    color: #F0F0F0;
    border: 1px solid #384552;
    border-radius: 9px;
    padding: 12px;
    font-weight: bold;
}

#StageButton:hover, #SecondaryButton:hover {
    background-color: #273544;
}

#ActiveStage {
    background-color: #49171B;
    color: #FFB9BA;
    border: 1px solid #B01C25;
    border-radius: 9px;
    padding: 12px;
    font-weight: bold;
}

#PrimaryButton {
    background-color: #B9000B;
    color: white;
    border: 1px solid #EF3038;
    border-radius: 12px;
    padding: 15px;
    font-size: 16px;
    font-weight: bold;
}

#PrimaryButton:hover {
    background-color: #D71924;
}

#Footer {
    background-color: #101820;
    border-top: 1px solid #303A45;
}

#StatusLabel {
    color: #55D66C;
    font-weight: bold;
}
"""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())
