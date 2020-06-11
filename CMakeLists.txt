cmake_minimum_required(VERSION 3.4.0)

project(watchoptical)

find_package(PythonExtensions REQUIRED)

add_library(_watchopticalcpp MODULE watchoptical/watchopticalcpp/_hello.cxx)
python_extension_module(_watchopticalcpp)
install(TARGETS _watchopticalcpp LIBRARY DESTINATION watchoptical/watchopticalcpp)