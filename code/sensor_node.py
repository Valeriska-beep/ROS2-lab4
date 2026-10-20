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
