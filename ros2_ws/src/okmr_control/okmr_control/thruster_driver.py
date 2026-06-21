import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry  # NEW: Import Odometry
import math                        # NEW: Import math for quaternion conversion

class ThrusterDriver(Node):
    def __init__(self):
        super().__init__('thruster_driver')
        
        # --- PUBLISHERS (Outputs) ---
        self.pub_fro = self.create_publisher(Float64, '/cascade/fro', 10)
        self.pub_flo = self.create_publisher(Float64, '/cascade/flo', 10)
        self.pub_bro = self.create_publisher(Float64, '/cascade/bro', 10)
        self.pub_blo = self.create_publisher(Float64, '/cascade/blo', 10)
        
        # --- SUBSCRIBERS (Inputs) ---
        self.odom_subscriber = self.create_subscription(
            Odometry,
            '/model/cascade/odometry_with_covariance',
            self.odom_callback,
            10
        )
        
        # Store current heading in radians
        self.current_yaw = 0.0

        # --- CONTROL LOOP ---
        timer_period = 0.1  
        self.timer = self.create_timer(timer_period, self.control_loop)

    def odom_callback(self, msg):
        # Extract the orientation quaternion from the odometry message
        q = msg.pose.pose.orientation
        
        # Convert the quaternion to Yaw (rotation around the Z-axis)
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)
        
        # Log the output in degrees so it is easy to read in the terminal
        self.get_logger().info(f'Current Yaw: {math.degrees(self.current_yaw):.1f}°')

    def control_loop(self):
        # PID math will go here. 
        # For now, we still push static values to keep the AUV moving.
        msg_fro = Float64(); msg_fro.data = 10.0
        msg_flo = Float64(); msg_flo.data = 10.0
        msg_bro = Float64(); msg_bro.data = -10.0
        msg_blo = Float64(); msg_blo.data = -10.0

        self.pub_fro.publish(msg_fro)
        self.pub_flo.publish(msg_flo)
        self.pub_bro.publish(msg_bro)
        self.pub_blo.publish(msg_blo)

def main(args=None):
    rclpy.init(args=args)
    thruster_driver = ThrusterDriver()
    
    try:
        rclpy.spin(thruster_driver)
    except KeyboardInterrupt:
        pass
    finally:
        thruster_driver.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()