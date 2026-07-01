import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import math

class ThrusterDriver(Node):
    def __init__(self):
        super().__init__('thruster_driver')
        
        # Publishers
        self.pub_fro = self.create_publisher(Float64, '/cascade/fro', 10)
        self.pub_flo = self.create_publisher(Float64, '/cascade/flo', 10)
        self.pub_bro = self.create_publisher(Float64, '/cascade/bro', 10)
        self.pub_blo = self.create_publisher(Float64, '/cascade/blo', 10)
        
        # TF Broadcaster for Foxglove 3D visualization
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # Subscribers
        self.odom_subscriber = self.create_subscription(
            Odometry,
            '/model/cascade/odometry_with_covariance',
            self.odom_callback,
            10
        )
        
        # PID
        self.target_yaw = math.radians(90.0)  # Target heading: 90 degrees left
        self.current_yaw = 0.0
        
        # PID Gains (May need tuning)
        self.Kp = 15.0
        self.Ki = 0.05
        self.Kd = 4.0
        
        # PID Vars
        self.prev_error = 0.0
        self.integral = 0.0
        self.max_torque = 30.0  # Capped the maximum thruster effort

        # Control Loop
        timer_period = 0.1  
        self.timer = self.create_timer(timer_period, self.control_loop)
        self.get_logger().info(f"Target Heading set to: {math.degrees(self.target_yaw)}°")

    def odom_callback(self, msg):
        # Extract quaternion from Gazebo odometry
        q = msg.pose.pose.orientation
        
        # Convert quaternion to Euler Yaw
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)

        # Broadcast AUV position using TF Tree
        t = TransformStamped()
        
        t.header.stamp = msg.header.stamp 
        t.header.frame_id = 'underwater_world'
        t.child_frame_id = 'cascade'
        
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z
        
        t.transform.rotation = q
        
        self.tf_broadcaster.sendTransform(t)

    def control_loop(self):
        raw_error = self.target_yaw - self.current_yaw
        
        error = math.atan2(math.sin(raw_error), math.cos(raw_error))
        
        self.integral += error * 0.1
        derivative = (error - self.prev_error) / 0.1
        
        self.integral = max(min(self.integral, 5.0), -5.0)
        
        u = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)
        u = max(min(u, self.max_torque), -self.max_torque)
        
        self.prev_error = error

        msg_fro = Float64(); msg_fro.data = u
        msg_flo = Float64(); msg_flo.data = u
        msg_bro = Float64(); msg_bro.data = -u
        msg_blo = Float64(); msg_blo.data = -u

        self.pub_fro.publish(msg_fro)
        self.pub_flo.publish(msg_flo)
        self.pub_bro.publish(msg_bro)
        self.pub_blo.publish(msg_blo)
        
        self.get_logger().info(
            f"Heading: {math.degrees(self.current_yaw):.1f}° | "
            f"Error: {math.degrees(error):.1f}° | "
            f"Effort: {u:.2f}"
        )

def main(args=None):
    rclpy.init(args=args)
    thruster_driver = ThrusterDriver()
    try:
        rclpy.spin(thruster_driver)
    except KeyboardInterrupt:
        pass
    finally:
        thruster_driver.destroy_node()
        # Suppress the RCLError when ros2 launch tears down the context
        try:
            if rclpy.ok():
                rclpy.shutdown()
        except Exception:
            pass

if __name__ == '__main__':
    main()