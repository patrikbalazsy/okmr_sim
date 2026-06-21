FROM osrf/ros:jazzy-desktop

ENV DEBIAN_FRONTEND=noninteractive

USER root
# Install ROS 2, Gazebo integration, and Foxglove Bridge
RUN apt-get update && apt-get install -y \
    ros-jazzy-ros-gz \
    ros-jazzy-rosbridge-suite \
    ros-jazzy-foxglove-bridge \
    && rm -rf /var/lib/apt/lists/*

USER ubuntu
WORKDIR /home/ubuntu

# Source ROS 2 automatically
RUN echo "source /opt/ros/jazzy/setup.bash" >> /home/ubuntu/.bashrc

CMD ["sleep", "infinity"]