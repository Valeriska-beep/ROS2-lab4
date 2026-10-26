# Лабораторна робота №4: Розробка сенсорної ноди та публікація даних у систему

### 1. Створення пакету `sensor_node_pkg`

У каталозі `~/ros2_ws/src` створено новий пакет типу `ament_python` із залежностями від `rclpy` та `std_msgs`:

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws/src
ls
ros2 pkg create --build-type ament_python sensor_node_pkg --dependencies rclpy std_msgs

```

### 2. Налаштування точки входу (`setup.py`)

Відкриваємо setup.py у редакторі nano:

```bash
nano ~/ros2_ws/src/sensor_node_pkg/setup.py

```

У файлі `~/ros2_ws/src/sensor_node_pkg/setup.py` зареєстровано точку входу (entry point) для можливості виклику вузла через `ros2 run`:

```python
entry_points={
    'console_scripts': [
        'sensor_node = sensor_node_pkg.sensor_node:main',
    ],
},

```

### 3. Реалізація вузла сенсора (`sensor_node.py`)

У файлі `~/ros2_ws/src/sensor_node_pkg/sensor_node_pkg/sensor_node.py` реалізовано логіку роботи сенсора:

1. **Генерація даних:** симуляція вимірювань дистанції у діапазоні 0.2 \dots 1.2 м із додаванням шуму.
2. **Періодичність:** публікація з частотою 10 Гц (таймер з періодом 0.1 с).
3. **Фільтрація:** ковзне середнє за останніми 5 вимірюваннями.
4. **Контроль безпеки:** виведення попередження `WARN`, якщо середня дистанція < 0.40$ м.

Відкриваємо файл для створення коду ноди:

```bash
nano ~/ros2_ws/src/sensor_node_pkg/sensor_node_pkg/sensor_node.py
```

```py
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import random

class SensorNode(Node):
    def __init__(self):
        super().__init__('sensor_node')

        # Publisher у топік /sensor_data з типом std_msgs/msg/Float32
        self.sensor_publisher = self.create_publisher(Float32, '/sensor_data', 10)

        # Періодичність 10 Гц (0.1 секунди)
        self.timer_period = 0.1
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        # Буфер для ковзного середнього (5 останніх вимірювань)
        self.window_size = 5
        self.data_history = []

        # Порогове значення для попередження (дистанція в метрах)
        self.threshold = 0.4

        self.get_logger().info('Sensor Node started (10 Hz)')

    def timer_callback(self):
        # 1. Симуляція сенсора (випадкова відстань від 0.2 до 1.2 м)
        raw_distance = round(random.uniform(0.2, 1.2), 3)

        # 2. Оновлення вікна ковзного середнього
        self.data_history.append(raw_distance)
        if len(self.data_history) > self.window_size:
            self.data_history.pop(0)

        # 3. Обчислення усередненого значення
        filtered_distance = sum(self.data_history) / len(self.data_history)

        # 4. Публікація у топік
        msg = Float32()
        msg.data = float(filtered_distance)
        self.sensor_publisher.publish(msg)

        # 5. Інформаційний вивід (INFO)
        self.get_logger().info(
            f'Raw: {raw_distance:.2f} m | Filtered: {filtered_distance:.2f} m'
        )

        # 6. Перевірка порогу (WARN)
        if filtered_distance < self.threshold:
            self.get_logger().warn(
                f'Obstacle too close! Filtered: {filtered_distance:.2f} m (Threshold: {self.threshold:.2f} m)'
            )

def main(args=None):
    rclpy.init(args=args)
    node = SensorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

```


### 4. Збірка робочого простору

```bash
cd ~/ros2_ws
colcon build --packages-select sensor_node_pkg
source install/setup.bash
ros2 pkg list | grep sensor_node_pkg

```


### 5. Тестування та перевірка функціонування

#### Термінал 1: Запуск сенсорної ноди

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run sensor_node_pkg sensor_node

```

Вузол публікує вимірювання кожні 0.1 с та сигналізує про небезпечне наближення

#### Термінал 2: Моніторинг отримання повідомлень через топік

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
source ros2 topic list
ros2 topic echo /sensor_data

```

#### Термінал 3: Перевірка типу даних та частоти публікації

```bash
source /opt/ros/humble/setup.bash
ros2 topic info /sensor_data
ros2 topic hz /sensor_data

```

# Запуск програми:

Термінал 1: Запуск самої сенсорної ноди
Запущено вузол sensor_node. У логах видно необроблені дані (Raw), які симулюють шумний далекомір, та відфільтровані значення (Filtered), пораховані за алгоритмом ковзного середнього з вікном у 5 замірів. Коли середнє значення падає нижче 0.40 м, нода виводить жовте повідомлення [WARN] про критичне наближення до перешкоди».

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run sensor_node_pkg sensor_node
```

Термінал 2: Перевірка публікації та перегляд потоку даних

Командою ros2 topic list ми бачимо зареєстрований топік /sensor_data. За допомогою ros2 topic echo ми підписуємося на нього та переконуємося, що в систему передаються саме вже очищені відфільтровані числові значення».

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

# 1. Перевіряємо список активних топіків
ros2 topic list

# 2. Виводимо потік значень у реальному часі
ros2 topic echo /sensor_data
```

Термінал 3: Перевірка типу та стабільності частоти
Тут демонструються технічні характеристики шини передачі даних.
Команда ros2 topic info демонструє, що використовується стандартний числовий тип std_msgs/msg/Float32. А за допомогою ros2 topic hz ми бачимо, що нода стабільно публікує дані із частотою близько 10 Гц (середнє відхилення мінімальне, період складає приблизно 0.1 с)

```bash
source /opt/ros/humble/setup.bash

# 1. Перевірка типу повідомлень та кількості підписників/паблішерів
ros2 topic info /sensor_data

# 2. Перевірка частоти публікації
ros2 topic hz /sensor_data
```
