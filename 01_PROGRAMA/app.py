import html
import json
import os
import random
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QStandardPaths, QUrl
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QStackedWidget,
    QSizePolicy,
    QMessageBox,
    QLineEdit,
    QTextEdit,
    QTextBrowser,
    QScrollArea,
    QComboBox,
    QFileDialog,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QSlider,
    QCheckBox,
    QProgressBar,
)

# Qt Multimedia é opcional nesta etapa. Se estiver instalado, o mini-player
# reproduz arquivos locais. A captura real de câmera/microfone será integrada
# em uma etapa posterior.
try:
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaDevices
    from PySide6.QtMultimediaWidgets import QVideoWidget
    MULTIMEDIA_AVAILABLE = True
except Exception:
    QMediaPlayer = None
    QAudioOutput = None
    QMediaDevices = None
    QVideoWidget = None
    MULTIMEDIA_AVAILABLE = False


APP_NAME = "Arquivo Restrito"
REFERENCE_WIDTH = 1672
UI_SCALE = 1.0


def configure_ui_scale():
    global UI_SCALE
    screen = QApplication.primaryScreen()
    if screen is not None:
        width = screen.availableGeometry().width()
        UI_SCALE = max(0.88, min(1.30, width / REFERENCE_WIDTH))
    else:
        UI_SCALE = 1.0


def px(value):
    return max(1, int(round(value * UI_SCALE)))


def scaled_stylesheet(stylesheet):
    return re.sub(
        r"(\d+(?:\.\d+)?)px",
        lambda match: f"{px(float(match.group(1)))}px",
        stylesheet,
    )


def now_text():
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def split_paragraphs(text):
    return [part.strip() for part in re.split(r"\n\s*\n", text or "") if part.strip()]


