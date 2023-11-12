import sys
import sqlite3
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QMessageBox
from PyQt5.QtWidgets import QMainWindow, QWidget


class MainWindow(QMainWindow):
    def __init__(self):

        super().__init__()

        self.setFixedSize(850, 650)
        uic.loadUi('diets.ui', self)
        self.setWindowTitle("Диеты")
        self.conn = sqlite3.connect('my_database.db')
        self.tableWidget.setColumnWidth(1, 445)
        self.filters_current_index = 0
        self.diseaseBox_current_text = 'Пусто'
        self.receipt_widget = None
        self.new_window = None

        self.all_diets_table()

        self.searchButton.clicked.connect(self.search)
        self.filters.currentIndexChanged.connect(self.index_selection)
        self.diseaseBox.currentTextChanged.connect(self.text_selection)
        self.addButton.clicked.connect(self.add)
        self.updButton.clicked.connect(self.upd)
        self.deleteButton.clicked.connect(self.delete_elem)
        self.receiptButton.clicked.connect(self.show_receipt)

    def all_diets_table(self):
        cursor = self.conn.cursor()
        result = cursor.execute(f'''
            SELECT id, diet FROM diets
        ''').fetchall()

        if not result:
            self.tableWidget.setColumnCount(2)
            self.tableWidget.setRowCount(0)
        else:
            self.tableWidget.setColumnCount(len(result[0]))
            self.tableWidget.setRowCount(len(result))
            row = 0
            for i in result:
                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(i[0])))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(str(i[1])))
                row += 1

    def index_selection(self, i):
        self.filters_current_index = i

    def text_selection(self, i):
        self.diseaseBox_current_text = i

    def search(self):
        # noinspection PyBroadException
        try:
            self.errorLabel.setText('')
            cursor = self.conn.cursor()
            text = self.filterEdit.text()
            filters = {
                1: 'id',
                2: 'diet'
            }
            if self.diseaseBox_current_text == 'Пусто' and self.filters_current_index == 0:
                self.errorLabel.setText('Ничего не выбрано')

            elif self.diseaseBox_current_text == 'Пусто' and self.filters_current_index != 0:
                if text == '':
                    raise ValueError
                text = '"' + text + '"'
                result = cursor.execute(f'''
                    SELECT id, diet FROM diets WHERE {filters[self.filters_current_index]} = {text}
                ''').fetchall()
                row = 0
                if not result:
                    raise Exception
                self.tableWidget.setColumnCount(len(result[0]))
                self.tableWidget.setRowCount(len(result))
                for i in result:
                    self.tableWidget.setItem(row, 0, QTableWidgetItem(str(i[0])))
                    self.tableWidget.setItem(row, 1, QTableWidgetItem(str(i[1])))
                    row += 1

            elif self.diseaseBox_current_text != 'Пусто' and self.filters_current_index == 0:
                result = cursor.execute(f'''
                    SELECT id, diet FROM diets WHERE disease = "{self.diseaseBox_current_text}"
                ''').fetchall()
                row = 0
                if not result:
                    raise Exception
                self.tableWidget.setColumnCount(len(result[0]))
                self.tableWidget.setRowCount(len(result))
                for i in result:
                    self.tableWidget.setItem(row, 0, QTableWidgetItem(str(i[0])))
                    self.tableWidget.setItem(row, 1, QTableWidgetItem(str(i[1])))
                    row += 1

            else:
                if text == '':
                    raise ValueError
                text = '"' + text + '"'
                result = cursor.execute(f'''
                    SELECT id, diet FROM diets WHERE {filters[self.filters_current_index]} = {text} and disease = 
                    "{self.diseaseBox_current_text}"
                ''').fetchall()
                row = 0
                if not result:
                    raise Exception
                self.tableWidget.setColumnCount(len(result[0]))
                self.tableWidget.setRowCount(len(result))
                for i in result:
                    self.tableWidget.setItem(row, 0, QTableWidgetItem(str(i[0])))
                    self.tableWidget.setItem(row, 1, QTableWidgetItem(str(i[1])))
                    row += 1
        except ValueError:
            self.errorLabel.setText('Неправильный ввод')
        except Exception:
            self.errorLabel.setText('Ничего не найдено')

    def upd(self):
        self.errorLabel.setText('')
        self.filterEdit.setText('')
        self.filters.setCurrentIndex(0)
        self.diseaseBox.setCurrentIndex(0)
        cursor = self.conn.cursor()
        result = cursor.execute(f'''
            SELECT id, diet FROM diets
        ''').fetchall()
        if not result:
            self.tableWidget.setColumnCount(2)
            self.tableWidget.setRowCount(0)
        else:
            self.tableWidget.setColumnCount(len(result[0]))
            self.tableWidget.setRowCount(len(result))
            row = 0
            for i in result:
                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(i[0])))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(str(i[1])))
                row += 1

    def add(self):
        self.new_window = SecondWindow()
        self.new_window.show()

    def delete_elem(self):
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        ids = [self.tableWidget.item(i, 0).text() for i in rows]
        valid = QMessageBox.question(
            self, 'Подтвердите удаление', "Действительно удалить рецепты с номерами " + ",".join(ids),
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM diets WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids)
            self.conn.commit()

    def show_receipt(self):
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        ids = [self.tableWidget.item(i, 0).text() for i in rows]
        self.receipt_widget = ThirdWindow(ids)
        self.receipt_widget.show_reciept(ids)
        self.receipt_widget.show()


