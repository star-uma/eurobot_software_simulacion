cmake_minimum_required(VERSION 3.8)
project(eurobot_software_simulacion)

# Comprueba que el compilador sea compatible
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Busca el motor de CMAKE
find_package(ament_cmake REQUIRED)

# Instrucción para copiar las carpetas al compilar dede /src/ a install/share/
install(
  DIRECTORY description launch config worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
