import sys
from PyQt6.QtCore import QTimer, QTime
from PyQt6.QtWidgets import QLabel

class ReuniteClock(QLabel):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("font-size: 14px; padding: 5px;")
        self.setFixedHeight(30)

        # Initialize timer to update the clock every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every 1 second

        # Set the initial time
        self.update_time()

    def update_time(self):
        current_time = QTime.currentTime().toString("hh:mm AP")  # Format 12-hour with AM/PM
        self.setText(current_time)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test the clock module
    clock = ReuniteClock()
    clock.show()

    sys.exit(app.exec())
