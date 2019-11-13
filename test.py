import os
import sqlite3
import sys

import PIL.Image as Img
import PIL.ImageEnhance as Enhance
import PyQt5.QtCore as core
import PyQt5.QtGui as gui
import PyQt5.QtWidgets as wdgts
import cv2
import numpy as np


class ProcessingThread(core.QThread):
    current_signal = core.pyqtSignal(np.ndarray)
    cap = None
    pause = True

    def run(self):
        while True:
            if not self.pause:
                if self.cap and self.cap.isOpened():
                    ret, frame = self.cap.read()

                    if frame is None:
                        self.pause = True
                        continue

                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    current = gui.QImage(frame.data, frame.shape[1], frame.shape[0], gui.QImage.Format_RGB888)
                    self.current_signal.emit(frame)

                else:
                    print('VideoCapture is None')


class Ui_Dialog(wdgts.QMainWindow):

    def closeEvent(self, a0: gui.QCloseEvent):
        try:
            self.parent.load_materials()
            self.parent.combo_box_materials.clear()
            self.parent.combo_box_materials.addItems([mtrl[1] for mtrl in self.materials])
            self.parent.material_selected(0,False)
            self.close()
        except Exception as e:
            print(e)

    def push_button_delete_click(self):
        index = self.text_edit_material_id.toPlainText()
        try:
            index = int(index) - 1
            if 0 <= index <= len(self.materials) -1:
                connect = sqlite3.connect(self.db_name)
                crsr = connect.cursor()
                row = self.materials.pop(index)
                id = row[0]
                crsr.execute('DELETE FROM Materials WHERE ID=?', (id,))
                connect.commit()
                connect.close()
                self.load_materials()
                self.fill_table()
        except Exception as e:
            print(e)

        self.text_edit_material_id.setPlainText('')
        self.text_edit_material_id.clear()

    def push_button_add_click(self):
        material_name = self.text_edit_material_id.toPlainText()
        material_area = self.text_edit_material_area.toPlainText()
        material_area_std = self.text_edit_material_area_std.toPlainText()
        material_porous = self.text_edit_material_porous.toPlainText()
        material_porous_std = self.text_edit_materials_porous_std.toPlainText()

        data = [material_name, material_area, material_area_std, material_porous, material_porous_std]

        flag = [True if (m is not None and m != '') else False for m in data]

        if flag:
            try:
                material_area = float(material_area)
                material_area_std = float(material_area_std)
                material_porous = float (material_porous)
                material_porous_std = float (material_porous_std)
                connect = sqlite3.connect(self.db_name)
                crsr = connect.cursor()
                crsr.execute("""INSERT INTO Materials(NAME, PORE_AREA_MEAN, PORE_AREA_STD, POROUS_MEAN, POROUS_STD
                VALUES (?, ?, ?, ?, ?)""", (material_name, material_area, material_area_std,
                                            material_porous, material_porous_std))
                connect.commit()
                connect.close()
                self.load_materials()
                self.fi11_table()

            except Exception as e:
                print(e)

    def button_ok_click(self):

            self.parent.load_materials()
            self.parent.combo_box_materials.clear()
            self.parent.combo_box_materials.addItems([mtrl[1] for mtrl in self.materials])
            self.parent.material_selected(0, False)

            self.close()

    def load_materials(self):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        self.materials = cur.execute('SELECT * FROM Materials').fetchall()
        conn.close()

    def f111_table(self):
        while self.tableWidget.rowCount() > 0:
            self.tableWidget.renoveRow(0)

        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(len(self.materials))

        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Наименование', 'Площадь поры', 'Откл. от площади',
                                                    'Пористость', 'Откл. от пористости'])

        self.tableWidget.horizontalHeaderItem(0).setToolTip("ID записи в базе данных")
        self.tableWidget.horizontalHeaderItem(1).setToolTip("Наименование материала")
        self.tableWidget.horizontalHeaderItem(2).setToolTip("Нормальная площадь поры")
        self.tableWidget.horizontalHeaderItem(3).setToolTip("Отклонение от нормы площади поры")
        self.tableWidget.horizontalHeaderItem(4).setToolTip("Нормальная пористость")
        self.tableWidget.horizontalHeaderItem(5).setToolTip("OTicnoHeHne от нормы пористости")

        for i, row in enumerate(self.materials):

            self.tableWidget.setItem(i, 0, wdgts.QTableWidgetItem(str(row[0])))
            self.tableWidget.setItem(i, 1, wdgts.QTableWidgetItem(str(row[1])))
            self.tableWidget.setItem(i, 2, wdgts.QTableWidgetItem(str(row[2])))
            self.tableWidget.setItem(i, 3, wdgts.QTableWidgetItem(str(row[3])))
            self.tableWidget.setItem(i, 4, wdgts.QTableWidgetItem(str(row[4])))
            self.tableWidget.setItem(i, 5, wdgts.QTableWidgetItem(str(row[5])))

        # делаем ресайз колонок no содержимому
        self.tableWidget.resizeColumnsToContents()

    def retranslateUi(self):
        _translate = core.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Dialog"))
        self.group_box_add_row.setTitle(_translate("Dialog", "Добавить запись"))
        self.push_button_add_row.setText(_translate("Dialog", "Добавить"))
        self.text_edit_material_name.setPlaceholderText(_translate("Dialog", "название материала"))
        self.text_edit_material_area.setPlaceholderText(_translate("Dialog", "площадь поры"))
        self.text_edit_material_area_std.setPlaceholderText(_translate("Dialog", "откл.от площ."))
        self.text_edit_material_porous_std.setPlaceholderText(_translate("Dialog", "откл. от порист."))
        self.text_edit_material_porous.setPlaceholderText(_translate("Dialog", "пористость"))
        self.group_box_delete_row.setTitle(_translate("Dialog", "Удалить запись"))
        self.push_button_delete_row.setText(_translate("Dialog", "Удалить"))
        self.text_edit_material_id.setPlaceholderText(_translate("Dialog", "номер записи"))

    def __init__(self, parent = None, db_name = 'porousquality.db'):
        super(Ui_Dialog, self).__init__(parent)
        self.db_name = db_name
        self.parent = parent

        self.setObjectName("Dialog")
        self.resize(760, 410)
        self.buttonBox = wdgts.QDialogButtonBox(self)
        self.buttonBox.setGeometry(core.QRect(390, 370, 350, 30))
        self.buttonBox.setOrientation(core.Qt.Horizontal)
        self.buttonBox.setStandardButtons(wdgts.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("button8ox")

        self.tableWidget = wdgts.QTableWidget(self)
        self.tableWidget.setGeometry(core.QRect(10, 10, 740, 250))
        self.tableWidget.setObjectName("tableWidget")

        self.group_box_add_row = wdgts.QGroupBox(self)
        self.group_box_add_row.setGeometry(core.QRect(10, 260, 740, 50))
        self.group_box_add_row.setObjectName("group_box_add_row")
        self.push_button_add_row = wdgts.QPushButton(self.group_box_add_row)
        self.push_button_add_row.setGeometry(core.QRect(630, 20, 100, 25))
        self.push_button_add_row.setObjectName("push_button_add_row")
        self.text_edit_material_name = wdgts.QTextEdit(self.group_box_add_row)
        self.text_edit_material_name.setGeometry(core.QRect(10, 20, 135, 25))
        sizePolicy = wdgts.QSizePolicy(wdgts.QSizePolicy.Fixed, wdgts.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_edit_material_name.sizePolicy().hasHeightForWidth())
        self.text_edit_material_name.setSizePolicy(sizePolicy)
        self.text_edit_material_name.setInputMethodHints(core.Qt.ImhNone)
        self.text_edit_material_name.setVerticalScrollBarPolicy(core.Qt.ScrollBarAlwaysOff)
        self.text_edit_material_name.setHorizontalScrollBarPolicy(core.Qt.ScrollBarAlwaysOff)
        self.text_edit_material_name.setObjectName("text_edit_material_name")
        self.text_edit_material_area = wdgts.QTextEdit(self.group_box_add_row)
        self.text_edit_material_area.setGeometry(core.QRect(150, 20, 110, 25))
        sizePolicy = wdgts.QSizePolicy(wdgts.QSizePolicy.Fixed, wdgts.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_edit_material_area.sizePolicy().hasHeightForWidth())
        self.text_edit_material_area.setSizePolicy(sizePolicy)
        self.text_edit_material_area.setInputMethodHints(core.Qt.ImhNone)
        self.text_edit_material_area.setVerticalScrollBarPolicy(core.Qt.ScrollBarAlwaysOff)
        self.text_edit_material_area.setHorizontalScrollBarPolicy(core.Qt.ScrollBarAlwaysOff)
        self.text_edit_material_area.setObjectName("text_edit_material_area")
        self.text_edit_material_area_std = wdgts.QTextEdit(self.group_box_add_row)
        self.text_edit_material_area_std.setGeometry(core.QRect(265, 20, 110, 25))
        sizePolicy = wdgts.QSizePolicy(wdgts.QSizePolicy.Fixed, wdgts.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_edit_material_area_std.sizePolicy().hasHeightForWidth())
        self.text_edit_material_area_std.setSizePolicy(sizePolicy)
        self.text_edit_material_area_std.setInputMethodHints(core.Qt.ImhNone)
        self.text_edit_material_area_std.setVerticalScrollBarPolicy(core.Qt.ScrollBarAlwaysOff)
        self.text_edit_material_area_std.setHorizontalScrollBarPolicy(core.Qt.ScrollBarAlwaysOff)
        self.text_edit_material_area_std.setObjectName("text_edit_material_area_std")
        self.text_edit_material_porous_std = wdgts.QTextEdit(self.group_box_add_row)
        self.text_edit_material_porous_std.setGeometry(core.QRect(495, 20, 110, 25))
        sizePolicy = wdgts.QSizePolicy(wdgts.QSizePolicy.Fixed, wdgts.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_edit_material_porous_std.sizePolicy().hasHeightForWidth())
        self.text_edit_material_porous_std.setSizePolicy(sizePolicy)
        self.text_edit_material_porous_std.setInputMethodHints(core.Qt.ImhNone)
        self.text_edit_material_porous_std.setVerticalScrollBarPolicy(core.Qt.ScrollBarAlwaysOff)
        self.text_edit_material_porous_std.setHorizontalScrollBarPolicy(core.Qt.ScrollBarAlwaysOff)
        self.text_edit_material_porous_std.setObjectName("text_edit_material_porous_std")
        self.text_edit_material_porous = wdgts.QTextEdit(self.group_box_add_row)
        self.text_edit_material_porous.setGeometry(core.QRect(380, 20, 110, 25))
        sizePolicy = wdgts.QSizePolicy(wdgts.QSizePolicy.Fixed, wdgts.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_edit_material_porous.sizePolicy().hasHeightForWidth())
        self.text_edit_material_porous.setSizePolicy(sizePolicy)
        self.text_edit_material_porous.setInputMethodHints(core.Qt.ImhNone)
        self.text_edit_material_porous.setVerticalScrollBarPolicy(core.Qt.ScrollBarAlwaysOff)
        self.text_edit_material_porous.setHorizontalScrollBarPolicy(core.Qt.ScrollBarAlwaysOff)
        self.text_edit_material_porous.setObjectName("text_edit_material_porous")

        self.group_box_delete_row = wdgts.QGroupBox(self)
        self.group_box_delete_row.setGeometry(core.QRect(10, 310, 740, 50))
        self.group_box_delete_row.setObjectName("group_box_delete_row")
        self.push_button_delete_row = wdgts.QPushButton(self.group_box_delete_row)
        self.push_button_delete_row.setGeometry(core.QRect(630, 20, 100, 25))
        self.push_button_delete_row.setObjectName("push_button_delete_row")
        self.text_edit_material_id = wdgts.QTextEdit(self.group_box_delete_row)
        self.text_edit_material_id.setGeometry(core.QRect(10, 20, 115, 25))
        sizePolicy = wdgts.QSizePolicy(wdgts.QSizePolicy.Fixed, wdgts.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_edit_material_id.sizePolicy().hasHeightForWidth())
        self.text_edit_material_id.setSizePolicy(sizePolicy)
        self.text_edit_material_id.setInputMethodHints(core.Qt.ImhDigitsOnly)
        self.text_edit_material_id.setVerticalScrollBarPolicy(core.Qt.ScrollBarAlwaysOff)
        self.text_edit_material_id.setHorizontalScrollBarPolicy(core.Qt.ScrollBarAlwaysOff)
        self.text_edit_material_id.setObjectName("text_edit_n»aterial_id")

        self.load_materials()
        self.f111_table()

        self.buttonBox.raise_()
        self.tableWidget.raise_()
        self.group_box_delete_row.raise_()
        self.group_box_add_row.raise_()

        self.retranslateUi()
        self.buttonBox.accepted.connect(self.button_ok_click)
        #self.buttonBox.rejected.connect(self.button_canceL_click)
        self.push_button_add_row.clicked.connect(self.push_button_add_click)
        self.push_button_delete_row.clicked.connect(self.push_button_delete_click)

        core.QMetaObject.connectSlotsByName(self)


class MainWindow(wdgts.QMainWindow):
    def explore(self, image):
        """
        Входной аргумент:
        image - исследуемое изображение
        Выход:
        image - изображение с контурами пор
        агеа_с - отношение площади всех пор ко всей площади изображения (пористость)
        Len(bad_conrours) - количество 'плохих' пор
        """
        image = np.copy(image)
        # дополнительная обработка шумов
        blured = cv2.GaussianBlur(image, (5, 5), 0)
        # конвертация BGR формата в формат HSV
        hsv = cv2.cvtColor(blured, cv2.COLOR_BGR2HSV)

        lower_black = np.array([0, 0, 0])
        upper_black = np.array([120, 120, 120])
        # определяем маску для обнаружения контуров пор.
        # будут выделены поры в заданном диапозоне
        mask = cv2.inRange(hsv, lower_black, upper_black)
        # получаем массив конутров
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)


        good_contours = []
        bad_contours = []
        area_c = 0
        # находим 'хорошие' и 'плохие' поры
        for contour in contours:
            #также подсчитываем общую площадь пор
            area_c += cv2.contourArea(contour)
            if self.mat_area - self.mat_area_std <= cv2.contourArea(contour) <= self.mat_area + self.mat_area_std:
                good_contours.append(contour)
            else:
                bad_contours.append(contour)
        area_c = area_c / (image.shape[0] * image.shape[1])
        # выделяем'хорошие' поры зеленым цветом
        cv2.drawContours(image, good_contours, -1, (0, 255, 0), 3)
        #выделяем 'плохие' поры красным цветом
        cv2.drawContours(image, bad_contours, -1, (255, 0, 0), 3)
        return image, area_c, len(bad_contours)

    @core.pyqtSlot(np.ndarray)
    def set_current_frame(self, image):
        '''Converts a Qlmage into an opency f-IAT format '''
        self.set_original_frame(image)

    def set_original_frame(self, image):
        self.origin_img = cv2.resize(image, dsize=(300, 300))
        image = gui.QImage(self.origin_img.data, self.origin_img.shape[1], self.origin_img.shape[0],
                       gui.QImage.Format_RGB888)
        self.original_frame.setPixmap(gui.QPixmap.fromImage(image))

    def set_transformed_frame(self, image):
        image = Img.fromarray(image)

        image = Enhance.Contrast(image).enhance(self.contrast_slider.value() / 10)
        image = Enhance.Brightness(image).enhance(self.brightness_slider.value() / 10)
        image = Enhance.Sharpness(image).enhance(self.sharpness_slider.value() / 10)
        image = np.array(image)
        self.transform_img = image
        image = gui.QImage(image.data, image.shape[1], image.shape[0], gui.QImage.Format_RGB888)
        self.transformed_frame.setPixmap(gui.QPixmap.fromImage(image))

    def set_result_frame(self, image):
        self.result_img = image
        image, pore, bad_pores = self.explore(image)
        image = gui.QImage(image.data, image.shape[1], image.shape[1], gui.QImage.Format_RGB888)
        if self.mat_porous - self.mat_porous_std <= pore <= self.mat_porous + self.mat_porous_std:
            pore_rep = 'общая пористость в норме'
        else:
            pore_rep =" общая пористость не в норме"
        self.report_area.setText('Зеленым контуром отмечены поры, \n не привышающие норму по площади\n'
                                 'Красным контуром отмечены поры,\nпревышающие норму по площади\n\n'
                                 'Отчет: \nпористость - {}\n{}'.format(pore, pore_rep))
        self.report_text.setText('количество пор, площадь\n которых превышает норму: {} '.format(bad_pores))
        self.result_frame.setPixmap(gui.QPixmap.fromImage(image))


    def contrast_changed(self):
        self.set_transformed_frame(self.origin_img)
        self.set_result_frame(self.transform_img)

    def brightness_changed(self):
        self.set_transformed_frame(self.origin_img)
        self.set_result_frame(self.transform_img)

    def sharpness_changed(self):
        self.set_transformed_frame(self.origin_img)
        self.set_result_frame(self.transform_img)

    def material_selected(self, index, set_res_fr = True) :
        self.update_data(index)
        self.material_area.setText('Площадь поры:{}'.format(str(self.mat_area)))
        self.material_std_area.setText('Отк. от площади:{}'.format(str(self.mat_area)))
        self.material_porous.setText('Пористость:{}'.format(str(self.mat_porous)))
        self.material_std_porous.setText("Откл. от порист.: {}".format(str(self.mat_porous_std)))
        if set_res_fr:
            self.set_result_frame(self.transform_img)

    def open_file(self):
        if self.thread:
            self.shoot_button.setEnabled(False)
            self.thread.pause = True
            if self.thread.cap is not None:
                self.thread.cap.release()
                self.thread.cap = None
        filename, __ = wdgts.QFileDialog.getOpenFileName(self, "Open file", core.QDir.homePath())
        if filename != '':
            try:
                origin_img = Img.open(filename)
                origin_img = np.array(origin_img)
                self.set_original_frame(origin_img)
                self.set_transformed_frame(self.origin_img)
                self.set_result_frame((self.origin_img))
            except Exception as ex:
                print(ex)

    def set_via_webcam(self):
        if self.thread is None:
            self.thread = ProcessingThread(self)
            self.thread.current_signal.connect(self.set_current_frame)
            self.thread.start()
        if self.thread.cap is None:
            self.thread.cap = cv2.VideoCapture(0)
        if self.thread.pause is True:
            self.shoot_button.setEnabled(True)
            self.thread.pause = False

    def closeEvent(self, a0: gui.QCloseEvent):
        if self.thread is not None:
            self.thread.pause = True
        if self.thread.cap is not None:
            self.thread.cap.release()
        self.thread.exit(0)


    def shoot_button_click(self):
        if self.thread.pause:
            self.thread.pause = False
        else:
            self.thread.pause = True
            self.set_transformed_frame(self.origin_img)
            self.set_result_frame(self.origin_img)


    def load_materials(self):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        self.materials = cur.execute('SELECT * FROM Materials').fetchall()
        conn.close()

    def update_data(self, id: int):
        if len(self.materials) != 0:
            row = self.materials[np.min([np.max([0, id]), len(self.materials) - 1])]
            self.mat_mame = row[1]
            self.mat_area = row[2]
            self.mat_area_std = row[3]
            self.mat_porous = row[4]
            self.mat_porous_std = row[5]
        else:
            self.mat_name = 'Не задано'
            self.mat_area = 0
            self.mat_area_std = 0
            self.mat_propus = 0
            self.mat_porous_std = 0


    def dialog_show(self):
        dialog = Ui_Dialog(self, self.db_name)
        dialog.show()

    def __init__ (self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.db_name = 'porousqality.db'
        if not os.path.isfile(self.db_name):
            rows = [(0, 'Материал2', 12.0, 5.0, 0.1, 0.01),
                (1, 'Материал3', 9.00, 8.0, 0.15, 0.01),
                (2, 'Материал4', 15.0, 8.0, 0.2, 0.5),
                (3, 'Материал5', 14.0, 7.0, 0.3, 0.7)]
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("""CREATE TABLE Materials
                (ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                NAME TEXT,
                PORE_ARE_mEAN REAL NOT NULL,
                PORE_AREA_STD REAL NOT NULL,
                PROROUS_MEAN REAL NOT NULL,
                PROROUS_STD REAL NOT NULL)""")
            cur.executemany("""INSERT INTO Materials values (?,?,?,?,?,?)""", rows)
            conn.commit()
            conn.close()

        self.load_materials()
        font = gui.QFont()
        font.setPointSize(8)

        self.setObjectName('Window')
        self.resize(1000, 670)
        self.setMinimumSize(core.QSize(1000, 670))
        self.setMaximumSize(core.QSize(1000, 670))

        open_action = wdgts.QAction('&open', self)
        open_action.setStatusTip('Open file')
        open_action.triggered.connect(self.open_file)
        webcam_action = wdgts.QAction('&Webcam',self)
        webcam_action.setStatusTip('Set webcam')
        webcam_action.triggered.connect(self.set_via_webcam)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("&File")
        fileMenu.addAction(open_action)
        fileMenu.addAction(webcam_action)

        self.gridFrame = wdgts.QFrame(self)
        self.gridFrame.setGeometry(core.QRect(0, 20, 1000, 650))
        self.gridFrame.setMinimumSize(core.QSize(1000, 650))
        self.gridFrame.setMaximumSize(core.QSize(1000, 650))
        self.gridFrame.setObjectName('gridFrame')

        self.gridLayout = wdgts.QGridLayout(self.gridFrame)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName('gridLayout')

        self.original_frame = wdgts.QLabel(self.gridFrame)
        self.original_frame.setMinimumSize(core.QSize(300, 300))
        self.original_frame.setMaximumSize(core.QSize(300, 300))
        self.original_frame.setObjectName('original_frame')

        self.gridLayout.addWidget(self.original_frame, 0, 0, 1, 1)

        self.transformed_frame = wdgts.QLabel(self.gridFrame)
        self.transformed_frame.setMinimumSize(core.QSize(300, 300))
        self.transformed_frame.setMaximumSize(core.QSize(300, 300))
        self.transformed_frame.setObjectName('transformed_frame')

        self.gridLayout.addWidget(self.transformed_frame, 0, 1, 1, 1)

        self.result_frame = wdgts.QLabel(self.gridFrame)
        self.result_frame.setMinimumSize(core.QSize(300, 300))
        self.result_frame.setMaximumSize(core.QSize(300, 300))
        self.result_frame.setObjectName('result_frame')

        self.gridLayout.addWidget(self.result_frame, 1, 0, 1, 1)

        self.report_frame = wdgts.QFrame(self.gridFrame)
        self.report_frame.setMinimumSize(core.QSize(300, 300))
        self.report_frame.setMaximumSize(core.QSize(300, 300))
        self.report_frame.setObjectName('report_frame')

        self.report_layout = wdgts.QVBoxLayout(self.report_frame)
        self.report_layout.setObjectName('report_layout')
        self.gridLayout.addWidget(self.report_frame, 1, 1, 1, 1)

        self.report_area = wdgts.QLabel(self.report_frame)
        self.report_area.setGeometry(core.QRect(0, 0, 300, 130))
        self.report_area.setAlignment(core.Qt.AlignCenter)
        self.report_area.setFont(font)
        self.report_area.setObjectName('report_area')

        self.report_text = wdgts.QLabel(self.report_frame)
        self.report_text.setGeometry(core.QRect(0, 130, 300, 60))
        self.report_text.setAlignment((core.Qt.AlignCenter))
        self.report_text.setFont(font)
        self.report_text.setObjectName('report_text')


        self.tools_frame = wdgts.QFrame(self.gridFrame)
        self.tools_frame.setMinimumSize(core.QSize(300 ,300))
        self.tools_frame.setMaximumSize(core.QSize(300, 300))
        self.tools_frame.setObjectName('tools_frame')

        self.tools_layout = wdgts.QVBoxLayout(self.tools_frame)
        self.tools_layout.setObjectName('tools_layout')

        self.gridLayout.addWidget(self.tools_frame, 0, 2, 1, 1)

        self.options_frame = wdgts.QFrame(self.gridFrame)
        self.options_frame.setMaximumSize(core.QSize(300, 300))
        self.options_frame.setMinimumSize(core.QSize(300, 300))
        self.options_frame.setObjectName('options_frame')

        self.option_layout = wdgts.QVBoxLayout(self.options_frame)
        self.option_layout.setObjectName('option_layout')

        self.gridLayout.addWidget(self.options_frame, 1, 2, 1, 1)

        self.shoot_button = wdgts.QPushButton(parent=self.options_frame, text='Снимок')
        self.shoot_button.setGeometry(core.QRect(0, 250, 150, 50))
        self.shoot_button.clicked.connect(self.shoot_button_click)
        self.shoot_button.setEnabled(False)

        self.combo_box_materials = wdgts.QComboBox(self.options_frame)
        self.combo_box_materials.setGeometry(core.QRect(0, 0, 150, 40))
        self.combo_box_materials.addItems([mtrl[1] for mtrl in self.materials])
        self.combo_box_materials.activated.connect(self.material_selected)

        self.dialog_button = wdgts.QPushButton(parent=self.options_frame, text='изменить')
        self.dialog_button.setGeometry(core.QRect(0, 50, 150, 40))
        self.dialog_button.clicked.connect(self.dialog_show)

        self.material_area = wdgts.QLabel(self.options_frame)
        self.material_area.setGeometry(core.QRect(150, 0, 150, 40))
        self.material_area.setAlignment(core.Qt.AlignCenter)
        self.material_area.setFont(font)
        self.material_area.setObjectName('material_area')

        self.material_std_area = wdgts.QLabel(self.options_frame)
        self.material_std_area.setGeometry(core.QRect(150, 40, 150, 40))
        self.material_std_area.setAlignment(core.Qt.AlignCenter)
        self.material_std_area.setFont(font)
        self.material_std_area.setObjectName('material_std_area')

        self.material_porous = wdgts.QLabel(self.options_frame)
        self.material_porous.setGeometry(core.QRect(150, 80, 150, 40))
        self.material_porous.setAlignment(core.Qt.AlignCenter)
        self.material_porous.setFont(font)
        self.material_porous.setObjectName('material_prorous')

        self.material_std_porous = wdgts.QLabel(self.options_frame)
        self.material_std_porous.setGeometry(core.QRect(150, 120, 150, 40))
        self.material_std_porous.setAlignment(core.Qt.AlignCenter)
        self.material_std_porous.setFont(font)
        self.material_std_porous.setObjectName("material_porous")

        self.contrast_label = wdgts.QLabel(self.tools_frame)
        self.contrast_label.setFont(font)
        self.contrast_label.setAlignment(core.Qt.AlignCenter)
        self.contrast_label.setObjectName("contrast_label")
        self.contrast_label.setText('контрастность')

        self.contrast_slider = wdgts.QSlider(core.Qt.Horizontal)
        self.contrast_slider.setRange(-200, 200)
        self.contrast_slider.setTickPosition(wdgts.QSlider.TicksBothSides)
        self.contrast_slider.setValue(10)

        self.brightness_label = wdgts.QLabel(self.tools_frame)
        self.brightness_label.setFont(font)
        self.brightness_label.setAlignment(core.Qt.AlignCenter)
        self.brightness_label.setObjectName("brightness_label")
        self.brightness_label.setText('яркость ')

        self.brightness_slider = wdgts.QSlider(core.Qt.Horizontal)
        self.brightness_slider.setRange(-50, 250)
        self.brightness_slider.setTickPosition(wdgts.QSlider.TicksBothSides)
        self.brightness_slider.setValue(10)

        self.sharpness_label = wdgts.QLabel(self.tools_frame)
        self.sharpness_label.setFont(font)
        self.sharpness_label.setAlignment(core.Qt.AlignCenter)
        self.sharpness_label.setObjectName("sharpness_label")
        self.sharpness_label.setText('резкость')

        self.sharpness_slider = wdgts.QSlider(core.Qt.Horizontal)
        self.sharpness_slider.setRange(-200, 200)
        self.sharpness_slider.setTickPosition(wdgts.QSlider.TicksBothSides)
        self.sharpness_slider.setValue(10)

        self.tools_layout.addWidget(self.contrast_label)
        self.tools_layout.addWidget(self.contrast_slider)

        self.tools_layout.addWidget(self.brightness_label)
        self.tools_layout.addWidget(self.brightness_slider)

        self.tools_layout.addWidget(self.sharpness_label)
        self.tools_layout.addWidget(self.sharpness_slider)

        self.contrast_slider.valueChanged.connect(self.contrast_changed)
        self.brightness_slider.valueChanged.connect(self.brightness_changed)
        self.sharpness_slider.valueChanged.connect(self.sharpness_changed)

        self.material_selected(0, False)

        self.setWindowTitle("Quality porous material")
        self.thread = None

        blank_img = 255 * np.ones(shape=(300, 300, 3), dtype=np.uint8)
        self.set_original_frame(blank_img)
        self.set_transformed_frame(self.origin_img)
        self.set_result_frame(self.transform_img)



class App(wdgts.QApplication):
    def __init__(self, *args):
        super(App, self).__init__(*args)
        self.main = MainWindow()
        self.main.show()

app = App(sys.argv)
sys.exit(app.exec())