cmake_minimum_required(VERSION 3.4.0)

project(watchoptical)

add_subdirectory(pybind11)
pybind11_add_module(_watchopticalcpp watchoptical/watchopticalcpp/_hello.cxx)


install(TARGETS _watchopticalcpp LIBRARY DESTINATION watchoptical/watchopticalcpp)
