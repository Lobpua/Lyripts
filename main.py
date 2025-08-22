import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QMessageBox,
    QLineEdit,
    QDialog,
    QFormLayout,
    QComboBox,
)
from settings import AppSettings
from autoclicker import AutoClicker
from resolution import ResolutionChanger


class ControlApp(QWidget):
    BG_COLOR = QColor(20, 19, 20, 255)
    RADIUS = 33

    def __init__(self) -> None:
        super().__init__()
        self._drag_pos = QPoint()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.97)
        self.settings = AppSettings()
        self.clicker = AutoClicker(self.settings)
        self.res_changer = ResolutionChanger(self.settings)
        self._build_ui()
        self._connect()
        self._update_state()

    def _build_ui(self) -> None:
        self.setWindowTitle("Lyripts")
        self.resize(400, 360)
        font = QFont("Roboto", 10)
        self.setFont(font)
        self.title_label = QLabel("Lyripts")
        self.title_label.setStyleSheet("color:white;font-size:18px;font-weight:600;")
        self.btn_toggle = QPushButton("Автокликер: выкл")
        self.btn_set_res = QPushButton("Применить разрешение")
        self.btn_restore_res = QPushButton("Вернуть разрешение")
        self.btn_settings = QPushButton("Настройки")
        self.btn_quit = QPushButton("Выход")
        for b in (self.btn_toggle, self.btn_set_res, self.btn_restore_res, self.btn_settings, self.btn_quit):
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(
                """
                QPushButton{background:#a78fff;color:#111;padding:10px 14px; border:none; border-radius:14px;}
                QPushButton:hover{background:#9277d8;}
                QPushButton:pressed{background:#7e66c2;}
                """
            )
        top_bar = QHBoxLayout()
        top_bar.addWidget(self.title_label)
        top_bar.addStretch()
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        layout.addLayout(top_bar)
        layout.addWidget(self.btn_toggle)
        layout.addWidget(self.btn_set_res)
        layout.addWidget(self.btn_restore_res)
        layout.addStretch()
        layout.addWidget(self.btn_settings)
        layout.addWidget(self.btn_quit)
        self.setLayout(layout)

    def _connect(self) -> None:
        self.btn_toggle.clicked.connect(self.toggle_mouse_spam)
        self.btn_set_res.clicked.connect(self.change_resolution)
        self.btn_restore_res.clicked.connect(self.reset_resolution)
        self.btn_settings.clicked.connect(self.open_settings)
        self.btn_quit.clicked.connect(self.close)

    def _update_state(self) -> None:
        self.btn_toggle.setText(
            f"Автокликер: {'вкл' if self.clicker.is_active() else 'выкл'}"
        )

    def toggle_mouse_spam(self) -> None:
        self.clicker.toggle()
        self._update_state()

    def change_resolution(self) -> None:
        ok = self.res_changer.set_desired()
        if not ok:
            self._show_message("Ошибка", "Неверно заполнены поля желаемого разрешения или отсутствует QRes.exe")

    def reset_resolution(self) -> None:
        ok = self.res_changer.restore_original()
        if not ok:
            self._show_message("Ошибка", "Неверно заполнены поля исходного разрешения или отсутствует QRes.exe")

    def open_settings(self) -> None:
        dialog = SettingsDialog(self, self.settings)
        if dialog.exec_() == QDialog.Accepted:
            self.settings.save()
            self._update_state()

    def _show_message(self, title: str, text: str) -> None:
        mb = QMessageBox(self)
        mb.setIcon(QMessageBox.Warning)
        mb.setWindowTitle(title)
        mb.setText(text)
        mb.exec_()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.BG_COLOR))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), self.RADIUS, self.RADIUS)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def closeEvent(self, event):
        self.clicker.stop()
        event.accept()


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget, settings: AppSettings) -> None:
        super().__init__(parent)
        self.settings = settings
        self._drag_pos = QPoint()
        self.setWindowTitle("Настройки")
        self.setModal(True)
        self.resize(350, 400)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._build_ui()
        self._load_values()

    def _build_ui(self) -> None:
        layout = QFormLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        title = QLabel("Настройки")
        title.setStyleSheet("color:white;font-size:18px;font-weight:600;margin-bottom:10px;")
        layout.addRow(title)
        clicker_label = QLabel("Настройки автокликера:")
        clicker_label.setStyleSheet("color:white;font-size:14px;font-weight:500;margin-top:10px;")
        layout.addRow(clicker_label)
        self.trigger_combo = QComboBox()
        self.trigger_combo.addItems(["mouse1", "mouse2", "mouse3", "mouse4", "mouse5"])
        self.trigger_combo.setStyleSheet(self._combo_style())
        trigger_label = QLabel("Кнопка триггера:")
        trigger_label.setStyleSheet("color:white;font-size:13px;")
        layout.addRow(trigger_label, self.trigger_combo)
        self.spam_combo = QComboBox()
        self.spam_combo.addItems(["ЛКМ", "ПКМ", "СКМ"])
        self.spam_combo.setStyleSheet(self._combo_style())
        spam_label = QLabel("Кнопка спама:")
        spam_label.setStyleSheet("color:white;font-size:13px;")
        layout.addRow(spam_label, self.spam_combo)
        self.interval_edit = QLineEdit()
        self.interval_edit.setStyleSheet(self._edit_style())
        self.interval_edit.setPlaceholderText("60")
        interval_label = QLabel("Интервал (мс):")
        interval_label.setStyleSheet("color:white;font-size:13px;")
        layout.addRow(interval_label, self.interval_edit)
        res_label = QLabel("Настройки разрешения:")
        res_label.setStyleSheet("color:white;font-size:14px;font-weight:500;margin-top:15px;")
        layout.addRow(res_label)
        orig_label = QLabel("Исходное разрешение:")
        orig_label.setStyleSheet("color:white;font-size:13px;font-weight:500;")
        layout.addRow(orig_label)
        self.orig_width = QLineEdit()
        self.orig_width.setStyleSheet(self._edit_style())
        self.orig_width.setPlaceholderText("1920")
        orig_width_label = QLabel("Ширина:")
        orig_width_label.setStyleSheet("color:white;font-size:13px;")
        layout.addRow(orig_width_label, self.orig_width)
        self.orig_height = QLineEdit()
        self.orig_height.setStyleSheet(self._edit_style())
        self.orig_height.setPlaceholderText("1080")
        orig_height_label = QLabel("Высота:")
        orig_height_label.setStyleSheet("color:white;font-size:13px;")
        layout.addRow(orig_height_label, self.orig_height)
        self.orig_refresh = QLineEdit()
        self.orig_refresh.setStyleSheet(self._edit_style())
        self.orig_refresh.setPlaceholderText("60")
        orig_refresh_label = QLabel("Частота (Гц):")
        orig_refresh_label.setStyleSheet("color:white;font-size:13px;")
        layout.addRow(orig_refresh_label, self.orig_refresh)
        desired_label = QLabel("Желаемое разрешение:")
        desired_label.setStyleSheet("color:white;font-size:13px;font-weight:500;margin-top:10px;")
        layout.addRow(desired_label)
        self.desired_width = QLineEdit()
        self.desired_width.setStyleSheet(self._edit_style())
        self.desired_width.setPlaceholderText("1280")
        desired_width_label = QLabel("Ширина:")
        desired_width_label.setStyleSheet("color:white;font-size:13px;")
        layout.addRow(desired_width_label, self.desired_width)
        self.desired_height = QLineEdit()
        self.desired_height.setStyleSheet(self._edit_style())
        self.desired_height.setPlaceholderText("720")
        desired_height_label = QLabel("Высота:")
        desired_height_label.setStyleSheet("color:white;")
        layout.addRow(desired_height_label, self.desired_height)
        self.desired_refresh = QLineEdit()
        self.desired_refresh.setStyleSheet(self._edit_style())
        self.desired_refresh.setPlaceholderText("60")
        desired_refresh_label = QLabel("Частота (Гц):")
        desired_refresh_label.setStyleSheet("color:white;font-size:13px;")
        layout.addRow(desired_refresh_label, self.desired_refresh)
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        for btn in (self.save_btn, self.cancel_btn):
            btn.setStyleSheet(self._button_style())
            btn.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addRow(button_layout)
        self.setLayout(layout)
        self.save_btn.clicked.connect(self._save_and_accept)
        self.cancel_btn.clicked.connect(self.reject)

    def _load_values(self) -> None:
        data = self.settings.data
        trigger = data.get("trigger_button", "mouse4")
        if trigger in ["mouse1", "mouse2", "mouse3", "mouse4", "mouse5"]:
            self.trigger_combo.setCurrentText(trigger)
        spam = data.get("spam_button", "ЛКМ")
        if spam in ["ЛКМ", "ПКМ", "СКМ"]:
            self.spam_combo.setCurrentText(spam)
        interval = data.get("click_interval_ms", 60)
        self.interval_edit.setText(str(interval))
        orig_res = data.get("original_resolution", {})
        self.orig_width.setText(orig_res.get("width", ""))
        self.orig_height.setText(orig_res.get("height", ""))
        self.orig_refresh.setText(orig_res.get("refresh", ""))
        desired_res = data.get("desired_resolution", {})
        self.desired_width.setText(desired_res.get("width", ""))
        self.desired_height.setText(desired_res.get("height", ""))
        self.desired_refresh.setText(desired_res.get("refresh", ""))

    def _save_and_accept(self) -> None:
        self.settings.data["trigger_button"] = self.trigger_combo.currentText()
        self.settings.data["spam_button"] = self.spam_combo.currentText()
        try:
            interval = int(self.interval_edit.text() or "60")
            self.settings.set_click_interval(max(1, interval))
        except ValueError:
            self.settings.set_click_interval(60)
        self.settings.data["original_resolution"] = {
            "width": self.orig_width.text().strip(),
            "height": self.orig_height.text().strip(),
            "refresh": self.orig_refresh.text().strip(),
        }
        self.settings.data["desired_resolution"] = {
            "width": self.desired_width.text().strip(),
            "height": self.desired_height.text().strip(),
            "refresh": self.desired_refresh.text().strip(),
        }
        self.accept()

    def _edit_style(self) -> str:
        return """
            QLineEdit {
                background:#333;
                color:white;
                border:1px solid #555;
                border-radius:6px;
                padding:8px;
                font-size:13px;
            }
            QLineEdit:focus {
                border-color:#a78fff;
            }
        """

    def _combo_style(self) -> str:
        return """
            QComboBox {
                background:#333;
                color:white;
                border:1px solid #555;
                border-radius:6px;
                padding:8px;
                font-size:13px;
            }
            QComboBox:focus {
                border-color:#a78fff;
            }
            QComboBox::drop-down {
                border:none;
            }
            QComboBox::down-arrow {
                image:none;
                border-left:5px solid transparent;
                border-right:5px solid transparent;
                border-top:5px solid white;
                margin-right:5px;
            }
        """

    def _button_style(self) -> str:
        return """
            QPushButton {
                background:#a78fff;
                color:#111;
                padding:10px 18px;
                border:none;
                border-radius:12px;
                font-size:13px;
                font-weight:500;
            }
            QPushButton:hover {
                background:#9277d8;
            }
            QPushButton:pressed {
                background:#7e66c2;
            }
        """

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(25, 25, 25, 250)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()


def main() -> None:
    app = QApplication(sys.argv)
    window = ControlApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
