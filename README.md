# Eurobot 2027 - Software de Simulación

Ejecutar comandos en eurobot_ws, dos carpetas anteriores. Necesario hacer los pasos de [eurobot_software](https://github.com/star-uma/eurobot_software.git).

## Instalación gazebo ignition

1. Herramientas necesarias.

```bash
sudo apt-get update
sudo apt-get install lsb-release gnupg
```

2. Instalar Gazebo Ignition Fortress
```bash
sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] https://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
sudo apt-get update
sudo apt-get install ignition-fortress
```
## Instalación de dependencias 

```bash
sudo rosdep init
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```
## Compilación del paquete simulación
```bash
colcon build --packages-select eurobot_software_simulacion --symlink-install
```
## Referencia a los archivos
```bash
source install/setup.bash
```

## Lanzamiento gazebo (terminal 1)
```bash
ros2 launch eurobot_software_simulacion sim.launch.py
```
## Control teleop (terminal 2)
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
