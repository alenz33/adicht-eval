# -*- coding: utf-8 -*-

import os

from PyQt5.QtCore import pyqtSlot, QSettings
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PyQt5.uic import loadUi

from adicht.report import Reporter


UI_DIR = os.path.join(os.path.dirname(__file__), 'ui')

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        loadUi(os.path.join(UI_DIR, 'mainwindow.ui'), self)

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
        reporter = Reporter(self.output_directory_edit.text())

        for entry in [entry.strip() for entry in self.files_line_edit.text().split(';')]:
            self.append_log('Start report generation for %s ...' % entry)
            reporter.generate_report(entry)

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