class ProjectStore:
    """Armazena episódios/projetos localmente, fora da pasta publicada no GitHub."""

    def __init__(self):
        base = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation
        )
        if not base:
            base = str(Path.home() / ".arquivo_restrito")
        self.directory = Path(base)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.file_path = self.directory / "projetos.json"

    def _normalize_section(self, section, index):
        section = dict(section or {})
        section.setdefault("id", str(uuid.uuid4()))
        section.setdefault("title", f"Relato {index}")
        # Migração segura: o texto antigo passa para o campo Resumo, sem perda.
        if not any(section.get(key) for key in ("summary", "terror", "ending")):
            section["summary"] = section.get("text", "")
        section.setdefault("summary", "")
        section.setdefault("terror", "")
        section.setdefault("ending", "")
        section.setdefault("protagonist", "")
        section.setdefault("age", "")
        section.setdefault("protagonist_gender", "Feminino")
        section.setdefault("female_names", [])
        section.setdefault("male_names", [])
        section.setdefault("allow_compound", False)
        section.setdefault("harmony_status", "Aguardando verificação de harmonia")
        section.setdefault("versions", [])
        section.setdefault("saved_at", "")
        section["text"] = section_text(section)
        return section

    def _normalize_project(self, project):
        project = dict(project or {})
        project.setdefault("id", str(uuid.uuid4()))
        project.setdefault("title", project.get("theme", "Projeto sem título"))
        project.setdefault("theme", project.get("title", ""))
        project.setdefault("status", "Em desenvolvimento")
        project.setdefault("created_at", now_text())
        project.setdefault("updated_at", now_text())
        project.setdefault("duration", "1h30min")
        project.setdefault("duration_minutes", 90)
        project.setdefault("report_count", len(project.get("sections", [])) or 1)
        project.setdefault("prompt_id", "")
        project.setdefault("prompt_name", "Prompt Mestre")
        project.setdefault("master_prompt", "")
        project.setdefault("recordings", [])
        project["sections"] = [
            self._normalize_section(section, index)
            for index, section in enumerate(project.get("sections", []), start=1)
        ]
        if not project["sections"]:
            project["sections"] = [self._normalize_section({}, 1)]
        project["report_count"] = len(project["sections"])
        return project

    def all(self):
        if not self.file_path.exists():
            return []
        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                return []
            return [self._normalize_project(item) for item in data if isinstance(item, dict)]
        except (OSError, json.JSONDecodeError):
            return []

    def get(self, project_id):
        return next((p for p in self.all() if p.get("id") == project_id), None)

    def save(self, project):
        project = self._normalize_project(project)
        projects = self.all()
        existing_index = next(
            (i for i, item in enumerate(projects) if item.get("id") == project.get("id")),
            None,
        )
        if existing_index is None:
            projects.insert(0, project)
        else:
            projects[existing_index] = project
        temp_path = self.file_path.with_suffix(".tmp")
        temp_path.write_text(
            json.dumps(projects, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp_path.replace(self.file_path)
        return project

    def delete(self, project_id):
        projects = [p for p in self.all() if p.get("id") != project_id]
        temp_path = self.file_path.with_suffix(".tmp")
        temp_path.write_text(
            json.dumps(projects, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp_path.replace(self.file_path)

    def new_project(self):
        stamp = now_text()
        return {
            "id": str(uuid.uuid4()),
            "title": "",
            "theme": "",
            "status": "Em criação",
            "created_at": stamp,
            "updated_at": stamp,
            "duration": "1h30min",
            "duration_minutes": 90,
            "report_count": 1,
            "prompt_id": "",
            "prompt_name": "Prompt Mestre",
            "master_prompt": "",
            "sections": [self._normalize_section({}, 1)],
            "recordings": [],
        }


def section_text(section):
    """Texto em ordem para o teleprompter, com compatibilidade ao formato antigo."""
    fields = [
        (section or {}).get("summary", ""),
        (section or {}).get("terror", ""),
        (section or {}).get("ending", ""),
    ]
    combined = "\n\n".join(value.strip() for value in fields if value and value.strip())
    return combined or (section or {}).get("text", "")


def duration_minutes(label):
    mapping = {
        "10 minutos": 10, "20 minutos": 20, "30 minutos": 30,
        "35 minutos": 35, "40 minutos": 40, "45 minutos": 45,
        "1 hora": 60, "1h20min": 80, "1h30min": 90,
        "1h40min": 100, "1h45min": 105, "1h50min": 110,
        "2 horas": 120, "2h30min": 150,
    }
    return mapping.get(label, 90)


class Panel(QFrame):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.panel_layout = QVBoxLayout(self)
        self.panel_layout.setContentsMargins(px(12), px(10), px(12), px(10))
        self.panel_layout.setSpacing(px(8))
        if title:
            heading = QLabel(title)
            heading.setObjectName("PanelTitle")
            self.panel_layout.addWidget(heading)


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget is not None:
            widget.deleteLater()
        elif child_layout is not None:
            clear_layout(child_layout)


class ProjectCard(QFrame):
    def __init__(self, project, on_open, compact=False, parent=None):
        super().__init__(parent)
        self.setObjectName("ProjectCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(self) if compact else QVBoxLayout(self)
        layout.setContentsMargins(px(14), px(12), px(14), px(12))
        layout.setSpacing(px(8))

        top = QHBoxLayout()
        icon = QLabel("▣")
        icon.setObjectName("ProjectIcon")
        title = QLabel(project.get("title") or "Projeto sem título")
        title.setObjectName("ProjectTitle")
        title.setWordWrap(True)
        top.addWidget(icon)
        top.addWidget(title, 1)
        status = QLabel(project.get("status", "Rascunho"))
        status.setObjectName("ProjectStatus")
        top.addWidget(status)
        layout.addLayout(top)

        sections = project.get("sections", [])
        count = len(sections)
        updated = project.get("updated_at", "")
        info = QLabel(f"{count} relato(s)  •  Atualizado: {updated}")
        info.setObjectName("Muted")
        layout.addWidget(info)

        if not compact:
            summary = " ".join(
                split_paragraphs("\n\n".join(section_text(s) for s in sections))[:1]
            )
            if summary:
                summary_label = QLabel(summary[:150] + ("…" if len(summary) > 150 else ""))
                summary_label.setObjectName("ProjectSummary")
                summary_label.setWordWrap(True)
                layout.addWidget(summary_label)

        open_button = QPushButton("Abrir projeto  →" if not compact else "Abrir →")
        open_button.setObjectName("SmallRedButton")
        open_button.setCursor(Qt.CursorShape.PointingHandCursor)
        open_button.clicked.connect(lambda: on_open(project.get("id")))
        if compact:
            layout.addWidget(open_button)
        else:
            layout.addStretch()
            layout.addWidget(open_button)


class ProjectHomePage(QWidget):
    def __init__(self, store, on_open_project, on_new_project):
        super().__init__()
        self.store = store
        self.on_open_project = on_open_project
        self.on_new_project = on_new_project
        self.view_mode = "grid"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(px(24), px(20), px(24), px(20))
        outer.setSpacing(px(14))

        header = QHBoxLayout()
        heading_box = QVBoxLayout()
        title = QLabel("Meus Projetos")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Cada projeto representa um vídeo do seu canal.")
        subtitle.setObjectName("Muted")
        heading_box.addWidget(title)
        heading_box.addWidget(subtitle)
        header.addLayout(heading_box, 1)

        self.new_button = QPushButton("＋  Criar Novo Episódio")
        self.new_button.setObjectName("PrimaryButton")
        self.new_button.clicked.connect(self.on_new_project)
        header.addWidget(self.new_button)
        outer.addLayout(header)

        tools = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setObjectName("SearchInput")
        self.search.setPlaceholderText("Buscar roteiro ou projeto...")
        self.search.textChanged.connect(self.refresh)
        tools.addWidget(self.search, 1)

        self.grid_button = QPushButton("▦  Grade")
        self.grid_button.setObjectName("ViewToggleActive")
        self.list_button = QPushButton("☷  Lista")
        self.list_button.setObjectName("ViewToggle")
        self.grid_button.clicked.connect(lambda: self.set_view("grid"))
        self.list_button.clicked.connect(lambda: self.set_view("list"))
        tools.addWidget(self.grid_button)
        tools.addWidget(self.list_button)
        outer.addLayout(tools)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.content = QWidget()
        self.content_layout = QGridLayout(self.content)
        self.content_layout.setContentsMargins(0, px(4), 0, px(4))
        self.content_layout.setSpacing(px(14))
        self.scroll.setWidget(self.content)
        outer.addWidget(self.scroll, 1)
        self.refresh()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "content_layout"):
            self.refresh()

    def set_view(self, mode):
        self.view_mode = mode
        self.grid_button.setObjectName("ViewToggleActive" if mode == "grid" else "ViewToggle")
        self.list_button.setObjectName("ViewToggleActive" if mode == "list" else "ViewToggle")
        self.grid_button.style().unpolish(self.grid_button)
        self.grid_button.style().polish(self.grid_button)
        self.list_button.style().unpolish(self.list_button)
        self.list_button.style().polish(self.list_button)
        self.refresh()

    def refresh(self):
        clear_layout(self.content_layout)
        query = self.search.text().strip().lower()
        projects = self.store.all()
        if query:
            projects = [p for p in projects if query in p.get("title", "").lower()]

        if not projects:
            empty = QFrame()
            empty.setObjectName("EmptyState")
            empty_layout = QVBoxLayout(empty)
            empty_layout.setContentsMargins(px(24), px(34), px(24), px(34))
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_icon = QLabel("▣")
            empty_icon.setObjectName("EmptyIcon")
            empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            message = QLabel(
                "Nenhum projeto encontrado.\nCrie um roteiro e ele ficará salvo aqui para você continuar outro dia."
            )
            message.setObjectName("EmptyText")
            message.setAlignment(Qt.AlignmentFlag.AlignCenter)
            message.setWordWrap(True)
            create = QPushButton("＋  Criar primeiro episódio")
            create.setObjectName("PrimaryButton")
            create.clicked.connect(self.on_new_project)
            empty_layout.addWidget(empty_icon)
            empty_layout.addWidget(message)
            empty_layout.addWidget(create, 0, Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(empty, 0, 0, 1, 3)
            return

        if self.view_mode == "grid":
            width = max(1, self.scroll.viewport().width())
            columns = 3 if width >= px(1100) else 2 if width >= px(680) else 1
            for index, project in enumerate(projects):
                card = ProjectCard(project, self.on_open_project, compact=False)
                self.content_layout.addWidget(card, index // columns, index % columns)
            for col in range(columns):
                self.content_layout.setColumnStretch(col, 1)
        else:
            for index, project in enumerate(projects):
                card = ProjectCard(project, self.on_open_project, compact=True)
                self.content_layout.addWidget(card, index, 0)
            self.content_layout.setColumnStretch(0, 1)
        self.content_layout.setRowStretch(self.content_layout.rowCount(), 1)


class PromptStore:
    """Biblioteca local de prompts. O Prompt Mestre é preenchido pelo usuário."""

    def __init__(self, directory):
        self.directory = Path(directory)
        self.file_path = self.directory / "prompts.json"

    def all(self):
        if not self.file_path.exists():
            return [{
                "id": "prompt-mestre-padrao",
                "name": "Prompt Mestre",
                "content": "",
                "is_default": True,
                "updated_at": "Ainda não configurado",
            }]
        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            if isinstance(data, list) and data:
                return data
        except (OSError, json.JSONDecodeError):
            pass
        return [{
            "id": "prompt-mestre-padrao",
            "name": "Prompt Mestre",
            "content": "",
            "is_default": True,
            "updated_at": "Ainda não configurado",
        }]

    def get(self, prompt_id):
        return next((p for p in self.all() if p.get("id") == prompt_id), None)

    def default(self):
        prompts = self.all()
        return next((p for p in prompts if p.get("is_default")), prompts[0])

    def save(self, prompt):
        prompts = self.all()
        prompt = dict(prompt)
        prompt["updated_at"] = now_text()
        if prompt.get("is_default"):
            for item in prompts:
                item["is_default"] = False
        index = next((i for i, item in enumerate(prompts) if item.get("id") == prompt.get("id")), None)
        if index is None:
            prompts.insert(0, prompt)
        else:
            prompts[index] = prompt
        self._write(prompts)
        return prompt

    def delete(self, prompt_id):
        prompts = [p for p in self.all() if p.get("id") != prompt_id]
        if not prompts:
            prompts = [{
                "id": "prompt-mestre-padrao", "name": "Prompt Mestre",
                "content": "", "is_default": True, "updated_at": "Ainda não configurado",
            }]
        elif not any(p.get("is_default") for p in prompts):
            prompts[0]["is_default"] = True
        self._write(prompts)

    def _write(self, prompts):
        temp = self.file_path.with_suffix(".tmp")
        temp.write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(self.file_path)


class PromptSelectDialog(QDialog):
    def __init__(self, prompt_store, selected_id="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Carregar Prompt")
        self.setMinimumSize(px(540), px(430))
        self.prompts = prompt_store.all()
        layout = QVBoxLayout(self)
        title = QLabel("Selecione o prompt que orientará a criação deste episódio.")
        title.setObjectName("Muted")
        title.setWordWrap(True)
        layout.addWidget(title)
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("ProjectPicker")
        for prompt in self.prompts:
            state = " • PRINCIPAL" if prompt.get("is_default") else ""
            content_state = "configurado" if prompt.get("content", "").strip() else "sem conteúdo cadastrado"
            item = QListWidgetItem(f"{prompt.get('name', 'Prompt')} — {content_state}{state}")
            item.setData(Qt.ItemDataRole.UserRole, prompt.get("id"))
            self.list_widget.addItem(item)
            if prompt.get("id") == selected_id:
                self.list_widget.setCurrentItem(item)
        if self.list_widget.currentRow() < 0 and self.list_widget.count():
            self.list_widget.setCurrentRow(0)
        layout.addWidget(self.list_widget, 1)
        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.setObjectName("SecondaryButton")
        cancel.clicked.connect(self.reject)
        choose = QPushButton("Carregar selecionado")
        choose.setObjectName("PrimaryButton")
        choose.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(choose)
        layout.addLayout(buttons)

    def selected_id(self):
        item = self.list_widget.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None


class PromptPreviewDialog(QDialog):
    def __init__(self, title, prompt_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(px(780), px(620))
        layout = QVBoxLayout(self)
        note = QLabel(
            "Este é o prompt preparado com as informações do episódio. "
            "A geração automática por IA ainda não está conectada nesta versão."
        )
        note.setObjectName("Muted")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.text = QTextEdit()
        self.text.setObjectName("EditorText")
        self.text.setPlainText(prompt_text)
        layout.addWidget(self.text, 1)
        buttons = QHBoxLayout()
        buttons.addStretch()
        close = QPushButton("Fechar")
        close.setObjectName("SecondaryButton")
        close.clicked.connect(self.reject)
        copy = QPushButton("Copiar prompt")
        copy.setObjectName("PrimaryButton")
        copy.clicked.connect(self.copy_prompt)
        buttons.addWidget(close)
        buttons.addWidget(copy)
        layout.addLayout(buttons)

    def copy_prompt(self):
        QApplication.clipboard().setText(self.text.toPlainText())
        QMessageBox.information(self, "Prompt copiado", "O prompt foi copiado para a área de transferência.")


class PromptLibraryPage(QWidget):
    def __init__(self, prompt_store):
        super().__init__()
        self.prompt_store = prompt_store
        self.current_prompt = None
        outer = QVBoxLayout(self)
        outer.setContentsMargins(px(24), px(20), px(24), px(20))
        outer.setSpacing(px(12))
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Prompts")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Gerencie o Prompt Mestre e outros modelos usados na criação dos episódios.")
        subtitle.setObjectName("Muted")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box, 1)
        new_button = QPushButton("＋  Novo Prompt")
        new_button.setObjectName("PrimaryButton")
        new_button.clicked.connect(self.new_prompt)
        header.addWidget(new_button)
        outer.addLayout(header)

        body = QHBoxLayout()
        left = Panel("BIBLIOTECA DE PROMPTS")
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("ProjectPicker")
        self.list_widget.currentRowChanged.connect(self.load_selected)
        left.panel_layout.addWidget(self.list_widget, 1)
        body.addWidget(left, 2)

        right = Panel("EDITOR DO PROMPT")
        self.name_edit = QLineEdit()
        self.name_edit.setObjectName("EditorInput")
        self.name_edit.setPlaceholderText("Nome do prompt")
        right.panel_layout.addWidget(QLabel("NOME"))
        right.panel_layout.addWidget(self.name_edit)
        right.panel_layout.addWidget(QLabel("CONTEÚDO / INSTRUÇÕES"))
        self.content_edit = QTextEdit()
        self.content_edit.setObjectName("EditorText")
        self.content_edit.setPlaceholderText("Cole aqui o conteúdo integral do seu Prompt Mestre...")
        right.panel_layout.addWidget(self.content_edit, 1)
        self.default_check = QCheckBox("Definir como Prompt Mestre principal")
        self.default_check.setObjectName("PromptCheck")
        right.panel_layout.addWidget(self.default_check)
        actions = QHBoxLayout()
        self.status = QLabel("As alterações serão salvas localmente.")
        self.status.setObjectName("Muted")
        actions.addWidget(self.status, 1)
        delete = QPushButton("Excluir")
        delete.setObjectName("DangerButton")
        delete.clicked.connect(self.delete_prompt)
        save = QPushButton("Salvar Prompt")
        save.setObjectName("PrimaryButton")
        save.clicked.connect(self.save_prompt)
        actions.addWidget(delete)
        actions.addWidget(save)
        right.panel_layout.addLayout(actions)
        body.addWidget(right, 5)
        outer.addLayout(body, 1)
        self.refresh()

    def refresh(self, select_id=None):
        prompts = self.prompt_store.all()
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        target = 0
        for index, prompt in enumerate(prompts):
            marker = " ★" if prompt.get("is_default") else ""
            configured = "Configurado" if prompt.get("content", "").strip() else "Pendente"
            item = QListWidgetItem(f"{prompt.get('name', 'Prompt')}  |  {configured}{marker}")
            item.setData(Qt.ItemDataRole.UserRole, prompt.get("id"))
            self.list_widget.addItem(item)
            if prompt.get("id") == select_id:
                target = index
        self.list_widget.setCurrentRow(target)
        self.list_widget.blockSignals(False)
        self.load_selected(target)

    def load_selected(self, row):
        prompts = self.prompt_store.all()
        if not (0 <= row < len(prompts)):
            self.current_prompt = None
            self.name_edit.clear()
            self.content_edit.clear()
            self.default_check.setChecked(False)
            return
        self.current_prompt = prompts[row]
        self.name_edit.setText(self.current_prompt.get("name", ""))
        self.content_edit.setPlainText(self.current_prompt.get("content", ""))
        self.default_check.setChecked(bool(self.current_prompt.get("is_default")))
        if not self.current_prompt.get("content", "").strip():
            self.status.setText("Prompt sem conteúdo: cole as instruções aprovadas para ativá-lo.")
        else:
            self.status.setText(f"Atualizado: {self.current_prompt.get('updated_at', '—')}")

    def new_prompt(self):
        self.current_prompt = {"id": str(uuid.uuid4()), "name": "Novo Prompt", "content": "", "is_default": False}
        self.name_edit.setText("Novo Prompt")
        self.content_edit.clear()
        self.default_check.setChecked(False)
        self.list_widget.clearSelection()
        self.status.setText("Novo prompt ainda não salvo.")

    def save_prompt(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Nome obrigatório", "Informe um nome para o prompt.")
            return
        prompt = dict(self.current_prompt or {"id": str(uuid.uuid4())})
        prompt.update({
            "name": name,
            "content": self.content_edit.toPlainText().strip(),
            "is_default": self.default_check.isChecked(),
        })
        saved = self.prompt_store.save(prompt)
        self.status.setText(f"Prompt salvo em {saved.get('updated_at')}.")
        self.refresh(saved.get("id"))

    def delete_prompt(self):
        if not self.current_prompt:
            return
        answer = QMessageBox.question(
            self, "Excluir prompt", "Deseja realmente excluir este prompt?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.prompt_store.delete(self.current_prompt.get("id"))
            self.refresh()


FEMALE_NAMES = ["Cláudia", "Renata", "Patrícia", "Helena", "Mariana", "Isabela", "Camila", "Beatriz", "Júlia", "Teresa", "Marta", "Luciana", "Aline", "Sônia", "Elisa"]
MALE_NAMES = ["Marcelo", "Paulo", "Roberto", "André", "Ricardo", "Eduardo", "Fábio", "Henrique", "Samuel", "Antônio", "Gustavo", "Rafael", "Vinícius", "Daniel", "Otávio"]


def make_random_name(gender, compound=False, exclude=None):
    pool = FEMALE_NAMES if gender == "Feminino" else MALE_NAMES
    available = [name for name in pool if name not in (exclude or [])] or pool
    name = random.choice(available)
    if compound and random.random() < 0.28:
        second_pool = [n for n in pool if n != name]
        name += " " + random.choice(second_pool)
    return name


class CharacterNameRow(QFrame):
    def __init__(self, name, on_refresh, on_remove, protagonist=False, parent=None):
        super().__init__(parent)
        self.setObjectName("ProtagonistNameRow" if protagonist else "CharacterNameRow")
        self.on_refresh = on_refresh
        self.on_remove = on_remove
        self.name_edit = QLineEdit(name)
        self.name_edit.setObjectName("CharacterNameInput")
        self.name_edit.setReadOnly(True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(px(6), px(3), px(5), px(3))
        layout.setSpacing(px(4))
        layout.addWidget(self.name_edit, 1)
        refresh = QPushButton("↻")
        refresh.setObjectName("MiniActionButton")
        refresh.setToolTip("Sortear outro nome")
        refresh.clicked.connect(self.on_refresh)
        edit = QPushButton("✎")
        edit.setObjectName("MiniActionButton")
        edit.setToolTip("Editar nome")
        edit.clicked.connect(self.toggle_edit)
        remove = QPushButton("×")
        remove.setObjectName("MiniActionButton")
        remove.setToolTip("Remover personagem")
        remove.clicked.connect(self.on_remove)
        layout.addWidget(refresh)
        layout.addWidget(edit)
        layout.addWidget(remove)

    def toggle_edit(self):
        self.name_edit.setReadOnly(not self.name_edit.isReadOnly())
        if not self.name_edit.isReadOnly():
            self.name_edit.setFocus()
            self.name_edit.selectAll()
        else:
            self.name_edit.setText(self.name_edit.text().strip())

    def value(self):
        return self.name_edit.text().strip()


class ReportEditor(QFrame):
    def __init__(self, section, index, theme, master_prompt, on_save, on_prompt, on_changed, parent=None):
        super().__init__(parent)
        self.setObjectName("ReportCard")
        self.section = dict(section or {})
        self.index = index
        self.theme = theme
        self.master_prompt = master_prompt
        self.on_save = on_save
        self.on_prompt = on_prompt
        self.on_changed = on_changed
        self.female_rows = []
        self.male_rows = []
        self.last_changed_field = "summary"
        self._loading = True

        outer = QVBoxLayout(self)
        outer.setContentsMargins(px(14), px(12), px(14), px(12))
        outer.setSpacing(px(8))

        header = QHBoxLayout()
        number = QLabel(f"RELATO {index:02d}")
        number.setObjectName("ReportNumber")
        header.addWidget(number)
        header.addStretch()
        recreate = QPushButton("↻  RECRIAR RELATO")
        recreate.setObjectName("SmallRedButton")
        recreate.setToolTip("Preparar a recriação completa somente deste relato, mantendo tema e Prompt Mestre")
        recreate.clicked.connect(self.prepare_recreate)
        header.addWidget(recreate)
        outer.addLayout(header)

        title_row = QHBoxLayout()
        self.title_edit = QLineEdit(self.section.get("title", f"Relato {index}"))
        self.title_edit.setObjectName("ReportTitleInput")
        self.title_edit.setPlaceholderText("Título do relato")
        self.title_edit.textChanged.connect(lambda: self.changed("title"))
        title_row.addWidget(self.title_edit, 1)
        title_refresh = QPushButton("↻")
        title_refresh.setObjectName("MiniActionButton")
        title_refresh.setToolTip("Preparar sugestão de novo título")
        title_refresh.clicked.connect(self.prepare_title_prompt)
        title_row.addWidget(title_refresh)
        outer.addLayout(title_row)

        self.summary_edit = self.add_text_field(outer, "RESUMO DO RELATO", "summary", self.section.get("summary", self.section.get("text", "")), 118)
        protagonist_row = QHBoxLayout()
        protagonist_label = QLabel("PROTAGONISTA:")
        protagonist_label.setObjectName("ProtagonistCaption")
        protagonist_row.addWidget(protagonist_label)
        self.protagonist_edit = QLineEdit(self.section.get("protagonist", ""))
        self.protagonist_edit.setObjectName("InlineProtagonistInput")
        self.protagonist_edit.setPlaceholderText("Nome")
        self.protagonist_edit.textChanged.connect(lambda: self.changed("protagonist"))
        protagonist_row.addWidget(self.protagonist_edit, 1)
        age_label = QLabel("IDADE")
        age_label.setObjectName("Muted")
        protagonist_row.addWidget(age_label)
        self.age_edit = QLineEdit(str(self.section.get("age", "")))
        self.age_edit.setObjectName("InlineAgeInput")
        self.age_edit.setMaximumWidth(px(65))
        self.age_edit.setPlaceholderText("29")
        self.age_edit.textChanged.connect(lambda: self.changed("age"))
        protagonist_row.addWidget(self.age_edit)
        self.protagonist_gender = QComboBox()
        self.protagonist_gender.addItems(["Feminino", "Masculino"])
        self.protagonist_gender.setCurrentText(self.section.get("protagonist_gender", "Feminino"))
        self.protagonist_gender.setObjectName("CompactCombo")
        self.protagonist_gender.currentTextChanged.connect(lambda: self.changed("protagonist_gender"))
        protagonist_row.addWidget(self.protagonist_gender)
        outer.addLayout(protagonist_row)

        self.terror_edit = self.add_text_field(outer, "PARTES DE TERROR", "terror", self.section.get("terror", ""), 118)
        self.ending_edit = self.add_text_field(outer, "FINAL DO RELATO", "ending", self.section.get("ending", ""), 118)

        harmony_row = QHBoxLayout()
        harmony = QPushButton("✓  CRIAR HARMONIA")
        harmony.setObjectName("HarmonyButton")
        harmony.clicked.connect(self.prepare_harmony_prompt)
        self.harmony_status = QLabel(self.section.get("harmony_status", "Aguardando verificação de harmonia"))
        self.harmony_status.setObjectName("HarmonyWaiting")
        self.harmony_status.setWordWrap(True)
        harmony_row.addWidget(harmony)
        harmony_row.addWidget(self.harmony_status, 1)
        outer.addLayout(harmony_row)

        characters_header = QHBoxLayout()
        characters_title = QLabel("PERSONAGENS DO RELATO")
        characters_title.setObjectName("SectionHeading")
        characters_header.addWidget(characters_title, 1)
        self.compound_check = QCheckBox("Permitir nomes compostos aleatórios")
        self.compound_check.setObjectName("PromptCheck")
        self.compound_check.setChecked(bool(self.section.get("allow_compound", False)))
        self.compound_check.stateChanged.connect(lambda: self.changed("characters"))
        characters_header.addWidget(self.compound_check)
        outer.addLayout(characters_header)

        character_columns = QHBoxLayout()
        female_panel = Panel("FEMININOS")
        male_panel = Panel("MASCULINOS")
        self.female_layout = QVBoxLayout()
        self.female_layout.setSpacing(px(4))
        self.male_layout = QVBoxLayout()
        self.male_layout.setSpacing(px(4))
        female_panel.panel_layout.addLayout(self.female_layout)
        male_panel.panel_layout.addLayout(self.male_layout)
        female_add = QPushButton("＋ Feminino")
        female_add.setObjectName("SecondaryButton")
        female_add.clicked.connect(lambda: self.add_character("Feminino"))
        male_add = QPushButton("＋ Masculino")
        male_add.setObjectName("SecondaryButton")
        male_add.clicked.connect(lambda: self.add_character("Masculino"))
        female_panel.panel_layout.addWidget(female_add)
        male_panel.panel_layout.addWidget(male_add)
        character_columns.addWidget(female_panel, 1)
        character_columns.addWidget(male_panel, 1)
        outer.addLayout(character_columns)

        footer = QHBoxLayout()
        footer.addStretch()
        recreate_names = QPushButton("↻  Recriar nomes")
        recreate_names.setObjectName("SecondaryButton")
        recreate_names.clicked.connect(self.recreate_names)
        save = QPushButton("✓  Salvar Relato")
        save.setObjectName("SaveReportButton")
        save.clicked.connect(self.save_report)
        footer.addWidget(recreate_names)
        footer.addWidget(save)
        outer.addLayout(footer)

        self._load_character_rows()
        self._loading = False

    def add_text_field(self, parent_layout, label_text, field_key, initial, height):
        header = QHBoxLayout()
        label = QLabel(label_text)
        label.setObjectName("FieldLabel")
        header.addWidget(label)
        header.addStretch()
        mic = QPushButton("🎙")
        mic.setObjectName("MicrophoneButton")
        mic.setToolTip("Gravação e transcrição ainda não conectadas")
        mic.clicked.connect(lambda: self.microphone_not_connected(field_key))
        header.addWidget(mic)
        parent_layout.addLayout(header)
        editor = QTextEdit()
        editor.setObjectName("ReportTextEdit")
        editor.setMinimumHeight(px(height))
        editor.setPlainText(initial or "")
        editor.textChanged.connect(lambda: self.changed(field_key))
        parent_layout.addWidget(editor)
        return editor

    def _load_character_rows(self):
        female = list(self.section.get("female_names", []))
        male = list(self.section.get("male_names", []))
        protagonist = self.section.get("protagonist", "").strip()
        gender = self.section.get("protagonist_gender", "Feminino")
        if protagonist:
            target = female if gender == "Feminino" else male
            if protagonist not in target:
                target.insert(0, protagonist)
        self._render_character_rows("Feminino", female)
        self._render_character_rows("Masculino", male)

    def _render_character_rows(self, gender, names):
        layout = self.female_layout if gender == "Feminino" else self.male_layout
        rows = self.female_rows if gender == "Feminino" else self.male_rows
        clear_layout(layout)
        rows.clear()
        protagonist = self.protagonist_edit.text().strip()
        protagonist_gender = self.protagonist_gender.currentText()
        for index, name in enumerate(names):
            is_protagonist = bool(name == protagonist and gender == protagonist_gender)
            row = CharacterNameRow(
                name,
                lambda checked=False, i=index, g=gender: self.refresh_character_name(g, i),
                lambda checked=False, i=index, g=gender: self.remove_character(g, i),
                protagonist=is_protagonist,
            )
            rows.append(row)
            layout.addWidget(row)
        layout.addStretch()

    def _names(self, gender):
        rows = self.female_rows if gender == "Feminino" else self.male_rows
        return [row.value() for row in rows if row.value()]

    def add_character(self, gender):
        names = self._names(gender)
        names.append(make_random_name(gender, self.compound_check.isChecked(), names))
        self._render_character_rows(gender, names)
        self.changed("characters")

    def refresh_character_name(self, gender, index):
        names = self._names(gender)
        if index >= len(names):
            return
        protagonist = self.protagonist_edit.text().strip()
        exclude = names + ([protagonist] if protagonist else [])
        names[index] = make_random_name(gender, self.compound_check.isChecked(), exclude)
        self._render_character_rows(gender, names)
        self.changed("characters")

    def remove_character(self, gender, index):
        names = self._names(gender)
        if index >= len(names):
            return
        if names[index] == self.protagonist_edit.text().strip():
            QMessageBox.information(self, "Protagonista", "Altere o protagonista antes de removê-lo da lista.")
            return
        names.pop(index)
        self._render_character_rows(gender, names)
        self.changed("characters")

    def recreate_names(self):
        allow_compound = self.compound_check.isChecked()
        protagonist = self.protagonist_edit.text().strip()
        gender = self.protagonist_gender.currentText()
        female = [make_random_name("Feminino", allow_compound) for _ in self._names("Feminino")]
        male = [make_random_name("Masculino", allow_compound) for _ in self._names("Masculino")]
        if protagonist:
            target = female if gender == "Feminino" else male
            if protagonist in target:
                target.remove(protagonist)
            target.insert(0, protagonist)
        self._render_character_rows("Feminino", female)
        self._render_character_rows("Masculino", male)
        self.changed("characters")

    def changed(self, field_key):
        if self._loading:
            return
        self.last_changed_field = field_key
        self.section["saved_at"] = ""
        self.harmony_status.setText("Aguardando verificação de harmonia")
        self.on_changed()

    def section_data(self):
        summary = self.summary_edit.toPlainText().strip()
        terror = self.terror_edit.toPlainText().strip()
        ending = self.ending_edit.toPlainText().strip()
        data = {
            "id": self.section.get("id") or str(uuid.uuid4()),
            "title": self.title_edit.text().strip() or f"Relato {self.index}",
            "summary": summary,
            "terror": terror,
            "ending": ending,
            "text": "\n\n".join(x for x in (summary, terror, ending) if x),
            "protagonist": self.protagonist_edit.text().strip(),
            "age": self.age_edit.text().strip(),
            "protagonist_gender": self.protagonist_gender.currentText(),
            "female_names": self._names("Feminino"),
            "male_names": self._names("Masculino"),
            "allow_compound": self.compound_check.isChecked(),
            "harmony_status": self.harmony_status.text(),
            "last_changed_field": self.last_changed_field,
            "versions": list(self.section.get("versions", [])),
            "saved_at": self.section.get("saved_at", ""),
        }
        protagonist = data["protagonist"]
        if protagonist:
            target = data["female_names"] if data["protagonist_gender"] == "Feminino" else data["male_names"]
            other = data["male_names"] if data["protagonist_gender"] == "Feminino" else data["female_names"]
            if protagonist in other:
                other.remove(protagonist)
            if protagonist in target:
                target.remove(protagonist)
            target.insert(0, protagonist)
        return data

    def save_report(self):
        data = self.section_data()
        data["saved_at"] = now_text()
        self.section = dict(data)
        self.on_save(self.index - 1, data)

    def microphone_not_connected(self, field_key):
        labels = {"summary": "Resumo", "terror": "Partes de terror", "ending": "Final"}
        QMessageBox.information(
            self, "Microfone ainda não integrado",
            f"O botão de microfone do campo {labels.get(field_key, field_key)} está posicionado. "
            "A captura e a transcrição de voz ainda não foram conectadas.",
        )

    def prepare_recreate(self):
        current = self.section_data()
        prompt = (
            f"{self.master_prompt.strip()}\n\n"
            "TAREFA: RECRIAR COMPLETAMENTE APENAS O RELATO INDICADO.\n"
            f"TEMA FIXO DO EPISÓDIO: {self.theme}\n"
            f"RELATO A RECRIAR: {self.index:02d}\n"
            "Crie acontecimentos, resumo, partes de terror, final, protagonista e personagens novos. "
            "Mantenha o tema geral do episódio e todas as regras do Prompt Mestre. "
            "Não altere nem recrie nenhum outro relato. Entregue título, resumo, partes de terror, final, "
            "protagonista com idade e personagens separados por gênero.\n\n"
            f"CONTEÚDO ATUAL DE REFERÊNCIA (não copiar literalmente):\n{json.dumps(current, ensure_ascii=False, indent=2)}"
        )
        self.on_prompt(f"Recriar somente o Relato {self.index:02d}", prompt)

    def prepare_title_prompt(self):
        current = self.section_data()
        prompt = (
            f"{self.master_prompt.strip()}\n\n"
            f"Sugira 10 títulos curtos, fortes e altamente clicáveis para o Relato {self.index:02d}. "
            f"Mantenha o tema do episódio: {self.theme}. Baseie-se no conteúdo abaixo e não altere a história.\n\n"
            f"{current.get('summary', '')}\n{current.get('terror', '')}\n{current.get('ending', '')}"
        )
        self.on_prompt(f"Sugestões de título — Relato {self.index:02d}", prompt)

    def prepare_harmony_prompt(self):
        current = self.section_data()
        versions = list(current.get("versions", []))
        versions.append({
            "saved_at": now_text(),
            "summary": current.get("summary", ""),
            "terror": current.get("terror", ""),
            "ending": current.get("ending", ""),
            "reason": "Versão anterior preservada antes da harmonização",
        })
        current["versions"] = versions
        self.section = current
        prompt = (
            f"{self.master_prompt.strip()}\n\n"
            f"TEMA DO EPISÓDIO: {self.theme}\nRELATO: {self.index:02d}\n"
            f"CAMPO ALTERADO MAIS RECENTEMENTE: {self.last_changed_field}\n\n"
            "Verifique a coerência entre RESUMO, PARTES DE TERROR e FINAL. Use o campo alterado mais recentemente "
            "como referência principal. Altere somente o necessário, preservando intenção, acontecimentos centrais, "
            "personagens, idade, cenário, objetos e causalidade. Não descarte a versão anterior. Retorne os três campos completos.\n\n"
            f"RESUMO:\n{current.get('summary', '')}\n\nPARTES DE TERROR:\n{current.get('terror', '')}\n\nFINAL:\n{current.get('ending', '')}"
        )
        self.on_prompt(f"Criar Harmonia — Relato {self.index:02d}", prompt)


class EpisodePage(QWidget):
    DURATIONS = [
        "10 minutos", "20 minutos", "30 minutos", "35 minutos", "40 minutos", "45 minutos",
        "1 hora", "1h20min", "1h30min", "1h40min", "1h45min", "1h50min", "2 horas", "2h30min",
    ]

    def __init__(self, store, prompt_store, on_saved, on_back):
        super().__init__()
        self.store = store
        self.prompt_store = prompt_store
        self.on_saved = on_saved
        self.on_back = on_back
        self.project = None
        self.selected_prompt_id = ""
        self.report_editors = []

        self.stack = QStackedWidget()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.stack)
        self.setup_page = self._build_setup_page()
        self.stack.addWidget(self.setup_page)
        self.editor_page = self._build_editor_page()
        self.stack.addWidget(self.editor_page)
        self.show_setup()

    def _build_setup_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(px(24), px(20), px(24), px(18))
        layout.setSpacing(px(13))
        heading = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("▣  CRIAR EPISÓDIO")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Configure o tema, a quantidade de relatos e a duração do vídeo completo.")
        subtitle.setObjectName("Muted")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        heading.addLayout(title_box, 1)
        badge = QLabel("NOVO EPISÓDIO")
        badge.setObjectName("SelectedBadge")
        heading.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(heading)

        theme_panel = Panel("TEMA DO EPISÓDIO")
        self.theme_input = QLineEdit()
        self.theme_input.setObjectName("EpisodeThemeInput")
        self.theme_input.setPlaceholderText("Ex.: 4 relatos de trabalhadores noturnos")
        theme_hint = QLabel("A IA utilizará este tema para desenvolver os relatos conforme o Prompt Mestre.")
        theme_hint.setObjectName("Muted")
        theme_panel.panel_layout.addWidget(self.theme_input)
        theme_panel.panel_layout.addWidget(theme_hint)
        layout.addWidget(theme_panel)

        options = QHBoxLayout()
        quantity_panel = Panel("QUANTIDADE DE RELATOS")
        self.quantity_combo = QComboBox()
        self.quantity_combo.setObjectName("EpisodeCombo")
        for count in range(1, 11):
            self.quantity_combo.addItem(f"{count} relato" if count == 1 else f"{count} relatos", count)
        self.quantity_combo.setCurrentIndex(3)
        quantity_panel.panel_layout.addWidget(self.quantity_combo)
        options.addWidget(quantity_panel, 1)

        duration_panel = Panel("DURAÇÃO DO EPISÓDIO COMPLETO")
        self.duration_combo = QComboBox()
        self.duration_combo.setObjectName("EpisodeCombo")
        self.duration_combo.addItems(self.DURATIONS)
        self.duration_combo.setCurrentText("1h30min")
        duration_panel.panel_layout.addWidget(self.duration_combo)
        options.addWidget(duration_panel, 1)
        layout.addLayout(options)

        prompt_panel = Panel("PROMPT MESTRE")
        prompt_header = QHBoxLayout()
        self.prompt_name_label = QLabel("Prompt Mestre")
        self.prompt_name_label.setObjectName("PromptSelectedName")
        prompt_header.addWidget(self.prompt_name_label, 1)
        self.prompt_status_label = QLabel("Pendente de configuração")
        self.prompt_status_label.setObjectName("PromptPending")
        prompt_header.addWidget(self.prompt_status_label)
        prompt_panel.panel_layout.addLayout(prompt_header)
        prompt_desc = QLabel("Instruções originais preservadas e aplicadas à criação dos resumos e histórias.")
        prompt_desc.setObjectName("Muted")
        prompt_panel.panel_layout.addWidget(prompt_desc)
        load_prompt = QPushButton("▤  Carregar Prompt")
        load_prompt.setObjectName("SmallRedButton")
        load_prompt.clicked.connect(self.load_prompt_dialog)
        prompt_panel.panel_layout.addWidget(load_prompt, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(prompt_panel)

        layout.addStretch()
        bottom = QHBoxLayout()
        back = QPushButton("←  Voltar para Home")
        back.setObjectName("SecondaryButton")
        back.clicked.connect(self.on_back)
        bottom.addWidget(back)
        bottom.addStretch()
        create = QPushButton("✦  CRIAR ROTEIRO")
        create.setObjectName("CreateEpisodeButton")
        create.setMinimumHeight(px(52))
        create.clicked.connect(self.create_episode)
        bottom.addWidget(create, 2)
        layout.addLayout(bottom)
        return page

    def _build_editor_page(self):
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        self.editor_scroll = QScrollArea()
        self.editor_scroll.setWidgetResizable(True)
        self.editor_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.editor_content = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_content)
        self.editor_layout.setContentsMargins(px(22), px(16), px(22), px(18))
        self.editor_layout.setSpacing(px(12))
        self.editor_scroll.setWidget(self.editor_content)
        outer.addWidget(self.editor_scroll)
        return page

    def show_setup(self):
        self.project = None
        self.selected_prompt_id = self.prompt_store.default().get("id", "")
        self.theme_input.clear()
        self.quantity_combo.setCurrentIndex(3)
        self.duration_combo.setCurrentText("1h30min")
        self.refresh_prompt_card()
        self.stack.setCurrentWidget(self.setup_page)

    def load_prompt_dialog(self):
        dialog = PromptSelectDialog(self.prompt_store, self.selected_prompt_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_prompt_id = dialog.selected_id() or self.selected_prompt_id
            self.refresh_prompt_card()

    def refresh_prompt_card(self):
        prompt = self.prompt_store.get(self.selected_prompt_id) or self.prompt_store.default()
        self.selected_prompt_id = prompt.get("id", "")
        self.prompt_name_label.setText(prompt.get("name", "Prompt Mestre"))
        if prompt.get("content", "").strip():
            self.prompt_status_label.setText("Selecionado")
            self.prompt_status_label.setObjectName("PromptReady")
        else:
            self.prompt_status_label.setText("Pendente — cadastre o conteúdo em Prompts")
            self.prompt_status_label.setObjectName("PromptPending")
        self.prompt_status_label.style().unpolish(self.prompt_status_label)
        self.prompt_status_label.style().polish(self.prompt_status_label)

    def create_episode(self):
        theme = self.theme_input.text().strip()
        if not theme:
            QMessageBox.warning(self, "Tema obrigatório", "Digite o tema do episódio antes de criar o roteiro.")
            self.theme_input.setFocus()
            return
        prompt = self.prompt_store.get(self.selected_prompt_id) or self.prompt_store.default()
        count = int(self.quantity_combo.currentData())
        duration = self.duration_combo.currentText()
        project = self.store.new_project()
        project.update({
            "title": theme,
            "theme": theme,
            "status": "Em criação",
            "duration": duration,
            "duration_minutes": duration_minutes(duration),
            "report_count": count,
            "prompt_id": prompt.get("id", ""),
            "prompt_name": prompt.get("name", "Prompt Mestre"),
            "master_prompt": prompt.get("content", ""),
            "sections": [
                {
                    "id": str(uuid.uuid4()), "title": f"Relato {i}",
                    "summary": "", "terror": "", "ending": "", "text": "",
                    "protagonist": "", "age": "", "protagonist_gender": "Feminino",
                    "female_names": [], "male_names": [], "allow_compound": False,
                    "harmony_status": "Aguardando verificação de harmonia", "versions": [],
                }
                for i in range(1, count + 1)
            ],
        })
        project = self.store.save(project)
        self.load_project(project)
        self.on_saved(project)
        initial_prompt = self.build_initial_prompt(project)
        if not project.get("master_prompt", "").strip():
            QMessageBox.information(
                self, "Episódio criado — Prompt Mestre pendente",
                "O episódio foi salvo e os relatos foram preparados.\n\n"
                "Antes de gerar o conteúdo, cadastre o texto integral do Prompt Mestre na opção Prompts. "
                "A geração automática por IA ainda não está conectada nesta versão.",
            )
        else:
            self.show_prompt_preview("Prompt para gerar o roteiro", initial_prompt)

    def build_initial_prompt(self, project):
        return (
            f"{project.get('master_prompt', '').strip()}\n\n"
            "CONFIGURAÇÃO DO EPISÓDIO\n"
            f"TEMA: {project.get('theme', '')}\n"
            f"QUANTIDADE: {project.get('report_count', 1)} relatos\n"
            f"DURAÇÃO DO EPISÓDIO COMPLETO: {project.get('duration', '')}\n\n"
            "Gere exatamente a quantidade solicitada de relatos, mantendo o tema e todas as regras do Prompt Mestre. "
            "Para cada relato, entregue: título, resumo completo, protagonista e idade, partes de terror, final, "
            "personagens femininos e masculinos. Os relatos devem ser independentes, mas pertencer ao tema geral."
        )

    def show_prompt_preview(self, title, prompt):
        dialog = PromptPreviewDialog(title, prompt, self)
        dialog.exec()

    def open_prompt_action(self, title, prompt):
        self.show_prompt_preview(title, prompt)

    def load_project(self, project):
        self.project = self.store._normalize_project(project)
        self._render_editor()
        self.stack.setCurrentWidget(self.editor_page)

    def _render_editor(self):
        clear_layout(self.editor_layout)
        self.report_editors = []
        project = self.project
        top = QHBoxLayout()
        heading_box = QVBoxLayout()
        title = QLabel("EPISÓDIO CRIADO")
        title.setObjectName("PageTitle")
        subtitle = QLabel(project.get("theme", project.get("title", "")))
        subtitle.setObjectName("Muted")
        subtitle.setWordWrap(True)
        heading_box.addWidget(title)
        heading_box.addWidget(subtitle)
        top.addLayout(heading_box, 1)
        back = QPushButton("←  Voltar para Home")
        back.setObjectName("SecondaryButton")
        back.clicked.connect(self.on_back)
        top.addWidget(back)
        self.editor_layout.addLayout(top)

        summary_panel = Panel("TEMA DO EPISÓDIO")
        theme_label = QLabel(project.get("theme", project.get("title", "")))
        theme_label.setObjectName("EpisodeThemeDisplay")
        theme_label.setWordWrap(True)
        summary_panel.panel_layout.addWidget(theme_label)
        meta = QHBoxLayout()
        for label, value in [
            ("QUANTIDADE DE RELATOS", str(len(project.get("sections", [])))),
            ("DURAÇÃO COMPLETA", project.get("duration", "—")),
            ("PROMPT MESTRE", project.get("prompt_name", "Prompt Mestre")),
        ]:
            block = QVBoxLayout()
            cap = QLabel(label)
            cap.setObjectName("Muted")
            val = QLabel(value)
            val.setObjectName("PlanningValueSmall")
            block.addWidget(cap)
            block.addWidget(val)
            meta.addLayout(block, 1)
        summary_panel.panel_layout.addLayout(meta)
        self.editor_layout.addWidget(summary_panel)

        reports_title = QHBoxLayout()
        label = QLabel("RELATOS DO EPISÓDIO")
        label.setObjectName("SectionHeading")
        reports_title.addWidget(label, 1)
        self.reports_count_label = QLabel(f"{len(project.get('sections', []))} de {len(project.get('sections', []))}")
        self.reports_count_label.setObjectName("PromptReady")
        reports_title.addWidget(self.reports_count_label)
        self.editor_layout.addLayout(reports_title)

        for index, section in enumerate(project.get("sections", []), start=1):
            editor = ReportEditor(
                section, index, project.get("theme", ""), project.get("master_prompt", ""),
                self.save_report, self.open_prompt_action, self.refresh_planning,
            )
            self.report_editors.append(editor)
            self.editor_layout.addWidget(editor)

        planning = Panel("PLANEJAMENTO DO EPISÓDIO")
        cards = QHBoxLayout()
        self.plan_reports = self._planning_card("▤", "RELATOS", "0", "No episódio")
        self.plan_characters = self._planning_card("♙", "PERSONAGENS", "0", "Planejados")
        self.plan_duration = self._planning_card("◷", "DURAÇÃO", "0", "Minutos")
        cards.addWidget(self.plan_reports[0], 1)
        cards.addWidget(self.plan_characters[0], 1)
        cards.addWidget(self.plan_duration[0], 1)
        planning.panel_layout.addLayout(cards)
        progress_head = QHBoxLayout()
        progress_title = QLabel("PROGRESSO DO PLANEJAMENTO")
        progress_title.setObjectName("Muted")
        progress_head.addWidget(progress_title, 1)
        self.progress_label = QLabel("0/0 relatos")
        self.progress_label.setObjectName("PromptReady")
        progress_head.addWidget(self.progress_label)
        planning.panel_layout.addLayout(progress_head)
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("PlanningProgress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        planning.panel_layout.addWidget(self.progress_bar)
        self.progress_description = QLabel("Preencha e salve cada relato para avançar no planejamento.")
        self.progress_description.setObjectName("Muted")
        planning.panel_layout.addWidget(self.progress_description)
        self.editor_layout.addWidget(planning)

        footer = QHBoxLayout()
        self.episode_save_status = QLabel("Projeto salvo localmente. Salve cada relato e o episódio.")
        self.episode_save_status.setObjectName("Muted")
        footer.addWidget(self.episode_save_status, 1)
        delete = QPushButton("Excluir Episódio")
        delete.setObjectName("DangerButton")
        delete.clicked.connect(self.delete_episode)
        create_episode = QPushButton("✓  Criar Episódio")
        create_episode.setObjectName("CreateEpisodeButton")
        create_episode.clicked.connect(self.finalize_episode)
        footer.addWidget(delete)
        footer.addWidget(create_episode)
        self.editor_layout.addLayout(footer)
        self.refresh_planning()

    def _planning_card(self, icon_text, title_text, value_text, caption_text):
        card = QFrame()
        card.setObjectName("PlanningCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(px(12), px(10), px(12), px(10))
        icon = QLabel(icon_text)
        icon.setObjectName("PlanningIcon")
        title = QLabel(title_text)
        title.setObjectName("Muted")
        value = QLabel(value_text)
        value.setObjectName("PlanningValue")
        caption = QLabel(caption_text)
        caption.setObjectName("Muted")
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(value)
        layout.addWidget(caption)
        return card, value, caption

    def refresh_planning(self):
        if not self.project or not hasattr(self, "plan_reports"):
            return
        data = [editor.section_data() for editor in self.report_editors]
        total = len(data)
        characters = sum(len(item.get("female_names", [])) + len(item.get("male_names", [])) for item in data)
        completed = sum(1 for item in data if item.get("saved_at"))
        self.plan_reports[1].setText(str(total))
        self.plan_characters[1].setText(str(characters))
        self.plan_duration[1].setText(str(self.project.get("duration_minutes", 90)))
        self.progress_label.setText(f"{completed}/{total} relatos")
        self.progress_bar.setValue(int((completed / total) * 100) if total else 0)
        self.progress_description.setText(
            "Todos os relatos estão incluídos no planejamento." if completed == total
            else "Preencha e salve cada relato para avançar no planejamento."
        )

    def save_report(self, index, data):
        if not self.project or not (0 <= index < len(self.project.get("sections", []))):
            return
        self.project["sections"][index] = data
        self.project["updated_at"] = now_text()
        self.project["status"] = "Em desenvolvimento"
        self.project = self.store.save(self.project)
        self.on_saved(self.project)
        self.episode_save_status.setText(f"Relato {index + 1} salvo em {data.get('saved_at', now_text())}.")
        self.refresh_planning()
        QMessageBox.information(self, "Relato salvo", f"Relato {index + 1} salvo com sucesso.")

    def save_episode(self):
        if not self.project:
            return
        for index, editor in enumerate(self.report_editors):
            self.project["sections"][index] = editor.section_data()
        self.project["updated_at"] = now_text()
        self.project["status"] = "Em desenvolvimento"
        self.project = self.store.save(self.project)
        self.on_saved(self.project)
        self.episode_save_status.setText(f"Episódio salvo em {self.project['updated_at']}.")
        QMessageBox.information(self, "Episódio salvo", "Todas as alterações do episódio foram salvas localmente.")
        self.refresh_planning()

    def finalize_episode(self):
        if not self.project:
            return
        missing = []
        for index, editor in enumerate(self.report_editors, start=1):
            data = editor.section_data()
            required = [data.get("title"), data.get("summary"), data.get("terror"), data.get("ending")]
            if not all(value and value.strip() for value in required):
                missing.append(f"Relato {index}: complete título, resumo, partes de terror e final.")
            elif not data.get("saved_at"):
                missing.append(f"Relato {index}: clique em Salvar Relato antes de criar o episódio.")
        if missing:
            QMessageBox.warning(
                self, "Planejamento incompleto",
                "Para criar o episódio, finalize e salve cada relato:\n\n" + "\n".join(missing),
            )
            return
        for index, editor in enumerate(self.report_editors):
            self.project["sections"][index] = editor.section_data()
        self.project["status"] = "Pronto para gravar"
        self.project["updated_at"] = now_text()
        self.project = self.store.save(self.project)
        self.on_saved(self.project)
        self.episode_save_status.setText(f"Episódio criado em {self.project['updated_at']} — pronto para gravar.")
        QMessageBox.information(
            self, "Episódio criado",
            "O episódio foi criado e salvo na Home. Você já pode carregá-lo na aba Gravação.",
        )
        self.refresh_planning()

    def delete_episode(self):
        if not self.project:
            return
        answer = QMessageBox.question(
            self, "Apagar episódio",
            f"Deseja realmente apagar o episódio '{self.project.get('title', '')}'? Esta ação remove o projeto e suas referências locais.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.store.delete(self.project.get("id"))
            self.on_saved(None)
            self.on_back()



class StorySelectButton(QPushButton):
    def __init__(self, title, count, parent=None):
        super().__init__(parent)
        self.setObjectName("StorySelectButton")
        self.setCheckable(True)
        self.setMinimumHeight(px(62))
        layout = QHBoxLayout(self)
        layout.setContentsMargins(px(10), px(7), px(10), px(7))
        layout.setSpacing(px(9))
        icon = QLabel("▤")
        icon.setObjectName("StoryIcon")
        layout.addWidget(icon)
        texts = QVBoxLayout()
        texts.setSpacing(px(2))
        name = QLabel(title)
        name.setObjectName("StoryName")
        count_label = QLabel(f"{count} parágrafo(s)")
        count_label.setObjectName("Muted")
        texts.addWidget(name)
        texts.addWidget(count_label)
        layout.addLayout(texts, 1)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class MicrophoneDialog(QDialog):
    def __init__(self, selected_name="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar microfone")
        self.setMinimumWidth(px(430))
        layout = QVBoxLayout(self)
        info = QLabel(
            "Selecione o dispositivo que será usado quando a captura de áudio for integrada.\n"
            "Nesta versão, a seleção é visual e ainda não inicia a gravação do microfone."
        )
        info.setWordWrap(True)
        info.setObjectName("Muted")
        layout.addWidget(info)
        self.combo = QComboBox()
        self.combo.setObjectName("EditorInput")
        if MULTIMEDIA_AVAILABLE and QMediaDevices is not None:
            try:
                devices = QMediaDevices.audioInputs()
            except Exception:
                devices = []
            if devices:
                for device in devices:
                    name = device.description()
                    self.combo.addItem(name, name)
            else:
                self.combo.addItem("Nenhum microfone detectado")
        else:
            self.combo.addItem("Enumeração de dispositivos indisponível")
        if selected_name:
            index = self.combo.findText(selected_name)
            if index >= 0:
                self.combo.setCurrentIndex(index)
        layout.addWidget(self.combo)
        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.setObjectName("SecondaryButton")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Salvar seleção")
        save.setObjectName("PrimaryButton")
        save.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

    def selected_name(self):
        return self.combo.currentText()


class LoadProjectDialog(QDialog):
    def __init__(self, projects, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Carregar projeto para gravação")
        self.setMinimumSize(px(500), px(400))
        self.projects = projects
        layout = QVBoxLayout(self)
        label = QLabel("Escolha um roteiro salvo para carregar seus relatos no Estúdio de Gravação.")
        label.setWordWrap(True)
        label.setObjectName("Muted")
        layout.addWidget(label)
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("ProjectPicker")
        for project in projects:
            title = project.get("title") or "Projeto sem título"
            status = project.get("status", "Rascunho")
            item = QListWidgetItem(f"{title}   —   {status}")
            item.setData(Qt.ItemDataRole.UserRole, project.get("id"))
            self.list_widget.addItem(item)
        if projects:
            self.list_widget.setCurrentRow(0)
        layout.addWidget(self.list_widget, 1)
        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.setObjectName("SecondaryButton")
        cancel.clicked.connect(self.reject)
        load = QPushButton("Carregar selecionado")
        load.setObjectName("PrimaryButton")
        load.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(load)
        layout.addLayout(buttons)

    def selected_project_id(self):
        item = self.list_widget.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None


class RecordingPage(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.current_project = None
        self.selected_section_index = 0
        self.visible_paragraph_start = 0
        self.selected_microphone = ""
        self.story_buttons = []
        self.stage_buttons = []
        self.recording_rows_layout = None
        self.player = None
        self.audio_output = None

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.content = QWidget()
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(px(22), px(14), px(22), px(16))
        content_layout.setSpacing(px(12))
        page_layout.addWidget(self.scroll)
        self.scroll.setWidget(self.content)

        title = QLabel("▣  Estúdio de Gravação")
        title.setObjectName("PageTitle")
        content_layout.addWidget(title)

        top = QHBoxLayout()
        top.setSpacing(px(12))

        # CÂMERA / MINI-PLAYER
        camera = Panel()
        camera.setMinimumHeight(px(270))
        camera.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        camera_header = QHBoxLayout()
        camera_label = QLabel("Câmera — Pré-visualização")
        camera_label.setObjectName("CameraBadge")
        camera_header.addWidget(camera_label)
        camera_header.addStretch()
        self.camera_status = QLabel("AGUARDANDO CÂMERA")
        self.camera_status.setObjectName("WaitingBadge")
        camera_header.addWidget(self.camera_status)
        self.back_to_camera_button = QPushButton("←  Voltar para Câmera")
        self.back_to_camera_button.setObjectName("SecondaryButton")
        self.back_to_camera_button.setVisible(False)
        self.back_to_camera_button.clicked.connect(self.return_to_camera)
        camera_header.addWidget(self.back_to_camera_button)
        camera.panel_layout.addLayout(camera_header)

        self.camera_stack = QStackedWidget()
        self.camera_stack.setMinimumHeight(px(205))
        self.camera_preview = QFrame()
        self.camera_preview.setObjectName("CameraPreview")
        preview_layout = QVBoxLayout(self.camera_preview)
        preview_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_icon = QLabel("▣")
        preview_icon.setObjectName("PreviewIcon")
        preview_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_text = QLabel("CÂMERA — AGUARDANDO CONEXÃO")
        preview_text.setObjectName("PreviewText")
        preview_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(preview_icon)
        preview_layout.addWidget(preview_text)
        self.camera_stack.addWidget(self.camera_preview)

        if MULTIMEDIA_AVAILABLE and QVideoWidget is not None:
            self.video_widget = QVideoWidget()
            self.video_widget.setObjectName("VideoPreview")
            self.camera_stack.addWidget(self.video_widget)
            self.player = QMediaPlayer(self)
            self.audio_output = QAudioOutput(self)
            self.player.setAudioOutput(self.audio_output)
            self.player.setVideoOutput(self.video_widget)
            self.player.positionChanged.connect(self.update_player_position)
            self.player.durationChanged.connect(self.update_player_duration)
        else:
            self.video_widget = None

        camera.panel_layout.addWidget(self.camera_stack, 1)
        camera_bottom = QHBoxLayout()
        self.camera_bottom_label = QLabel("16:9   |   1080p   |   30 fps   •   Captura real ainda não conectada")
        self.camera_bottom_label.setObjectName("Muted")
        camera_bottom.addWidget(self.camera_bottom_label, 1)
        self.player_controls = QWidget()
        player_controls_layout = QHBoxLayout(self.player_controls)
        player_controls_layout.setContentsMargins(0, 0, 0, 0)
        player_controls_layout.setSpacing(px(7))
        self.player_play_button = QPushButton("Ⅱ")
        self.player_play_button.setObjectName("PlayButton")
        self.player_play_button.setToolTip("Reproduzir / pausar")
        self.player_play_button.clicked.connect(self.toggle_player)
        self.player_stop_button = QPushButton("■")
        self.player_stop_button.setObjectName("PlayButton")
        self.player_stop_button.setToolTip("Parar vídeo")
        self.player_stop_button.clicked.connect(self.stop_player)
        self.player_slider = QSlider(Qt.Orientation.Horizontal)
        self.player_slider.setObjectName("PlayerSlider")
        self.player_slider.setRange(0, 0)
        self.player_slider.sliderMoved.connect(self.seek_player)
        self.player_time_label = QLabel("00:00 / 00:00")
        self.player_time_label.setObjectName("Muted")
        player_controls_layout.addWidget(self.player_play_button)
        player_controls_layout.addWidget(self.player_stop_button)
        player_controls_layout.addWidget(self.player_slider, 1)
        player_controls_layout.addWidget(self.player_time_label)
        self.player_controls.setVisible(False)
        camera_bottom.addWidget(self.player_controls, 2)
        camera.panel_layout.addLayout(camera_bottom)

        # ÁUDIO
        audio = Panel("Áudio")
        audio.setFixedWidth(px(190))
        audio.setMinimumHeight(px(270))
        self.audio_device_label = QLabel("Aguardando dispositivo")
        self.audio_device_label.setObjectName("Muted")
        self.audio_device_label.setWordWrap(True)
        self.audio_device_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        audio.panel_layout.addWidget(self.audio_device_label)

        meter = QWidget()
        meter_layout = QHBoxLayout(meter)
        meter_layout.setContentsMargins(px(16), px(4), px(16), px(4))
        meter_layout.setSpacing(px(7))
        for _ in range(2):
            column = QWidget()
            col_layout = QVBoxLayout(column)
            col_layout.setContentsMargins(0, 0, 0, 0)
            col_layout.setSpacing(px(4))
            for _ in range(9):
                segment = QFrame()
                segment.setObjectName("MeterInactive")
                segment.setFixedHeight(px(10))
                col_layout.addWidget(segment)
            meter_layout.addWidget(column, 1)
        audio.panel_layout.addWidget(meter, 1)
        self.audio_status_label = QLabel("●  Sem sinal de áudio")
        self.audio_status_label.setObjectName("Muted")
        self.audio_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        audio.panel_layout.addWidget(self.audio_status_label)
        configure_mic = QPushButton("⚙  Configurar Microfone")
        configure_mic.setObjectName("SmallRedButton")
        configure_mic.setCursor(Qt.CursorShape.PointingHandCursor)
        configure_mic.clicked.connect(self.configure_microphone)
        audio.panel_layout.addWidget(configure_mic)

        # HISTÓRIAS DO PROJETO
        stories = Panel()
        stories.setMinimumWidth(px(330))
        stories.setMinimumHeight(px(270))
        stories_header = QHBoxLayout()
        stories_title = QLabel("▤  Histórias da Sessão")
        stories_title.setObjectName("PanelTitle")
        stories_header.addWidget(stories_title, 1)
        load_project = QPushButton("▰  Carregar Projeto")
        load_project.setObjectName("SmallRedButton")
        load_project.clicked.connect(self.load_project_dialog)
        stories_header.addWidget(load_project)
        stories.panel_layout.addLayout(stories_header)
        self.project_name_label = QLabel("Nenhum projeto carregado")
        self.project_name_label.setObjectName("Muted")
        stories.panel_layout.addWidget(self.project_name_label)
        self.story_list_widget = QWidget()
        self.story_list_layout = QVBoxLayout(self.story_list_widget)
        self.story_list_layout.setContentsMargins(0, 0, 0, 0)
        self.story_list_layout.setSpacing(px(7))
        self.story_list_layout.addStretch()
        stories.panel_layout.addWidget(self.story_list_widget, 1)
        top.addWidget(camera, 5)
        top.addWidget(audio, 1.25)
        top.addWidget(stories, 3.1)
        content_layout.addLayout(top, 5)

        # ESTRUTURA DA GRAVAÇÃO
        stages_panel = Panel("Estrutura da Gravação")
        stages_panel.setMinimumHeight(px(112))
        self.stages_layout = QHBoxLayout()
        self.stages_layout.setSpacing(px(10))
        stages_panel.panel_layout.addLayout(self.stages_layout)
        content_layout.addWidget(stages_panel)

        # TELEPROMPTER E STATUS DE NARRAÇÃO
        lower = QHBoxLayout()
        lower.setSpacing(px(12))

        reading = Panel()
        reading.setMinimumHeight(px(300))
        reading_header = QHBoxLayout()
        reading_title = QLabel("▤  Teleprompter — aguardando projeto")
        reading_title.setObjectName("PanelTitle")
        self.reading_title = reading_title
        self.paragraph_counter = QLabel("Parágrafo 0 de 0")
        self.paragraph_counter.setObjectName("AccentText")
        reading_header.addWidget(reading_title, 1)
        reading_header.addWidget(self.paragraph_counter)
        reading.panel_layout.addLayout(reading_header)

        self.teleprompter = QTextBrowser()
        self.teleprompter.setObjectName("Teleprompter")
        self.teleprompter.setOpenExternalLinks(False)
        self.teleprompter.setMinimumHeight(px(205))
        self.teleprompter.setHtml(
            "<div style='color:#AAB5C0;text-align:center;padding:35px;'>"
            "Carregue um projeto para visualizar os relatos aqui."
            "</div>"
        )
        teleprompter_row = QHBoxLayout()
        teleprompter_row.addWidget(self.teleprompter, 1)
        paragraph_controls = QVBoxLayout()
        paragraph_controls.setSpacing(px(7))
        previous_paragraph = QPushButton("▲")
        previous_paragraph.setObjectName("ArrowButton")
        previous_paragraph.setToolTip("Parágrafo anterior")
        previous_paragraph.clicked.connect(lambda: self.move_teleprompter(-1))
        next_paragraph = QPushButton("▼")
        next_paragraph.setObjectName("ArrowButton")
        next_paragraph.setToolTip("Próximo parágrafo")
        next_paragraph.clicked.connect(lambda: self.move_teleprompter(1))
        paragraph_controls.addWidget(previous_paragraph)
        paragraph_controls.addWidget(next_paragraph)
        paragraph_controls.addStretch()
        teleprompter_row.addLayout(paragraph_controls)
        reading.panel_layout.addLayout(teleprompter_row, 1)
        self.voice_scroll_label = QLabel(
            "◌  A rolagem automática será controlada pela voz; navegação manual disponível enquanto a integração é preparada"
        )
        self.voice_scroll_label.setObjectName("Muted")
        self.voice_scroll_label.setWordWrap(True)
        reading.panel_layout.addWidget(self.voice_scroll_label)
        lower.addWidget(reading, 7)

        narration = Panel("Acompanhamento do Texto")
        narration.setMinimumWidth(px(270))
        narration.setMinimumHeight(px(300))
        self.narration_indicator = QLabel("●  Aguardando integração de voz")
        self.narration_indicator.setObjectName("NarrationWaiting")
        self.narration_indicator.setWordWrap(True)
        narration.panel_layout.addWidget(self.narration_indicator)
        explanation = QLabel(
            "O indicador mudará automaticamente conforme a análise da voz estiver conectada."
        )
        explanation.setObjectName("Muted")
        explanation.setWordWrap(True)
        narration.panel_layout.addWidget(explanation)
        narration.panel_layout.addSpacing(px(8))
        self.add_status_legend(narration, "#21D45A", "Prosseguindo normalmente")
        self.add_status_legend(narration, "#F0A12B", "Regravando uma frase")
        self.add_status_legend(narration, "#36A8FF", "Retomando após interrupção")
        narration.panel_layout.addStretch()
        lower.addWidget(narration, 3)

        # ÚLTIMAS GRAVAÇÕES
        latest = Panel("▤  Últimas Gravações")
        latest.setFixedWidth(px(300))
        latest.setMinimumHeight(px(300))
        self.recording_rows_layout = QVBoxLayout()
        self.recording_rows_layout.setSpacing(px(7))
        latest.panel_layout.addLayout(self.recording_rows_layout, 1)
        import_video = QPushButton("＋  Importar vídeo para testar o mini-player")
        import_video.setObjectName("SecondaryButton")
        import_video.clicked.connect(self.import_video_for_review)
        latest.panel_layout.addWidget(import_video)
        lower.addWidget(latest)
        content_layout.addLayout(lower, 5)

        # CONTROLES INFERIORES
        controls = QHBoxLayout()
        controls.addStretch(8)
        start = QPushButton("◉  Iniciar Gravação")
        start.setObjectName("PrimaryButton")
        start.setMinimumHeight(px(58))
        start.clicked.connect(self.recording_not_connected)
        pause = QPushButton("Ⅱ  Pausar")
        pause.setObjectName("SecondaryButton")
        pause.setMinimumHeight(px(58))
        pause.clicked.connect(self.recording_not_connected)
        finish = QPushButton("■  Encerrar Sessão")
        finish.setObjectName("SecondaryButton")
        finish.setMinimumHeight(px(58))
        finish.clicked.connect(self.recording_not_connected)
        controls.addWidget(start, 6)
        controls.addWidget(pause, 4)
        controls.addWidget(finish, 4)
        content_layout.addLayout(controls)

        self.refresh_recordings()
        self.refresh_stories()
        self.refresh_stages()

    def add_status_legend(self, panel, color, text):
        row = QHBoxLayout()
        dot = QLabel("●")
        dot.setStyleSheet(f"color:{color};font-size:{px(17)}px;font-weight:bold;")
        label = QLabel(text)
        label.setObjectName("Muted")
        label.setWordWrap(True)
        row.addWidget(dot)
        row.addWidget(label, 1)
        panel.panel_layout.addLayout(row)

    def set_project(self, project):
        self.current_project = project
        self.selected_section_index = 0
        self.visible_paragraph_start = 0
        self.refresh_stories()
        self.refresh_stages()
        self.refresh_teleprompter()
        self.refresh_recordings()

    def load_project_dialog(self):
        projects = self.store.all()
        if not projects:
            QMessageBox.information(
                self,
                "Nenhum projeto salvo",
                "Crie e salve um episódio na Home antes de carregá-lo para gravação.",
            )
            return
        dialog = LoadProjectDialog(projects, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            project = self.store.get(dialog.selected_project_id())
            if project:
                self.set_project(project)

    def refresh_stories(self):
        clear_layout(self.story_list_layout)
        self.story_buttons = []
        if not self.current_project:
            label = QLabel("Carregue um episódio para inserir seus relatos nesta sessão.")
            label.setObjectName("Muted")
            label.setWordWrap(True)
            self.story_list_layout.addWidget(label)
            self.project_name_label.setText("Nenhum projeto carregado")
            self.story_list_layout.addStretch()
            return

        self.project_name_label.setText(self.current_project.get("title", "Projeto"))
        sections = self.current_project.get("sections", [])
        for index, section in enumerate(sections):
            count = len(split_paragraphs(section_text(section)))
            button = StorySelectButton(section.get("title", f"Relato {index + 1}"), count)
            button.setChecked(index == self.selected_section_index)
            button.clicked.connect(lambda checked=False, i=index: self.select_section(i))
            self.story_list_layout.addWidget(button)
            self.story_buttons.append(button)
        self.story_list_layout.addStretch()
        if sections:
            self.select_section(min(self.selected_section_index, len(sections) - 1))

    def refresh_stages(self):
        clear_layout(self.stages_layout)
        self.stage_buttons = []
        stage_specs = [("▶", "Início", "Tela cheia", None)]
        if self.current_project:
            for index, section in enumerate(self.current_project.get("sections", [])):
                count = len(split_paragraphs(section_text(section)))
                stage_specs.append(("▣", section.get("title", f"Relato {index + 1}"), f"{count} parágrafo(s)", index))
        stage_specs.append(("⚑", "Final", "Tela cheia", None))

        for position, (icon, name, detail, section_index) in enumerate(stage_specs):
            button = QPushButton()
            button.setObjectName("ActiveStage" if section_index == self.selected_section_index and section_index is not None else "StageButton")
            button.setMinimumHeight(px(68))
            button_layout = QVBoxLayout(button)
            button_layout.setContentsMargins(px(4), px(4), px(4), px(4))
            main_line = QLabel(f"{icon}  {name}")
            main_line.setObjectName("StageMain")
            main_line.setAlignment(Qt.AlignmentFlag.AlignCenter)
            detail_line = QLabel(detail)
            detail_line.setObjectName("StageDetail")
            detail_line.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button_layout.addWidget(main_line)
            button_layout.addWidget(detail_line)
            if section_index is not None:
                button.clicked.connect(lambda checked=False, i=section_index: self.select_section(i))
            else:
                button.clicked.connect(lambda checked=False, p=position: self.select_non_story_stage(p))
            self.stages_layout.addWidget(button, 1)
            self.stage_buttons.append(button)

    def select_non_story_stage(self, position):
        for index, button in enumerate(self.stage_buttons):
            button.setObjectName("ActiveStage" if index == position else "StageButton")
            button.style().unpolish(button)
            button.style().polish(button)

    def select_section(self, index):
        if not self.current_project:
            return
        sections = self.current_project.get("sections", [])
        if not (0 <= index < len(sections)):
            return
        self.selected_section_index = index
        self.visible_paragraph_start = 0
        for i, button in enumerate(self.story_buttons):
            button.setChecked(i == index)
        self.refresh_teleprompter()
        self.refresh_stages()

    def refresh_teleprompter(self):
        if not self.current_project:
            return
        sections = self.current_project.get("sections", [])
        if not sections:
            self.teleprompter.setPlainText("Este projeto ainda não possui relatos.")
            self.paragraph_counter.setText("Parágrafo 0 de 0")
            return
        index = min(self.selected_section_index, len(sections) - 1)
        section = sections[index]
        paragraphs = split_paragraphs(section_text(section))
        self.reading_title.setText(f"▤  Teleprompter — {section.get('title', 'Relato')}")
        start = min(self.visible_paragraph_start, max(0, len(paragraphs) - 1))
        visible = paragraphs[start:start + 2]
        if visible:
            self.paragraph_counter.setText(
                f"{start + 1}–{start + len(visible)} de {len(paragraphs)} parágrafo(s)"
            )
        else:
            self.paragraph_counter.setText("Parágrafo 0 de 0")
        if not paragraphs:
            self.teleprompter.setHtml(
                "<div style='color:#AAB5C0;text-align:center;padding:35px;'>"
                "Este relato ainda não possui texto. Volte ao projeto e adicione os parágrafos."
                "</div>"
            )
            return
        blocks = []
        for paragraph_index, paragraph in enumerate(visible):
            background = "#3B3018" if paragraph_index == 0 else "#17232D"
            color = "#FFF3D0" if paragraph_index == 0 else "#D6DEE6"
            blocks.append(
                f"<div style='background:{background};color:{color};padding:18px;"
                f"border-radius:9px;margin:8px 4px;font-size:20px;line-height:1.55;'>"
                f"{html.escape(paragraph)}</div>"
            )
        self.teleprompter.setHtml("<html><body style='background:#0B1219;'>" + "".join(blocks) + "</body></html>")
        self.teleprompter.verticalScrollBar().setValue(0)

    def move_teleprompter(self, direction):
        if not self.current_project:
            return
        sections = self.current_project.get("sections", [])
        if not sections:
            return
        section = sections[min(self.selected_section_index, len(sections) - 1)]
        paragraphs = split_paragraphs(section_text(section))
        if not paragraphs:
            return
        self.visible_paragraph_start = max(0, min(
            len(paragraphs) - 1, self.visible_paragraph_start + direction
        ))
        self.refresh_teleprompter()

    def configure_microphone(self):
        dialog = MicrophoneDialog(self.selected_microphone, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_microphone = dialog.selected_name()
            self.audio_device_label.setText(
                self.selected_microphone + "\nSeleção salva — captura ainda não conectada"
            )
            self.audio_status_label.setText("●  Dispositivo selecionado")

    def refresh_recordings(self):
        if self.recording_rows_layout is None:
            return
        clear_layout(self.recording_rows_layout)
        recordings = self.current_project.get("recordings", []) if self.current_project else []
        if not recordings:
            empty = QLabel("As gravações deste projeto aparecerão aqui.\nUse a opção abaixo para testar o mini-player com um vídeo local.")
            empty.setObjectName("Muted")
            empty.setWordWrap(True)
            self.recording_rows_layout.addWidget(empty)
        else:
            for recording in recordings:
                row = QFrame()
                row.setObjectName("RecordingRow")
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(px(5), px(5), px(7), px(5))
                row_layout.setSpacing(px(7))
                play = QPushButton("▶")
                play.setObjectName("PlayButton")
                play.setToolTip("Assistir gravação")
                play.clicked.connect(lambda checked=False, r=recording: self.play_recording(r))
                label = QLabel(recording.get("name", "Vídeo"))
                label.setObjectName("RecordingName")
                label.setWordWrap(True)
                row_layout.addWidget(play)
                row_layout.addWidget(label, 1)
                self.recording_rows_layout.addWidget(row)
        self.recording_rows_layout.addStretch()

    def import_video_for_review(self):
        if not self.current_project:
            QMessageBox.information(self, "Carregue um projeto", "Carregue um projeto antes de adicionar vídeos à revisão.")
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar vídeo para revisão",
            str(Path.home()),
            "Vídeos (*.mp4 *.mov *.mkv *.avi *.webm);;Todos os arquivos (*.*)",
        )
        if not path:
            return
        recording = {
            "id": str(uuid.uuid4()),
            "name": Path(path).name,
            "path": path,
            "added_at": now_text(),
        }
        self.current_project.setdefault("recordings", []).insert(0, recording)
        self.current_project["updated_at"] = now_text()
        self.store.save(self.current_project)
        self.refresh_recordings()
        self.play_recording(recording)

    def play_recording(self, recording):
        path = recording.get("path", "")
        if not path or not os.path.isfile(path):
            QMessageBox.warning(
                self,
                "Arquivo não encontrado",
                "O vídeo registrado neste projeto não está disponível neste computador.\n"
                "Selecione novamente um arquivo local para revisão.",
            )
            return
        if not MULTIMEDIA_AVAILABLE or self.player is None:
            QMessageBox.warning(
                self,
                "Mini-player indisponível",
                "O módulo Qt Multimedia não está disponível nesta instalação do PySide6.\n"
                "Instale/atualize o pacote PySide6 completo para habilitar a reprodução.",
            )
            return
        self.camera_stack.setCurrentIndex(1)
        self.camera_status.setText("REVISÃO DO VÍDEO")
        self.camera_status.setObjectName("ReviewBadge")
        self.camera_status.style().unpolish(self.camera_status)
        self.camera_status.style().polish(self.camera_status)
        self.back_to_camera_button.setVisible(True)
        self.player.setSource(QUrl.fromLocalFile(path))
        self.player_controls.setVisible(True)
        self.camera_bottom_label.setText("Revisão de gravação local  •  Mini-player")
        self.player_play_button.setText("Ⅱ")
        self.player.play()

    def format_time(self, milliseconds):
        seconds = max(0, int(milliseconds // 1000))
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def update_player_position(self, position):
        self.player_slider.setValue(position)
        self.player_time_label.setText(
            f"{self.format_time(position)} / {self.format_time(self.player.duration())}"
        )

    def update_player_duration(self, duration):
        self.player_slider.setRange(0, max(0, duration))
        self.player_time_label.setText(
            f"{self.format_time(self.player.position())} / {self.format_time(duration)}"
        )

    def seek_player(self, position):
        if self.player is not None:
            self.player.setPosition(position)

    def toggle_player(self):
        if self.player is None:
            return
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.player_play_button.setText("▶")
        else:
            self.player.play()
            self.player_play_button.setText("Ⅱ")

    def stop_player(self):
        if self.player is not None:
            self.player.stop()
            self.player_play_button.setText("▶")

    def return_to_camera(self):
        if self.player is not None:
            self.player.stop()
        self.camera_stack.setCurrentIndex(0)
        self.player_controls.setVisible(False)
        self.camera_bottom_label.setText("16:9   |   1080p   |   30 fps   •   Captura real ainda não conectada")
        self.camera_status.setText("AGUARDANDO CÂMERA")
        self.camera_status.setObjectName("WaitingBadge")
        self.camera_status.style().unpolish(self.camera_status)
        self.camera_status.style().polish(self.camera_status)
        self.back_to_camera_button.setVisible(False)

    def recording_not_connected(self):
        if not self.current_project:
            QMessageBox.information(self, "Nenhum projeto", "Carregue um projeto antes de iniciar uma sessão.")
            return
        QMessageBox.information(
            self,
            "Gravação ainda não integrada",
            "A interface está preparada, mas a captura real da câmera e do microfone ainda não foi implementada.\n\n"
            "O mini-player já pode ser testado importando um vídeo local em Últimas Gravações.",
        )


class PlaceholderPage(QWidget):
    def __init__(self, name, description):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(px(28), px(25), px(28), px(25))
        title = QLabel(name)
        title.setObjectName("PageTitle")
        description_label = QLabel(description)
        description_label.setObjectName("Muted")
        description_label.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(description_label)
        layout.addStretch()


class MainWindow(QMainWindow):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.prompt_store = PromptStore(store.directory)
        self.setWindowTitle("ARQUIVO RESTRITO — Fábrica de Vídeos")
        self.resize(px(1600), px(900))
        self.setMinimumSize(px(1100), px(700))

        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(px(112))
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_image = QLabel()
        image_path = os.path.join(os.path.dirname(__file__), "assets", "header_arquivo_restrito.png")
        if os.path.exists(image_path):
            header_image.setPixmap(QPixmap(image_path))
            header_image.setScaledContents(True)
        else:
            header_image.setText("ARQUIVO RESTRITO — FÁBRICA DE VÍDEOS")
            header_image.setObjectName("HeaderFallback")
        header_layout.addWidget(header_image)
        root_layout.addWidget(header)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(px(255))
        self.sidebar_layout = QVBoxLayout(sidebar)
        self.sidebar_layout.setContentsMargins(px(9), px(18), px(9), px(15))
        self.sidebar_layout.setSpacing(px(9))

        self.pages = QStackedWidget()
        self.pages.setObjectName("ContentArea")
        self.navigation_buttons = []
        self.page_indices = {}

        self.home_page = ProjectHomePage(self.store, self.open_project, self.new_project)
        self.episode_page = EpisodePage(self.store, self.prompt_store, self.editor_saved, self.show_home)
        self.recording_page = RecordingPage(self.store)
        self.prompts_page = PromptLibraryPage(self.prompt_store)

        self.add_page("Home", "⌂", self.home_page)
        self.add_page("Criar Novo Episódio", "＋", self.episode_page)
        self.add_page("Gravação", "◉", self.recording_page)
        self.add_page("Edição Automática", "⚒", PlaceholderPage("Edição Automática", "Montagem e edição dos vídeos gravados."))
        self.add_page("Cortes (Reels/Shorts)", "⊕", PlaceholderPage("Cortes (Reels/Shorts)", "Criação de vídeos curtos a partir dos projetos."))
        self.add_page("Configurações", "⚙", PlaceholderPage("Configurações", "Preferências gerais do sistema."))
        self.add_page("Prompts", "▤", self.prompts_page)

        self.sidebar_layout.addStretch()
        body.addWidget(sidebar)
        body.addWidget(self.pages, 1)
        root_layout.addLayout(body, 1)

        footer = QFrame()
        footer.setObjectName("Footer")
        footer.setFixedHeight(px(38))
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(px(18), 0, px(18), 0)
        dot = QLabel("●")
        dot.setObjectName("StatusDot")
        status = QLabel("Projetos e prompts salvos localmente  |  IA, câmera e gravação real ainda não conectadas")
        status.setObjectName("StatusLabel")
        footer_layout.addWidget(dot)
        footer_layout.addWidget(status)
        footer_layout.addStretch()
        root_layout.addWidget(footer)
        self.show_home()

    def add_page(self, name, icon, page):
        index = self.pages.addWidget(page)
        self.page_indices[name] = index
        button = QPushButton(f"{icon}   {name}")
        button.setObjectName("NavButton")
        button.setMinimumHeight(px(48))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(lambda checked=False, n=name: self.navigate(n))
        self.sidebar_layout.addWidget(button)
        self.navigation_buttons.append((name, button))
        return button

    def navigate(self, name):
        if name == "Criar Novo Episódio":
            self.new_project()
            return
        self.pages.setCurrentIndex(self.page_indices[name])
        self.update_nav(name)
        if name == "Home":
            self.home_page.refresh()
        elif name == "Prompts":
            self.prompts_page.refresh()

    def update_nav(self, active_name):
        for name, button in self.navigation_buttons:
            button.setObjectName("ActiveNav" if name == active_name else "NavButton")
            button.style().unpolish(button)
            button.style().polish(button)

    def show_home(self):
        self.pages.setCurrentIndex(self.page_indices["Home"])
        self.update_nav("Home")
        self.home_page.refresh()

    def new_project(self):
        self.episode_page.show_setup()
        self.pages.setCurrentIndex(self.page_indices["Criar Novo Episódio"])
        self.update_nav("Criar Novo Episódio")

    def open_project(self, project_id):
        project = self.store.get(project_id)
        if project:
            self.episode_page.load_project(project)
            self.pages.setCurrentIndex(self.page_indices["Criar Novo Episódio"])
            self.update_nav("Criar Novo Episódio")

    def editor_saved(self, project):
        self.home_page.refresh()
        if project and self.recording_page.current_project:
            if self.recording_page.current_project.get("id") == project.get("id"):
                self.recording_page.set_project(project)


STYLESHEET = """
QMainWindow, QWidget {
    background-color: #080D12;
    color: #E8E9EC;
    font-family: "Segoe UI";
    font-size: 14px;
}
QLabel { background-color: transparent; color: #E8E9EC; }
#Header { background-color: #101820; border-bottom: 2px solid #8F171B; }
#HeaderFallback { color: #F4F1EE; font-size: 30px; font-weight: 900; }
#Sidebar { background-color: #0C131B; border-right: 1px solid #27313B; }
#NavButton {
    background-color: transparent; color: #D1D5DA; border: none; border-radius: 9px;
    text-align: left; padding-left: 15px; font-size: 15px; font-weight: bold;
}
#NavButton:hover { background-color: #202A34; }
#ActiveNav {
    background-color: #351619; color: #FFBFC0; border: 1px solid #671B20;
    border-radius: 9px; text-align: left; padding-left: 15px; font-size: 15px; font-weight: bold;
}
#ContentArea { background-color: #080D12; }
#PageTitle { color: #F0F0F0; font-size: 25px; font-weight: bold; }
#Panel, #ProjectCard, #EditorSection, #EmptyState {
    background-color: #101820; border: 1px solid #303C49; border-radius: 12px;
}
#PanelTitle, #SectionHeading { color: #FFFFFF; font-size: 16px; font-weight: bold; }
#Muted { color: #A7B0BB; font-size: 12px; }
#CameraBadge {
    background-color: #173C2A; color: #B9F5C9; border-radius: 7px;
    padding: 6px 10px; font-weight: bold;
}
#WaitingBadge {
    background-color: #4A171B; color: #FFC2C5; border-radius: 7px;
    padding: 6px 9px; font-size: 11px; font-weight: bold;
}
#ReviewBadge {
    background-color: #17405A; color: #C7E9FF; border-radius: 7px;
    padding: 6px 9px; font-size: 11px; font-weight: bold;
}
#CameraPreview, #VideoPreview { background-color: #05080C; border: 1px solid #263440; border-radius: 9px; }
#PreviewIcon { color: #687786; font-size: 42px; }
#PreviewText { color: #8A96A3; font-size: 17px; font-weight: bold; }
#MeterInactive { background-color: #26333C; border: 1px solid #34424D; border-radius: 2px; }
#StorySelectButton {
    text-align: left; background-color: #17212B; border: 1px solid #263440;
    border-radius: 8px; color: #F1F3F5;
}
#StorySelectButton:checked { background-color: #153B2A; border: 1px solid #25864A; }
#StoryIcon { color: #D7E1EA; font-size: 20px; }
#StoryName { color: #F1F3F5; font-size: 13px; font-weight: bold; }
#SmallRedButton, #PrimaryButton {
    background-color: #A9000B; color: #FFFFFF; border: 1px solid #E12B35;
    border-radius: 8px; padding: 8px 12px; font-weight: bold;
}
#SmallRedButton:hover, #PrimaryButton:hover { background-color: #D71924; }
#StageButton, #ActiveStage {
    border-radius: 9px; padding: 6px; min-width: 92px;
}
#StageButton { background-color: #19232D; color: #F0F0F0; border: 1px solid #384552; }
#StageButton:hover { background-color: #273544; }
#ActiveStage { background-color: #49171B; color: #FFB9BA; border: 1px solid #B01C25; }
#StageMain { color: #F5F5F5; font-size: 14px; font-weight: bold; }
#StageDetail { color: #B4BDC6; font-size: 11px; }
#Teleprompter { background-color: #0B1219; color: #E8E9EC; border: 1px solid #273744; border-radius: 8px; padding: 7px; }
#AccentText { color: #F09A78; font-weight: bold; }
#NarrationWaiting { background-color: #202A34; color: #D4DCE4; border: 1px solid #44515E; border-radius: 8px; padding: 12px; font-weight: bold; }
#RecordingRow { background-color: #17212B; border: 1px solid #263440; border-radius: 8px; }
#PlayButton { background-color: #202D38; color: #E8EDF2; border: 1px solid #344451; border-radius: 8px; min-width: 38px; max-width: 38px; min-height: 38px; }
#PlayButton:hover { background-color: #344451; }
#RecordingName { color: #E8EDF2; font-size: 12px; }
#PlayerSlider::groove:horizontal { background: #263744; height: 5px; border-radius: 2px; }
#PlayerSlider::handle:horizontal { background: #D71924; width: 12px; margin: -5px 0; border-radius: 6px; }
#SecondaryButton, #DangerButton {
    background-color: #19232D; color: #F0F0F0; border: 1px solid #303C49;
    border-radius: 9px; padding: 9px 13px; font-weight: bold;
}
#SecondaryButton:hover { background-color: #273544; }
#DangerButton { color: #FFB9BA; border-color: #74343A; }
#Footer { background-color: #101820; border-top: 1px solid #303A45; }
#StatusDot { color: #24D653; font-size: 15px; }
#StatusLabel { color: #C9D0D7; font-size: 11px; }
#ProjectCard { min-height: 180px; }
#ProjectCard:hover { border: 1px solid #7C343B; }
#ProjectIcon { color: #E4B6B8; font-size: 25px; }
#ProjectTitle { color: #FFFFFF; font-size: 16px; font-weight: bold; }
#ProjectStatus { color: #FFCF9A; background-color: #392A1B; border-radius: 6px; padding: 4px 7px; font-size: 11px; font-weight: bold; }
#ProjectSummary { color: #AEB8C2; font-size: 12px; }
#SearchInput, #EditorInput {
    background-color: #111B24; color: #F0F2F4; border: 1px solid #344451;
    border-radius: 8px; padding: 10px; selection-background-color: #8F171B;
}
#SearchInput { min-height: 22px; }
#ViewToggle, #ViewToggleActive {
    background-color: #19232D; color: #D8E0E7; border: 1px solid #344451;
    border-radius: 8px; padding: 9px 12px; font-weight: bold;
}
#ViewToggleActive { background-color: #351619; color: #FFBFC0; border-color: #8F252C; }
#EmptyIcon { color: #657482; font-size: 42px; }
#EmptyText { color: #C5CED7; font-size: 15px; line-height: 1.5; }
#EditorText { background-color: #0D151D; color: #E8EDF2; border: 1px solid #344451; border-radius: 8px; padding: 8px; }
#ProjectPicker { background-color: #0D151D; color: #E8EDF2; border: 1px solid #344451; border-radius: 8px; padding: 6px; }

#SelectedBadge { color: #8FE1A5; background-color: #153B2A; border: 1px solid #267A49; border-radius: 7px; padding: 6px 10px; font-size: 11px; font-weight: bold; }
#EpisodeThemeInput { background-color: #142A39; color: #F3F6F8; border: 1px solid #3A5263; border-radius: 10px; padding: 13px; font-size: 16px; font-weight: bold; }
#EpisodeThemeDisplay { color: #F3F6F8; background-color: #142A39; border: 1px solid #344B5B; border-radius: 9px; padding: 12px; font-size: 17px; font-weight: bold; }
#EpisodeCombo, #CompactCombo { background-color: #0D1721; color: #F0F2F4; border: 1px solid #405362; border-radius: 8px; padding: 9px; min-height: 24px; }
#PromptSelectedName { color: #F0F4F7; font-size: 15px; font-weight: bold; }
#PromptReady { color: #62D88A; background-color: #153B2A; border: 1px solid #267A49; border-radius: 7px; padding: 4px 8px; font-size: 11px; font-weight: bold; }
#PromptPending { color: #F2C078; background-color: #3A2B18; border: 1px solid #76572B; border-radius: 7px; padding: 4px 8px; font-size: 11px; font-weight: bold; }
#CreateEpisodeButton { background-color: #008B36; color: white; border: 1px solid #1AC05B; border-radius: 12px; padding: 12px 18px; font-size: 17px; font-weight: bold; }
#CreateEpisodeButton:hover { background-color: #0AA64A; }
#ReportCard { background-color: #132A39; border: 1px solid #344B5B; border-radius: 12px; }
#ReportNumber { color: #E7B17A; font-size: 14px; font-weight: 900; letter-spacing: 1px; }
#ReportTitleInput { background-color: #142A39; color: #F1F4F6; border: 1px solid #486071; border-radius: 8px; padding: 8px 10px; font-size: 14px; font-weight: bold; }
#FieldLabel { color: #E8EDF2; font-size: 12px; font-weight: bold; }
#ReportTextEdit { background-color: #0D1B27; color: #E8EDF2; border: 1px solid #405464; border-radius: 7px; padding: 7px; font-size: 12px; }
#ProtagonistCaption { color: #E8C77F; font-size: 11px; font-weight: bold; }
#InlineProtagonistInput, #InlineAgeInput { background-color: transparent; color: #E8D59D; border: none; border-bottom: 1px solid #6A5A35; padding: 3px 5px; font-weight: bold; }
#MicrophoneButton { background-color: #202D38; color: #D5DCE5; border: 1px solid #465764; border-radius: 7px; min-width: 34px; max-width: 34px; min-height: 29px; max-height: 29px; }
#MicrophoneButton:hover { background-color: #2C3C49; }
#HarmonyButton { background-color: #087B3B; color: #FFFFFF; border: 1px solid #21B96B; border-radius: 8px; padding: 7px 12px; font-weight: bold; }
#HarmonyWaiting { color: #E5C27B; font-size: 11px; }
#CharacterNameRow, #ProtagonistNameRow { background-color: #1A3445; border: 1px solid #3B5363; border-radius: 6px; }
#ProtagonistNameRow { background-color: #F5E7B7; border: 1px solid #D7BD72; }
#CharacterNameInput { background-color: transparent; color: #E8EDF2; border: none; padding: 3px; }
#ProtagonistNameRow #CharacterNameInput { color: #24201A; font-weight: bold; }
#MiniActionButton { background-color: transparent; color: #B7C5D0; border: none; padding: 1px 4px; min-width: 20px; max-width: 24px; font-weight: bold; }
#MiniActionButton:hover { color: #FFFFFF; background-color: #354B5A; border-radius: 4px; }
#ProtagonistNameRow #MiniActionButton { color: #51472E; }
#PromptCheck { color: #C9D4DE; font-size: 11px; }
#SaveReportButton { background-color: #078B3C; color: white; border: 1px solid #22C465; border-radius: 7px; padding: 7px 12px; font-weight: bold; }
#PlanningCard { background-color: #15374A; border: 1px solid #2D5268; border-radius: 10px; }
#PlanningIcon { color: #78BCE8; font-size: 20px; }
#PlanningValue { color: #F2F5F7; font-size: 25px; font-weight: bold; }
#PlanningValueSmall { color: #F2F5F7; font-size: 14px; font-weight: bold; }
#PlanningProgress { background-color: #1D3441; border: none; border-radius: 5px; min-height: 9px; max-height: 9px; }
#PlanningProgress::chunk { background-color: #08B86C; border-radius: 5px; }

QScrollArea { border: none; }
QScrollBar:vertical { background: #0B1219; width: 12px; margin: 0; }
QScrollBar::handle:vertical { background: #344451; min-height: 28px; border-radius: 5px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName("ArquivoRestrito")
    app.setApplicationName(APP_NAME)
    configure_ui_scale()
    app.setStyleSheet(scaled_stylesheet(STYLESHEET))

    store = ProjectStore()
    window = MainWindow(store)
    window.showMaximized()
    sys.exit(app.exec())
