import sys
import os
import subprocess
import threading
import configparser
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QScrollArea, QGridLayout, QApplication, QHBoxLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QGuiApplication


class AppLauncherThread(QThread):
    """Thread to launch the application without blocking the UI."""
    app_launched = pyqtSignal(str)

    def __init__(self, app_command):
        super().__init__()
        self.app_command = app_command

    def run(self):
        try:
            subprocess.run(self.app_command, check=True)
            self.app_launched.emit(f"Successfully launched: {self.app_command[0]}")
        except subprocess.CalledProcessError:
            self.app_launched.emit(f"Failed to launch: {self.app_command[0]}")

    def stop(self):
        """Ensure the thread is properly stopped if needed."""
        self.quit()
        self.wait()  # Ensure the thread has finished before deleting


class AppsMenu(QWidget):
    def __init__(self):
        super().__init__()

        # Remove the title bar, make it frameless, and set it as transparent
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set up the layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Create the close button and place it inside the window
        close_button = QPushButton("X")
        close_button.setFixedSize(20, 20)  # Smaller close button
        close_button.setStyleSheet("background-color: red; color: white; border: none; border-radius: 10px;")
        close_button.clicked.connect(self.close)

        # Create a horizontal layout for the close button
        button_layout = QHBoxLayout()
        button_layout.addWidget(close_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        button_layout.setContentsMargins(0, 0, 10, 0)  # Position the button slightly inside

        # Add the close button layout to the main layout
        layout.addLayout(button_layout)

        # Scrollable area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: white; border: none;")

        scroll_content = QWidget()
        grid_layout = QGridLayout(scroll_content)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(2, 1)
        grid_layout.setColumnStretch(3, 1)

        # Load applications and display them in the grid
        self.load_apps(grid_layout)

        scroll_content.setLayout(grid_layout)
        scroll_area.setWidget(scroll_content)

        layout.addWidget(scroll_area)
        self.setLayout(layout)

        # Set rounded corners for the window
        self.setStyleSheet("border-radius: 20px; background-color: rgba(255, 255, 255, 180);")

        # Ensure focus events work correctly
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Store a reference to the launcher thread for cleanup
        self.app_launcher_thread = None

    def load_apps(self, grid_layout):
        apps_dir = "/usr/share/applications/"
        
        # Loop over files in the applications directory
        for i, filename in enumerate(os.listdir(apps_dir)):
            if filename.endswith(".desktop"):
                app_path = os.path.join(apps_dir, filename)
                app_info = self.read_desktop_file(app_path)

                if app_info:
                    app_button = QPushButton(f"{app_info['Name']}")
                    app_button.setFixedSize(100, 100)
                    app_button.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; background-color: #f9f9f9;")

                    # Set the icon
                    icon = QIcon(app_info.get("Icon", ""))
                    app_button.setIcon(icon)
                    app_button.setIconSize(app_button.size())  # Set icon size to button size

                    # Connect the button click to launch the app and close the menu
                    app_button.clicked.connect(self.launch_app(app_info['Exec'], grid_layout))

                    grid_layout.addWidget(app_button, i // 4, i % 4)  # 4 columns

    def read_desktop_file(self, app_path):
        # Read the .desktop file and extract Name and Icon
        config = configparser.ConfigParser(interpolation=None)  # Disable interpolation
        config.read(app_path)

        if 'Desktop Entry' in config:
            app_info = {}
            app_info['Name'] = config.get('Desktop Entry', 'Name', fallback='Unknown')
            app_info['Icon'] = config.get('Desktop Entry', 'Icon', fallback='')
            app_info['Exec'] = config.get('Desktop Entry', 'Exec', fallback='')

            return app_info
        return None

    def launch_app(self, app_command, grid_layout):
        """Launch the application in a separate thread."""
        def run():
            # Close the apps menu
            self.close()

            # Split the command into a list to pass it to subprocess
            app_command_split = app_command.split()
            self.app_launcher_thread = AppLauncherThread(app_command_split)
            self.app_launcher_thread.start()

        return run

    def showEvent(self, event):
        # Center the window on the screen once it's visible
        screen = QGuiApplication.primaryScreen()  # Get the primary screen
        screen_geometry = screen.geometry()
        window_geometry = self.geometry()
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.move(x, y)
        super().showEvent(event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.close()  # Close the window when it loses focus

    def mousePressEvent(self, event):
        if not self.rect().contains(event.pos()):
            self.close()  # Close the window when clicking outside
        super().mousePressEvent(event)

    def closeEvent(self, event):
        # Clean up the thread properly
        if self.app_launcher_thread:
            self.app_launcher_thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apps_menu = AppsMenu()
    apps_menu.show()
    sys.exit(app.exec())