class SecondWindow(QMainWindow):
    def __init__(self):

        super().__init__()
        self.text1 = ''
        self.text2 = ''
        uic.loadUi('dietsADD_window.ui', self)
        self.setFixedSize(530, 420)
        self.setWindowTitle("Добавить рецепт")
        self.conn = sqlite3.connect('my_database.db')

        self.result_ing_string = ''
        self.result_count_string = ''

        self.countEdit.setAlignment(QtCore.Qt.AlignTop)
        self.IngredientsEdit.setAlignment(QtCore.Qt.AlignTop)
        self.addButton.clicked.connect(self.add)

    def add(self):
        try:

            ing_list = []
            count_list = []

            text1 = self.IngredientsEdit.toPlainText()
            text2 = self.countEdit.toPlainText()
            ing_list.append(text1)
            count_list.append(text2)

            ing_list = ing_list[0].split('\n')
            self.result_ing_string = '\n'.join(ing_list)

            count_list = count_list[0].split('\n')
            self.result_count_string = '\n'.join(count_list)

            self.errorLabel.setText('')
            title = self.titleEdit.text()
            if title == '':
                raise ValueError
            title = '"' + title + '"'
            cursor = self.conn.cursor()
            cursor.execute(f'''
                INSERT INTO diets(diet, receipt_ings, receipt_counts) VALUES({title}, "{self.result_ing_string}",
                "{self.result_count_string}")
            ''')

            self.conn.commit()
            self.titleEdit.setText('')
            self.IngredientsEdit.clear()
            self.countEdit.clear()
        except ValueError:
            self.errorLabel.setText('Неправильный ввод')


class ThirdWindow(QWidget):
    def __init__(self, ids):
        super().__init__()
        self.setFixedSize(600, 540)
        uic.loadUi('receipt_info.ui', self)
        self.setWindowTitle("Рецепт")
        self.conn = sqlite3.connect('my_database.db')

        cursor = self.conn.cursor()
        title = cursor.execute(f'''
            SELECT diet FROM diets WHERE id = {ids[0]}
        ''').fetchall()
        self.titleLabel.setText((title[0])[0])

    def show_reciept(self, ids):
        cursor = self.conn.cursor()
        result = cursor.execute(f'''
            SELECT receipt_ings, receipt_counts FROM diets WHERE id = {ids[0]}
        ''').fetchall()
        result2 = [i for i in result[0]]
        res_ing_list, res_count_list = result2

        res_ing_list = res_ing_list.split('\n')
        res_ing_list = '\n'.join(res_ing_list)

        res_count_list = res_count_list.split('\n')
        res_count_list = '\n'.join(res_count_list)

        self.text1.setText(f'{res_ing_list}')
        self.text2.setText(f'{res_count_list}')


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
