cmake_minimum_required(VERSION 3.4.0)

project(watchoptical)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_BUILD_TYPE Debug)

set(PYBIND11_CPP_STANDARD -std=c++14)
add_subdirectory(pybind11)
pybind11_add_module(_watchopticalcpp watchoptical/watchopticalcpp/_watchopticalcpp.cxx)


install(TARGETS _watchopticalcpp LIBRARY DESTINATION watchoptical/watchopticalcpp)
