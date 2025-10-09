import os
os.environ["QT_QPA_PLATFORM"] = "xcb"
os.environ["QT_OPENGL"] = "software"
os.environ["QT_QUICK_BACKEND"] = "software"

from PySide6.QtWidgets import QApplication, QLabel

app = QApplication([])
label = QLabel("Test OpenGL software")
label.show()
app.exec()
