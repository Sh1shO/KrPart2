from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTableWidget, QWidget, QTableWidgetItem, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDialog, QFormLayout, QDateEdit, QSpinBox, QComboBox, QMessageBox
from PySide6.QtCore import QDate
from db import get_session, Employee, Department, Project, Task, EmployeeProject
from datetime import datetime

class BaseDialog(QDialog):
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.layout = QFormLayout(self)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        cancel_button = QPushButton("Отмена")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        self.buttons_layout = buttons_layout

class DepartmentDialog(BaseDialog):
    def __init__(self, parent=None, department=None):
        super().__init__(parent, "Отдел")
        
        self.name = QLineEdit()
        self.layout.addRow("Название:", self.name)
        
        if department:
            self.name.setText(department.name)
        
        self.layout.addRow(self.buttons_layout)

class EmployeeDialog(BaseDialog):
    def __init__(self, parent=None, employee=None):
        super().__init__(parent, "Сотрудник")

        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.position = QLineEdit()
        self.salary = QSpinBox()
        self.salary.setRange(0, 1000000)
        self.hire_date = QDateEdit()
        self.hire_date.setCalendarPopup(True)
        self.hire_date.setDate(QDate.currentDate())
        self.department = QComboBox()

        session = get_session()
        departments = session.query(Department).all()
        for dept in departments:
            self.department.addItem(dept.name, dept.id)

        add_dept_button = QPushButton("Добавить отдел")
        add_dept_button.clicked.connect(self.add_department)

        self.layout.addRow("Имя:", self.first_name)
        self.layout.addRow("Фамилия:", self.last_name)
        self.layout.addRow("Должность:", self.position)
        self.layout.addRow("Зарплата:", self.salary)
        self.layout.addRow("Дата приема:", self.hire_date)
        dept_layout = QHBoxLayout()
        dept_layout.addWidget(self.department)
        dept_layout.addWidget(add_dept_button)
        self.layout.addRow("Отдел:", dept_layout)
        
        if employee:
            self.first_name.setText(employee.first_name)
            self.last_name.setText(employee.last_name)
            self.position.setText(employee.position)
            self.salary.setValue(employee.salary)
            self.hire_date.setDate(QDate.fromString(str(employee.hire_date), "yyyy-MM-dd"))
            if employee.department_id:
                index = self.department.findData(employee.department_id)
                self.department.setCurrentIndex(index)
        
        self.layout.addRow(self.buttons_layout)

    def add_department(self):
        dialog = DepartmentDialog(self)
        if dialog.exec():
            try:
                session = get_session()
                new_department = Department(name=dialog.name.text())
                session.add(new_department)
                session.commit()

                self.department.addItem(new_department.name, new_department.id)
                self.department.setCurrentIndex(self.department.count() - 1)
                
                QMessageBox.information(self, "Успех", "Отдел успешно добавлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении отдела: {str(e)}")

