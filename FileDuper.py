import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QMessageBox

class DirectoryCopierApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Directory Structure Copier')

        self.source_label = QLabel('Source Directory:', self)
        self.source_entry = QLineEdit(self)
        self.source_button = QPushButton('Choose Directory', self)
        self.source_button.clicked.connect(self.select_source_directory)

        self.target_label = QLabel('Target Directory:', self)
        self.target_entry = QLineEdit(self)
        self.target_button = QPushButton('Choose Directory', self)
        self.target_button.clicked.connect(self.select_target_directory)

        self.confirm_button = QPushButton('Confirm', self)
        self.confirm_button.clicked.connect(self.confirm)

        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.clicked.connect(self.cancel)

        source_layout = QHBoxLayout()
        source_layout.addWidget(self.source_label)
        source_layout.addWidget(self.source_entry)
        source_layout.addWidget(self.source_button)

        target_layout = QHBoxLayout()
        target_layout.addWidget(self.target_label)
        target_layout.addWidget(self.target_entry)
        target_layout.addWidget(self.target_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(source_layout)
        main_layout.addLayout(target_layout)
        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.setGeometry(300, 300, 600, 150)
        self.show()

    def select_source_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Source Directory')
        if directory:
            self.source_entry.setText(directory)

    def select_target_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Target Directory')
        if directory:
            self.target_entry.setText(directory)

    def confirm(self):
        source_directory = self.source_entry.text().strip().strip("'\"")
        target_directory = self.target_entry.text().strip().strip("'\"")

        if not source_directory or not target_directory:
            QMessageBox.critical(self, "Error", "Both source and target directories must be specified.")
            return

        if not os.path.exists(source_directory):
            QMessageBox.critical(self, "Error", f"Source directory {source_directory} does not exist.")
            return

        if os.path.exists(target_directory) and os.listdir(target_directory):
            reply = QMessageBox.question(self, "Confirm", f"Target directory {target_directory} is not empty. Continue?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        if self.has_conflicting_files(source_directory, target_directory):
            QMessageBox.critical(self, "Error", "Conflicting files detected in the target directory. Operation aborted to avoid overwriting.")
            return

        self.start_copy_process(source_directory, target_directory)

    def has_conflicting_files(self, source_directory, target_directory):
        for root, _, files in os.walk(source_directory):
            relative_path = os.path.relpath(root, source_directory)
            target_path = os.path.join(target_directory, relative_path)
            for file in files:
                target_file_path = os.path.join(target_path, file)
                if os.path.exists(target_file_path):
                    return True
        return False

    def start_copy_process(self, source_directory, target_directory):
        self.hide()
        self.output_window = OutputWindow(source_directory, target_directory)
        self.output_window.show()

    def cancel(self):
        self.close()

class OutputWindow(QMainWindow):
    def __init__(self, source_directory, target_directory):
        super().__init__()
        self.source_directory = source_directory
        self.target_directory = target_directory
        self.initUI()
        self.copy_structure()

    def initUI(self):
        self.setWindowTitle('Copy Process Output')

        self.output_text = QTextEdit(self)
        self.output_text.setReadOnly(True)

        self.finish_button = QPushButton('Finish and Close', self)
        self.finish_button.clicked.connect(self.finish)

        layout = QVBoxLayout()
        layout.addWidget(self.output_text)
        layout.addWidget(self.finish_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.setGeometry(300, 300, 800, 400)

    def append_output(self, message):
        self.output_text.append(message)
        QApplication.processEvents()

    def copy_structure(self):
        self.append_output(f"Starting copy process from {self.source_directory} to {self.target_directory}")

        if not os.path.exists(self.target_directory):
            os.makedirs(self.target_directory)
            self.append_output(f"Created target directory: {self.target_directory}")

        for root, dirs, files in os.walk(self.source_directory):
            if os.path.islink(root):
                self.append_output(f"Skipping symbolic link: {root}")
                continue

            relative_path = os.path.relpath(root, self.source_directory)
            target_path = os.path.join(self.target_directory, relative_path)

            if not os.path.exists(target_path):
                try:
                    os.makedirs(target_path)
                    self.append_output(f"Created directory: {target_path}")
                except Exception as e:
                    self.append_output(f"Failed to create directory {target_path}: {e}")

            for file in files:
                source_file_path = os.path.join(root, file)
                target_file_path = os.path.join(target_path, file)

                if os.path.exists(target_file_path):
                    self.append_output(f"File {target_file_path} already exists. Operation aborted to avoid overwriting.")
                    return

                try:
                    with open(target_file_path, 'w') as empty_file:
                        pass
                    self.append_output(f"Created empty file: {target_file_path}")
                except Exception as e:
                    self.append_output(f"Failed to create file {target_file_path}: {e}")

        self.append_output("Directory structure copy process completed!")

    def finish(self):
        self.close()
        app.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DirectoryCopierApp()
    sys.exit(app.exec_())