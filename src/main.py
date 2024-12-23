import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QHBoxLayout, QPushButton, QLabel,
    QWidget, QSystemTrayIcon, QMenu, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from mod_clock import ReuniteClock
from mod_apps import AppsMenu

class QtPanel(QMainWindow):
    def __init__(self, debug_mode=False):
        super().__init__()

        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        if not debug_mode:
            flags |= Qt.WindowType.Tool
        self.setWindowFlags(flags)
        screen_geometry = app.primaryScreen().geometry()
        self.setGeometry(0, 0, screen_geometry.width(), 30) 

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        main_widget.setLayout(main_layout)

  
        menu_button = QPushButton("⠿") 
        menu_button.setFixedSize(30, 30)
        menu_button.setStyleSheet("border: none;")
        menu_button.clicked.connect(self.show_apps_menu)

        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        clock_label = ReuniteClock() 

        settings_button = QPushButton("⚙")
        settings_button.setFixedSize(30, 30)
        settings_button.setStyleSheet("border: none;")

        main_layout.addWidget(menu_button)
        main_layout.addSpacerItem(spacer)
        main_layout.addWidget(clock_label)
        main_layout.addWidget(settings_button)

        self.tray_icon = QSystemTrayIcon(QIcon("your_icon_path_here.png"), self)
        tray_menu = QMenu()
        tray_menu.addAction("Quit", self.close)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def show_apps_menu(self):
        self.apps_menu = AppsMenu()
        self.apps_menu.setGeometry(self.x() + 10, self.y() +    40,    400, 600)  # Position below the panel
        self.apps_menu.show()


if __name__ == "__main__":
    debug_mode = "-d" in sys.argv
    app = QApplication(sys.argv)
    panel = QtPanel(debug_mode=debug_mode)
    panel.show()
    sys.exit(app.exec())