class TaskDialog(BaseDialog):
    def __init__(self, parent=None, task=None, edit_mode=False):
        super().__init__(parent, "Задача")
        
        self.name = QLineEdit()
        self.description = QLineEdit()
        self.status = QComboBox()
        self.status.addItems(["в процессе", "завершена", "отменена"])
        self.assignee = QComboBox()
        
        session = get_session()
        employees = session.query(Employee).all()
        for emp in employees:
            self.assignee.addItem(f"{emp.first_name} {emp.last_name}", emp.id)
        
        self.layout.addRow("Название:", self.name)
        self.layout.addRow("Описание:", self.description)
        self.layout.addRow("Статус:", self.status)
        self.layout.addRow("Исполнитель:", self.assignee)
        
        if task:
            self.name.setText(task.name)
            self.description.setText(task.description)
            self.status.setCurrentText(task.status)
            if task.assignee_id:
                index = self.assignee.findData(task.assignee_id)
                self.assignee.setCurrentIndex(index)
        
        if edit_mode:
            self.name.setEnabled(False)
            self.description.setEnabled(False)
            self.assignee.setEnabled(False)
        
        self.layout.addRow(self.buttons_layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление компанией")
        self.setGeometry(200, 200, 1024, 768)
        
        self.setup_ui()
        self.show_employees()
        self.load_employees_data()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        search_layout = QHBoxLayout()
        search_label = QLabel("Поиск")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст для поиска")
        self.search_input.textChanged.connect(self.search_items)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        buttons_layout = QHBoxLayout()
        self.employees_button = QPushButton("Сотрудники")
        self.tasks_button = QPushButton("Задачи")
        self.add_button = QPushButton("Добавить")
        self.edit_button = QPushButton("Редактировать")
        
        for button in [self.employees_button, self.tasks_button, 
                      self.add_button, self.edit_button]:
            buttons_layout.addWidget(button)
        layout.addLayout(buttons_layout)

        self.employees_table = QTableWidget()
        self.tasks_table = QTableWidget()
        layout.addWidget(self.employees_table)
        layout.addWidget(self.tasks_table)

        self.employees_button.clicked.connect(self.show_employees)
        self.tasks_button.clicked.connect(self.show_tasks)
        self.add_button.clicked.connect(self.add_item)
        self.edit_button.clicked.connect(self.edit_item)

    def load_data(self, model, table_widget, headers, data_function):
        session = get_session()
        self.current_items = session.query(model).all()
        table_widget.setRowCount(len(self.current_items))
        table_widget.setColumnCount(len(headers))
        table_widget.setHorizontalHeaderLabels(headers)

        for row, item in enumerate(self.current_items):
            for col, value in enumerate(data_function(item)):
                table_widget.setItem(row, col, QTableWidgetItem(str(value)))

        table_widget.resizeColumnsToContents()

    def load_employees_data(self):
        headers = ["Имя", "Фамилия", "Должность", "Зарплата", "Дата приема", "Отдел"]
        def get_employee_data(emp):
            return [
                emp.first_name,
                emp.last_name,
                emp.position,
                emp.salary,
                emp.hire_date,
                emp.fk_department.name if emp.fk_department else ""
            ]
        self.load_data(Employee, self.employees_table, headers, get_employee_data)

    def load_tasks_data(self):
        headers = ["Название", "Описание", "Статус", "Исполнитель"]
        def get_task_data(task):
            return [
                task.name,
                task.description,
                task.status,
                f"{task.fk_assignee.first_name} {task.fk_assignee.last_name}" if task.fk_assignee else ""
            ]
        self.load_data(Task, self.tasks_table, headers, get_task_data)

    def show_employees(self):
        self.employees_table.show()
        self.tasks_table.hide()
        self.current_table = self.employees_table
        self.load_employees_data()

    def show_tasks(self):
        self.employees_table.hide()
        self.tasks_table.show()
        self.current_table = self.tasks_table
        self.load_tasks_data()

    def search_items(self, search_text):
        if not search_text:
            if self.current_table == self.employees_table:
                self.load_employees_data()
            else:
                self.load_tasks_data()
            return

        filtered_items = []
        search_text = search_text.lower()
        
        for item in self.current_items:
            if self.current_table == self.employees_table:
                if self.match_employee(item, search_text):
                    filtered_items.append(item)
            else:
                if self.match_task(item, search_text):
                    filtered_items.append(item)

        self.current_items = filtered_items
        if self.current_table == self.employees_table:
            self.display_employees(filtered_items)
        else:
            self.display_tasks(filtered_items)

    def match_employee(self, emp, search_text):
        return any([
            search_text in emp.first_name.lower(),
            search_text in emp.last_name.lower(),
            search_text in emp.position.lower(),
            search_text in str(emp.salary).lower(),
            search_text in str(emp.hire_date).lower(),
            emp.fk_department and search_text in emp.fk_department.name.lower()
        ])

    def match_task(self, task, search_text):
        return any([
            search_text in task.name.lower(),
            search_text in task.description.lower(),
            search_text in task.status.lower(),
            task.fk_assignee and search_text in f"{task.fk_assignee.first_name} {task.fk_assignee.last_name}".lower()
        ])

    def add_item(self):
        try:
            session = get_session()
            if self.current_table == self.employees_table:
                dialog = EmployeeDialog(self)
                if dialog.exec():
                    new_employee = Employee(
                        first_name=dialog.first_name.text(),
                        last_name=dialog.last_name.text(),
                        position=dialog.position.text(),
                        salary=dialog.salary.value(),
                        hire_date=dialog.hire_date.date().toPython(),
                        department_id=dialog.department.currentData()
                    )
                    session.add(new_employee)
                    self.load_employees_data()
            else:
                dialog = TaskDialog(self)
                if dialog.exec():
                    new_task = Task(
                        name=dialog.name.text(),
                        description=dialog.description.text(),
                        status=dialog.status.currentText(),
                        assignee_id=dialog.assignee.currentData()
                    )
                    session.add(new_task)
                    self.load_tasks_data()
            session.commit()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")

    def edit_item(self):
        try:
            session = get_session()
            current_row = self.current_table.currentRow()
            if current_row >= 0:
                item = self.current_items[current_row]
                if self.current_table == self.employees_table:
                    dialog = EmployeeDialog(self, item)
                    if dialog.exec():
                        item.first_name = dialog.first_name.text()
                        item.last_name = dialog.last_name.text()
                        item.position = dialog.position.text()
                        item.salary = dialog.salary.value()
                        item.hire_date = dialog.hire_date.date().toPython()
                        item.department_id = dialog.department.currentData()
                        self.load_employees_data()
                else:
                    dialog = TaskDialog(self, item, edit_mode=True)
                    if dialog.exec():
                        item.status = dialog.status.currentText()
                        self.load_tasks_data()
                session.commit()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка при редактировании: {str(e)}")

app = QApplication([])
window = MainWindow()
window.show()
app.exec()