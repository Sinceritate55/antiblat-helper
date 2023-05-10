import sys
from datetime import datetime, timedelta

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox, QTextBrowser, QDockWidget, \
    QFileDialog, QDesktopWidget, QComboBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.f1 = None
        self.setWindowTitle("AntiBlat Helper")
        self.program_size()
        self.text_browser = QTextBrowser()
        self.font_size = 11
        font = QFont("Verdana", self.font_size)
        self.text_browser.setFont(font)
        self.setCentralWidget(self.text_browser)
        self.checkboxes = []
        self.text = self.load_file()
        self.text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.create_checkboxes()
        self.sort_text()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor("#212529")
        painter.fillRect(self.rect(), QBrush(color))
        # Остальной код рисования
        painter.drawRect(self.rect())
        rect = self.rect()
        rect.setWidth(rect.width() // 2)  # Половина ширины виджета
        rect.setHeight(rect.height() // 2)  # Половина высоты виджета

        # Задаем цвет для перекраски
        fill_color = QColor("#212529")

        # Перекрашиваем выбранную область фона
        painter.fillRect(rect, QBrush(fill_color))

    def program_size(self):

        screen = QDesktopWidget().screenGeometry()
        source_width = 1920
        source_height = 1080

        source_optimal_width = 1300
        source_optimal_height = 650

        target_width = screen.width()
        target_height = screen.height()

        target_optimal_width = int(source_optimal_width * (target_width / source_width))
        target_optimal_height = int(source_optimal_height * (target_height / source_height))
        self.resize(target_optimal_width, target_optimal_height)

    def create_checkboxes(self):
        layout = QVBoxLayout()
        filters = ["Принял игрока", "Уволил игрока", "Изменил ранг", "Установил игроку", "Снял со счета организации",
                   'выдал премию на сумму', 'изменил во фракции']
        checkbox_names = ['Принятия во фракцию', 'Увольнения из фракции', 'Изменения ранга', 'Установка тега',
                          'Снятие со счета организации', 'Премия', 'Изменения названия ранга']
        for i, (category, name) in enumerate(zip(filters, checkbox_names)):
            checkbox = QCheckBox(category)
            checkbox.setText(name)
            checkbox.setProperty("filter", category)
            checkbox.setStyleSheet("QCheckBox { color: white; }")
            font = QFont("Ariel")
            checkbox.setFont(font)
            checkbox.stateChanged.connect(self.sort_text)
            layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        # Добавление QComboBox
        self.time_filter = QComboBox()
        self.time_filter.addItems(["Неделя", "2 недели", "Месяц", "Все время"])
        self.time_filter.currentTextChanged.connect(self.sort_text)
        layout.addWidget(self.time_filter)

        container = QWidget()
        container.setLayout(layout)
        container.setMaximumHeight(200)
        dock_widget = QDockWidget("Фильтры")
        dock_widget.setStyleSheet("background: #212529; color: white;")
        dock_widget.setWidget(container)
        dock_widget.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.addDockWidget(1, dock_widget)

    def load_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select File", "", "Text Files (*.txt)")

        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()

    def sort_text(self):
        selected_filters = [checkbox.property("filter") for checkbox in self.checkboxes if checkbox.isChecked()]
        selected_time_filter = self.time_filter.currentText()
        rows = []

        time_filters = {
            "Неделя": timedelta(weeks=1, days=3),
            "2 недели": timedelta(weeks=2),
            "Месяц": timedelta(days=30),
            "Все время": None
        }

        selected_filter = time_filters.get(selected_time_filter)

        for line in self.text.split("\n"):
            for filter in selected_filters:
                if filter.lower() in line.lower():
                    parts = line.strip().split(" ", 2)  # Разделение строки на 3 части: Дата, Время, Действие
                    if len(parts) == 3:
                        date = datetime.strptime(parts[0] + " " + parts[1], "%Y-%m-%d %H:%M:%S")
                        if selected_filter is None or date >= (datetime.now() - selected_filter):
                            action = parts[2]
                            rows.append((date, action))

        if rows:
            html = """
            <html>
                <head>
                    <style>
                        table {
                            width: 100%;
                            border-collapse: collapse;
                        }
                        th, td {
                            padding: 10px;
                            border: 1px solid #ccc;
                        }
                        th {
                            background-color: #f2f2f2;
                        }
                        td:first-child {
                            width: 20%;
                        }
                        td:last-child {
                            width: 30%;
                        }
                        a {
                            text-decoration: none;
                            color: #007bff;
                        }
                        strong {
                            font-weight: bold;
                        }
                        code {
                            font-family: Consolas, monospace;
                            background-color: #f8f9fa;
                            padding: 2px 4px;
                        }
                    </style>
                </head>
                <body>
                    <table>
                        <tr>
                            <th>Дата</th>
                            <th>Действие</th>
                        </tr>
            """

            for row in rows:
                html += f"""
                <tr>
                    <td>
                        <code>{row[0]}</code>
                    </td>
                    <td>
                        {row[1]}
                    </td>
                </tr>
                """

            html += """
                    </table>
                </body>
            </html>
            """
            self.text_browser.setHtml(html)
        else:
            html = """
                <html>
                    <head>
                        <style>
                            .empty-message {
                                padding: 10px;
                                text-align: center;
                                font-weight: bold;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="empty-message">
                            Выберите фильтр/Не найдено действий
                        </div>
                    </body>
                </html>
                """
            self.text_browser.setHtml(html)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
