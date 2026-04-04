import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QCheckBox, QPushButton, QLineEdit, QGridLayout, QWidget
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QPoint
import math


class BVHNode:
    def __init__(self, walls):
        self.aabb = self._compute_node_aabb(walls)
        self.walls = walls
        self.left = None
        self.right = None
        self.wall_normals = [self._compute_wall_normal(wall) for wall in walls]
        # Добавляем случайный цвет для визуализации
        self.color = QColor(
            random.randint(50, 200),
            random.randint(50, 200),
            random.randint(50, 200),
            80  # Полупрозрачный
        )

    def _compute_node_aabb(self, walls):
        """Приватный метод: вычисляет AABB только для этого узла"""
        min_x = min(min(wall[0][0], wall[1][0]) for wall in walls)
        max_x = max(max(wall[0][0], wall[1][0]) for wall in walls)
        min_y = min(min(wall[0][1], wall[1][1]) for wall in walls)
        max_y = max(max(wall[0][1], wall[1][1]) for wall in walls)
        return (min_x, min_y, max_x, max_y)

    def _compute_wall_normal(self, wall):
        """Приватный метод: вычисляет нормаль конкретной стены"""
        (x1, y1), (x2, y2) = wall
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        normal = (-dy/length, dx/length)
        # Корректировка направления нормали
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        if (mid_x * normal[0] + mid_y * normal[1]) < 0:
            normal = (-normal[0], -normal[1])
        return normal
   

class RayTracingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Трассировка лучей 2D")
        self.setGeometry(100, 100, 1600, 900)

        # Константы для стилей
        self.BACKGROUND_COLOR = QColor(30, 30, 30)
        self.PANEL_COLOR = QColor(90, 90, 90)
        self.RAY_COLOR = QColor(175,238,238)
        self.LIGHT_COLOR = QColor(29,51,74)
        self.WALL_COLOR = QColor(255, 255, 255)
        self.TEXT_COLOR = QColor(255, 255, 255)
        self.SECOND_BACKGROUND_COLOR = QColor(0, 0, 0, 210)

        # Переменные для хранения чисел
        self.user_ray_length = 300  # Длина луча
        self.user_angle = 2         # Угол между лучами
        self.max_reflections = 3    # Максимальное количество отражений
        self.alpha_decay = 0.3      # Потеря прозрачности после каждого отражения (30%)
        self.wall_count = 9         # Количество стен
        self.wall_length = 300      # Длина стен

        # Начальная позиция источника света
        self.light_pos = QPoint(self.width() // 2, self.height() // 2)

        # Стены
        self.walls = self.generate_walls(self.wall_count, self.wall_length)
        self.bvh_root = self.build_bvh(self.walls)

        # Инициализация UI
        self.init_ui()

        # Инициализация счетчиков
        self.intersection_checks = 0  # Счётчик проверок пересечений
        self.last_counter_update = 0  # Время последнего обновления счётчика

    def init_ui(self):
        """Инициализация пользовательского интерфейса."""
        # Создаем контейнер для элементов управления
        self.control_panel = QWidget(self)
        self.control_panel.setGeometry(5, 5, 186, 30)  # Начальный размер контейнера
        self.control_panel.setStyleSheet(f"background-color: {self.PANEL_COLOR.name()};")

        # Используем QGridLayout для размещения элементов
        self.layout = QGridLayout(self.control_panel)
        self.layout.setContentsMargins(5, 5, 5, 5)  # Отступы
        self.layout.setSpacing(5)  # Промежутки между элементами

        # Кнопка "Настройки"
        self.settings_button = QPushButton("Настройки")
        self.settings_button.clicked.connect(self.toggle_settings_panel)
        self.layout.addWidget(self.settings_button, 0, 0, 1, 2)  # Занимает две колонки

        # Панель настроек (скрыта по умолчанию)
        self.settings_panel = QWidget(self)
        self.settings_panel.setGeometry(5, 40, 186, 200)  # Позиция и размер панели
        self.settings_panel.setStyleSheet(f"background-color: {self.PANEL_COLOR.name()};")
        self.settings_panel.setVisible(False)  # Скрыта по умолчанию

        # Используем QGridLayout для панели настроек
        self.settings_layout = QGridLayout(self.settings_panel)
        self.settings_layout.setContentsMargins(5, 5, 5, 5)
        self.settings_layout.setSpacing(5)

        # Поле для ввода длины луча
        self.input_field_ray = QLineEdit()
        self.input_field_ray.setPlaceholderText("Луч (def 300)")
        self.settings_layout.addWidget(self.input_field_ray, 0, 0, 1, 1)
        #
        # Кнопка для сохранения длины луча
        self.button_ray = QPushButton("Ok")
        self.button_ray.setFixedWidth(30)
        self.button_ray.clicked.connect(lambda: self.save_number(self.input_field_ray, "ray"))
        self.settings_layout.addWidget(self.button_ray, 0, 1, 1, 1)

        # Поле для ввода угла
        self.input_field_angle = QLineEdit()
        self.input_field_angle.setPlaceholderText("Угол (def 2)")
        self.settings_layout.addWidget(self.input_field_angle, 1, 0, 1, 1)
        #
        # Кнопка для сохранения угла
        self.button_angle = QPushButton("Ok")
        self.button_angle.setFixedWidth(30)
        self.button_angle.clicked.connect(lambda: self.save_number(self.input_field_angle, "angle"))
        self.settings_layout.addWidget(self.button_angle, 1, 1, 1, 1)

        # Поле для ввода количества стен
        self.input_field_walls = QLineEdit()
        self.input_field_walls.setPlaceholderText("Стены (def 9)")
        self.settings_layout.addWidget(self.input_field_walls, 2, 0, 1, 1)
        #
        # Кнопка для сохранения количества стен
        self.button_walls = QPushButton("Ok")
        self.button_walls.setFixedWidth(30)
        self.button_walls.clicked.connect(lambda: self.save_number(self.input_field_walls, "walls"))
        self.settings_layout.addWidget(self.button_walls, 2, 1, 1, 1)

        # Поле для ввода длины стен
        self.input_field_wall_length = QLineEdit()
        self.input_field_wall_length.setPlaceholderText("Длина (def 300)")
        self.settings_layout.addWidget(self.input_field_wall_length, 3, 0, 1, 1)
        #
        # Кнопка для сохранения длины стен
        self.button_wall_length = QPushButton("Ok")
        self.button_wall_length.setFixedWidth(30)
        self.button_wall_length.clicked.connect(lambda: self.save_number(self.input_field_wall_length, "wall_length"))
        self.settings_layout.addWidget(self.button_wall_length, 3, 1, 1, 1)

        # Чекбокс для включения оптимизации BVH
        self.bvh_checkbox = QCheckBox("Оптимизация BVH")
        self.bvh_checkbox.setChecked(False)  # Выключено по умолчанию
        self.bvh_checkbox.stateChanged.connect(self.toggle_bvh_optimization)
        self.settings_layout.addWidget(self.bvh_checkbox, 4, 0, 1, 2)

        # Чекбокс для визуализации BVH (скрыт по умолчанию)
        self.optimization_checkbox = QCheckBox("BVH контур")
        self.optimization_checkbox.setVisible(False)  # Скрыт, пока не активирована оптимизация
        self.optimization_checkbox.stateChanged.connect(self.toggle_optimization_vizualization)
        self.settings_layout.addWidget(self.optimization_checkbox, 5, 0, 1, 2)

        # Чекбокс для режима зеркал
        self.mirror_checkbox = QCheckBox("Режим зеркал")
        self.mirror_checkbox.stateChanged.connect(self.toggle_mirror_mode)
        self.settings_layout.addWidget(self.mirror_checkbox, 6, 0, 1, 2)

        # Поле для ввода максимального количества отражений (скрыто по умолчанию)
        self.input_field_reflections = QLineEdit()
        self.input_field_reflections.setPlaceholderText("Отражения (def 3)")
        self.input_field_reflections.setVisible(False)
        self.settings_layout.addWidget(self.input_field_reflections, 7, 0, 1, 1)
        #
        # Кнопка для сохранения количества отражений
        self.button_reflections = QPushButton("Ok")
        self.button_reflections.setFixedWidth(30)
        self.button_reflections.clicked.connect(lambda: self.save_number(self.input_field_reflections, "reflections"))
        self.button_reflections.setVisible(False)
        self.settings_layout.addWidget(self.button_reflections, 7, 1, 1, 1)

        # Поле для ввода прозрачности (скрыто по умолчанию)
        self.input_field_alpha = QLineEdit()
        self.input_field_alpha.setPlaceholderText("Прозрачн. (def 30%)")
        self.input_field_alpha.setVisible(False)
        self.settings_layout.addWidget(self.input_field_alpha, 8, 0, 1, 1)
        #
        # Кнопка для сохранения прозрачности
        self.button_alpha = QPushButton("Ok")
        self.button_alpha.setFixedWidth(30)
        self.button_alpha.clicked.connect(lambda: self.save_number(self.input_field_alpha, "alpha"))
        self.button_alpha.setVisible(False)
        self.settings_layout.addWidget(self.button_alpha, 8, 1, 1, 1)

        # Чекбокс для отображения счётчика проверок
        self.counter_checkbox = QCheckBox("Показать счётчик проверок")
        self.counter_checkbox.stateChanged.connect(self.toggle_counter)
        self.settings_layout.addWidget(self.counter_checkbox, 9, 0, 1, 2)

    def toggle_settings_panel(self):
        """Переключение видимости панели настроек."""
        self.settings_panel.setVisible(not self.settings_panel.isVisible())

    def toggle_bvh_optimization(self):
        """Переключение оптимизации BVH и управление видимостью чекбокса визуализации"""
        if self.bvh_checkbox.isChecked():
            self.optimization_checkbox.setVisible(True)
        else:
            self.optimization_checkbox.setChecked(False)
            self.optimization_checkbox.setVisible(False)
        self.update()
        self.adjust_settings_panel_size()

    def adjust_settings_panel_size(self):
        """Автоматически подстраивает размер панели настроек"""
        self.settings_panel.adjustSize()
        self.settings_panel.setGeometry(
            5, 40,
            self.settings_panel.width(),
            self.settings_panel.height()
        )

    def toggle_counter(self):
        """Переключение отображения счётчика"""
        self.update()

    def toggle_optimization_vizualization(self):
        """Визуальное отображение BVH"""
        self.update()

    def toggle_mirror_mode(self):
        """Переключение режима зеркал и отображение/скрытие дополнительных полей."""
        if self.mirror_checkbox.isChecked():
            self.input_field_reflections.setVisible(True)
            self.button_reflections.setVisible(True)
            self.input_field_alpha.setVisible(True)
            self.button_alpha.setVisible(True)
        else:
            self.input_field_reflections.setVisible(False)
            self.button_reflections.setVisible(False)
            self.input_field_alpha.setVisible(False)
            self.button_alpha.setVisible(False)
        
        # Автоматически изменяем размер панели
        self.settings_panel.adjustSize()
        
        # Обновляем геометрию панели, чтобы она не перекрывала другие элементы
        self.settings_panel.setGeometry(
        5,  # X-координата
        40,  # Y-координата (ниже кнопки "Настройки")
        self.settings_panel.width(),  # Ширина
        self.settings_panel.height()  # Высота
        )

    def save_number(self, input_field, field_type):
        """Сохранение числа из поля ввода."""
        text = input_field.text()
        try:
            number = float(text)
            if field_type == "ray":
                self.user_ray_length = int(number)
            elif field_type == "angle":
                self.user_angle = int(number)
            elif field_type == "reflections":
                self.max_reflections = int(number)
            elif field_type == "alpha":
                self.alpha_decay = number / 100  # Преобразуем проценты в дробь
            elif field_type == "walls":
                self.wall_count = int(number)
                self.walls = self.generate_walls(self.wall_count, self.wall_length)
            elif field_type == "wall_length":
                self.wall_length = int(number)
                self.walls = self.generate_walls(self.wall_count, self.wall_length)
            self.bvh_root = self.build_bvh(self.walls)
            self.update()  # Обновляем экран
        except ValueError:
            return

    def generate_walls(self, count, length):
        """Генерация случайных стен с корректировкой положения внутри окна."""
        walls = []
        for _ in range(count):
            # Генерируем первую точку (может быть и у самого края)
            x1 = random.randint(0, self.width())
            y1 = random.randint(0, self.height())
            
            # Генерируем случайный угол
            angle = random.uniform(0, 2 * math.pi)
            
            # Вычисляем вторую точку
            x2 = x1 + length * math.cos(angle)
            y2 = y1 + length * math.sin(angle)
            
            # Корректируем обе точки, чтобы вся стена была внутри окна
            (x1, y1), (x2, y2) = self.adjust_wall_to_window(x1, y1, x2, y2)
            
            walls.append(((x1, y1), (x2, y2)))
            
        return walls

    def adjust_wall_to_window(self, x1, y1, x2, y2):
        """Сдвигает всю стену внутрь окна."""
        # Границы окна с небольшим отступом
        margin = 1
        x_min, y_min = margin, margin
        x_max, y_max = self.width() - margin, self.height() - margin
        
        # Вычисляем вектор стены
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        
        # Если стена уже внутри окна - возвращаем как есть
        if (x_min <= x1 <= x_max and x_min <= x2 <= x_max and
            y_min <= y1 <= y_max and y_min <= y2 <= y_max):
            return (x1, y1), (x2, y2)
        
        # Находим минимальный сдвиг для всей стены
        shift_x = 0
        shift_y = 0
        
        # Проверяем выход за левую границу
        if x1 < x_min or x2 < x_min:
            needed_shift = max(x_min - min(x1, x2), 0)
            shift_x = needed_shift
        
        # Проверяем выход за правую границу
        if x1 > x_max or x2 > x_max:
            needed_shift = min(x_max - max(x1, x2), 0)
            shift_x = needed_shift
        
        # Проверяем выход за верхнюю границу
        if y1 < y_min or y2 < y_min:
            needed_shift = max(y_min - min(y1, y2), 0)
            shift_y = needed_shift
        
        # Проверяем выход за нижнюю границу
        if y1 > y_max or y2 > y_max:
            needed_shift = min(y_max - max(y1, y2), 0)
            shift_y = needed_shift
        
        # Применяем сдвиг к обеим точкам
        x1 += shift_x
        y1 += shift_y
        x2 += shift_x
        y2 += shift_y
        
        # Гарантируем, что точки точно внутри окна
        x1 = max(x_min, min(x1, x_max))
        y1 = max(y_min, min(y1, y_max))
        x2 = max(x_min, min(x2, x_max))
        y2 = max(y_min, min(y2, y_max))
        
        return (x1, y1), (x2, y2)
    
    def build_bvh(self, walls, depth=0, max_depth=20):
        """Рекурсивно строит BVH-дерево с автоматическим определением осей разделения."""
        
        # Базовый случай - создаём лист
        if len(walls) <= 4 or depth >= max_depth:
            return BVHNode(walls)
        
        # 1. Вычисляем общий AABB для всех стен
        all_min_x = min(min(wall[0][0], wall[1][0]) for wall in walls)
        all_max_x = max(max(wall[0][0], wall[1][0]) for wall in walls)
        all_min_y = min(min(wall[0][1], wall[1][1]) for wall in walls)
        all_max_y = max(max(wall[0][1], wall[1][1]) for wall in walls)
        
        # 2. Определяем лучшую ось для разделения (x или y)
        dx = all_max_x - all_min_x
        dy = all_max_y - all_min_y
        axis = 0 if dx > dy else 1  # 0 - ось X, 1 - ось Y
        
        # 3. Сортируем стены по средней точке на выбранной оси
        walls_sorted = sorted(walls, key=lambda wall: (
            (wall[0][axis] + wall[1][axis]) / 2  # Средняя точка стены
        ))
        
        # 4. Разделяем стены примерно пополам
        mid = len(walls_sorted) // 2
        left_walls = walls_sorted[:mid]
        right_walls = walls_sorted[mid:]
        
        # 5. Рекурсивно строим левое и правое поддеревья
        node = BVHNode(walls)  # Создаём узел (но пока без детей)
        node.left = self.build_bvh(left_walls, depth+1, max_depth)
        node.right = self.build_bvh(right_walls, depth+1, max_depth)
        
        return node

    def aabb_area(self, aabb):
        """Вычисляем площадь AABB для SAH"""
        min_x, min_y, max_x, max_y = aabb
        return (max_x - min_x) * (max_y - min_y)

    def draw_bvh(self, node, painter):
        if node is None:
            return
        
        min_x, min_y, max_x, max_y = map(int, node.aabb)
        
        pen = QPen(node.color)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(min_x, min_y, max_x - min_x, max_y - min_y)

        # Рекурсивно рисуем левую и правую ветви
        self.draw_bvh(node.left, painter)
        self.draw_bvh(node.right, painter)

    def intersect_bvh(self, node, ray_start, ray_end):
        """Рекурсивный поиск пересечений в BVH"""
        if node is None:
            return None, float('inf')

        if not self.aabb_intersects_ray(node.aabb, ray_start, ray_end):
            return None, float('inf')
        
        if node.left is None and node.right is None:
            closest_intersection = None
            min_distance = float('inf')

            for wall in node.walls:
                intersection = self.get_intersection(ray_start, ray_end, wall[0], wall[1])
                if intersection:
                    dist = math.hypot(intersection[0] - ray_start[0], intersection[1] - ray_start[1])
                    if dist < min_distance:
                        min_distance = dist
                        closest_intersection = intersection
            return closest_intersection, min_distance
        left_intersection, left_dist = self.intersect_bvh(node.left, ray_start, ray_end)
        right_intersection, right_dist = self.intersect_bvh(node.right, ray_start, ray_end)

        if left_dist < right_dist:
            return left_intersection, left_dist
        else:
            return right_intersection, right_dist

    def intersect_bvh_with_counting(self, node, ray_start, ray_end, return_wall=False):
        """Поиск с подсчётом и возвратом стены"""
        if node is None:
            return (None, float('inf'), None) if return_wall else (None, float('inf'))

        self.intersection_checks += 1
        
        if not self.aabb_intersects_ray(node.aabb, ray_start, ray_end):
            return (None, float('inf'), None) if return_wall else (None, float('inf'))
        
        if node.left is None and node.right is None:
            closest_intersection = None
            min_distance = float('inf')
            hit_wall = None

            for i, wall in enumerate(node.walls):
                self.intersection_checks += 1
                intersection = self.get_intersection(ray_start, ray_end, wall[0], wall[1])
                if intersection:
                    dist = math.hypot(intersection[0]-ray_start[0], intersection[1]-ray_start[1])
                    if dist < min_distance:
                        min_distance = dist
                        closest_intersection = intersection
                        hit_wall = wall

            if return_wall:
                return closest_intersection, min_distance, hit_wall
            return closest_intersection, min_distance
        
        left_result = self.intersect_bvh_with_counting(node.left, ray_start, ray_end, return_wall)
        right_result = self.intersect_bvh_with_counting(node.right, ray_start, ray_end, return_wall)

        if return_wall:
            left_intersection, left_dist, left_wall = left_result
            right_intersection, right_dist, right_wall = right_result
            if left_dist < right_dist:
                return left_intersection, left_dist, left_wall
            return right_intersection, right_dist, right_wall
        else:
            left_intersection, left_dist = left_result
            right_intersection, right_dist = right_result
            if left_dist < right_dist:
                return left_intersection, left_dist
            return right_intersection, right_dist

    def aabb_intersects_ray(self, aabb, ray_start, ray_end):
        """Проверяет, пересекает ли луч ограничивающий объем (AABB)"""
        min_x, min_y, max_x, max_y = aabb

        if (ray_start[0] < min_x and ray_end[0] < min_x) or (ray_start[0] > max_x and ray_end[0] > max_x):
            return False
        if (ray_start[1] < min_y and ray_end[1] < min_y) or (ray_start[1] > max_y and ray_end[1] > max_y):
            return False
        return True

    def find_wall_normal(self, intersection, walls):
        """Находит нормаль стены, с которой пересекся луч."""
        ix, iy = intersection
        for wall in walls:
            x1, y1 = wall[0]
            x2, y2 = wall[1]
            # Проверяем, лежит ли точка intersection на стене wall
            if self.point_on_segment((ix, iy), (x1, y1), (x2, y2)):
                wall_vec = (x2 - x1, y2 - y1)
                wall_length = math.hypot(wall_vec[0], wall_vec[1])
                if wall_length == 0:
                    continue
                normal = (-wall_vec[1]/wall_length, wall_vec[0]/wall_length)
                # Корректируем направление нормали
                to_wall = (ix - x1, iy - y1)
                if (to_wall[0] * normal[0] + to_wall[1] * normal[1]) < 0:
                    normal = (-normal[0], -normal[1])
                return normal
        return None

    def point_on_segment(self, p, a, b):
        """Проверяет, лежит ли точка p на отрезке ab."""
        px, py = p
        ax, ay = a
        bx, by = b
        cross = (px - ax) * (by - ay) - (py - ay) * (bx - ax)
        if abs(cross) > 1e-6:
            return False
        min_x = min(ax, bx)
        max_x = max(ax, bx)
        min_y = min(ay, by)
        max_y = max(ay, by)
        return (min_x <= px <= max_x) and (min_y <= py <= max_y)

    def paintEvent(self, event):
        """Отрисовка содержимого окна"""
        self.intersection_checks = 0

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Темный фон
        painter.fillRect(self.rect(), self.BACKGROUND_COLOR)

        # Отрисовка BVH только если включены и оптимизация, и визуализация
        if self.bvh_checkbox.isChecked() and self.optimization_checkbox.isChecked():
            self.draw_bvh(self.bvh_root, painter)

        # Отрисовка лучей
        for angle in range(0, 360, self.user_angle):
            radians = math.radians(angle)
            end_x = self.light_pos.x() + self.user_ray_length * math.cos(radians)
            end_y = self.light_pos.y() + self.user_ray_length * math.sin(radians)

            if self.mirror_checkbox.isChecked():
                # Режим зеркал - лучи отражаются
                start = (self.light_pos.x(), self.light_pos.y())
                direction = (math.cos(radians), math.sin(radians))
                reflections = self._reflect_ray(start, direction, self.walls)

                alpha = 1.0  # Начальная прозрачность
                for seg in reflections:
                    color = QColor(self.RAY_COLOR)
                    color.setAlphaF(alpha)  # Устанавливаем прозрачность
                    painter.setPen(color)
                    painter.drawLine(int(seg[0][0]), int(seg[0][1]), int(seg[1][0]), int(seg[1][1]))
                    alpha *= (1 - self.alpha_decay)  # Уменьшаем прозрачность
            else:
                # Режим зеркал выключен: проверяем столкновения с учётом оптимизации
                closest_intersection = None
                min_distance = float("inf")
                
                if self.bvh_checkbox.isChecked():
                    # Модифицируем intersect_bvh для подсчёта проверок
                    closest_intersection, _ = self.intersect_bvh_with_counting(
                        self.bvh_root,
                        (self.light_pos.x(), self.light_pos.y()),
                        (end_x, end_y)
                    )
                else:
                    for wall in self.walls:
                        self.intersection_checks += 1  # Увеличиваем счётчик
                        intersection = self.get_intersection(
                            (self.light_pos.x(), self.light_pos.y()),
                            (end_x, end_y),
                            wall[0], wall[1]
                        )
                        if intersection:
                            dist = ((intersection[0] - self.light_pos.x())**2 + 
                                (intersection[1] - self.light_pos.y())**2)**0.5
                            if dist < min_distance:
                                min_distance = dist
                                closest_intersection = intersection

                if closest_intersection:
                    painter.setPen(self.RAY_COLOR)
                    painter.drawLine(
                        self.light_pos.x(), self.light_pos.y(),
                        int(closest_intersection[0]), int(closest_intersection[1]))
                else:
                    painter.setPen(self.RAY_COLOR)
                    painter.drawLine(
                        self.light_pos.x(), self.light_pos.y(),
                        int(end_x), int(end_y))

        # Отрисовка стен
        painter.setPen(self.WALL_COLOR)
        for wall in self.walls:
            (x1, y1), (x2, y2) = wall
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Отрисовка точки, из которой исходит свет
        painter.setPen(self.LIGHT_COLOR)
        painter.setBrush(self.LIGHT_COLOR)
        painter.drawEllipse(self.light_pos, 4, 4)

        # Отрисовка счетчика с фоном
        if self.counter_checkbox.isChecked():
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            
            # Текст для отображения
            counter_text = f"Проверок пересечений: {self.intersection_checks}"
            
            text_rect = painter.fontMetrics().boundingRect(counter_text)
            padding = 5  # Отступ от краёв текста
            bg_rect = text_rect.adjusted(-padding, -padding, padding, padding)
            bg_rect.moveTo(5, self.height() - 33)  # Позиционируем
            
            # Рисуем полупрозрачный фон
            painter.setBrush(self.SECOND_BACKGROUND_COLOR)  # Чёрный с альфа=210
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(bg_rect)
            
            # Рисуем текст
            painter.setPen(self.TEXT_COLOR)  # Белый текст
            painter.drawText(10, self.height() - 15, counter_text)

        painter.end()

    def mouseMoveEvent(self, event):
        """Обновление позиции источника света при движении мыши."""
        self.light_pos = event.position().toPoint()
        self.update()

    def _reflect_ray(self, ray_start, ray_dir, walls):
        """Трассировка с подсчётом проверок"""
        reflections = []
        current_length = self.user_ray_length
        start = ray_start
        direction = (ray_dir[0], ray_dir[1])

        for _ in range(self.max_reflections):
            end_point = (start[0] + direction[0] * current_length,
                        start[1] + direction[1] * current_length)

            if self.bvh_checkbox.isChecked():
                result = self.intersect_bvh_with_counting(
                    self.bvh_root, start, end_point, return_wall=True)
                closest_intersection, min_distance, hit_wall = result
            else:
                closest_intersection = None
                min_distance = float('inf')
                hit_wall = None
                for wall in walls:
                    self.intersection_checks += 1
                    intersection = self.get_intersection(start, end_point, wall[0], wall[1])
                    if intersection:
                        dist = math.hypot(intersection[0]-start[0], intersection[1]-start[1])
                        if dist < min_distance:
                            min_distance = dist
                            closest_intersection = intersection
                            hit_wall = wall

            if closest_intersection is None:
                reflections.append((start, end_point))
                break

            reflections.append((start, closest_intersection))
            current_length -= min_distance

            # Используем предвычисленную нормаль
            wall_idx = self.bvh_root.walls.index(hit_wall) if hit_wall else None
            if wall_idx is not None:
                wall_normal = self.bvh_root.wall_normals[wall_idx]
            else:
                wall_normal = self.compute_wall_normal(hit_wall)

            # Отражаем направление
            dot = direction[0]*wall_normal[0] + direction[1]*wall_normal[1]
            direction = (
                direction[0] - 2 * dot * wall_normal[0],
                direction[1] - 2 * dot * wall_normal[1]
            )

            start = (
                closest_intersection[0] + direction[0] * 1e-3,
                closest_intersection[1] + direction[1] * 1e-3
            )

        return reflections

    def get_intersection(self, ray_start, ray_end, wall_start, wall_end):
        """Вычисление пересечения луча и стены."""
        x1, y1 = ray_start
        x2, y2 = ray_end
        x3, y3 = wall_start
        x4, y4 = wall_end

        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0:
            return None  # Луч и стена параллельны, пересечения нет

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator

        if 0 <= t <= 1 and 0 <= u <= 1:
            intersection_x = x1 + t * (x2 - x1)
            intersection_y = y1 + t * (y2 - y1)
            return intersection_x, intersection_y
        return None


if __name__ == "__main__": 
    app = QApplication(sys.argv)
    window = RayTracingApp()
    window.show()
    sys.exit(app.exec())
