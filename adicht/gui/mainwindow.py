# -*- coding: utf-8 -*-

import os

from PyQt5.QtCore import pyqtSlot, QSettings, pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PyQt5.uic import loadUi

from adicht.report import Reporter


UI_DIR = os.path.join(os.path.dirname(__file__), 'ui')


class ReportThread(QThread):
    new_log_message = pyqtSignal(str)

    def __init__(self, output_dir, data_files, parent=None):
        QThread.__init__(self, parent)

        self._output_dir = output_dir
        self._data_files = data_files

    def run(self):
        reporter = Reporter(self._output_dir, self.new_log_message.emit)

        for entry in self._data_files:
            reporter.generate_report(entry)


class MainWindow(QMainWindow):
    new_log_message = pyqtSignal(str)

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        loadUi(os.path.join(UI_DIR, 'mainwindow.ui'), self)

        self._threads = []
        self._load()


    def append_log(self, msg):
        self.log_output.setHtml(self.log_output.toHtml() + msg)

    @pyqtSlot()
    def on_actionExit_triggered(self):
        self.close()

    @pyqtSlot()
    def on_actionAbout_Qt_triggered(self):
        QMessageBox.aboutQt(self)

    @pyqtSlot()
    def on_choose_files_button_clicked(self):
        files, ext_filter = QFileDialog.getOpenFileNames(self, 'Choose files to evaluate')

        if files:
            self.files_line_edit.setText(';'.join(files))
        self._handle_eval_button_activation()

    @pyqtSlot()
    def on_choose_output_directory_button_clicked(self):
        result = QFileDialog.getExistingDirectory(self, 'Choose output directory')

        if result:
            self.output_directory_edit.setText(result)
        self._handle_eval_button_activation()

    @pyqtSlot()
    def on_evaluate_button_clicked(self):
        thread = ReportThread(self.output_directory_edit.text(),
                              [entry.strip() for entry in self.files_line_edit.text().split(';')])

        thread.new_log_message.connect(self.append_log)
        self._threads.append(thread)

        thread.start()


    def closeEvent(self, event):
        self._save()
        return QMainWindow.closeEvent(self, event)

    def _handle_eval_button_activation(self):
        self.evaluate_button.setEnabled(bool(self.files_line_edit.text()) and bool(self.output_directory_edit.text()))

    def _save(self):
        settings = self._get_settings_object()
        settings.setValue('output_dir', self.output_directory_edit.text())

    def _load(self):
        settings = self._get_settings_object()
        self.output_directory_edit.setText(settings.value('output_dir', ''))

    def _get_settings_object(self):
        return QSettings('adicht_eval')