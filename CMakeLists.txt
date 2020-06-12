cmake_minimum_required(VERSION 3.4.0)

project(watchoptical)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_BUILD_TYPE Debug)

# ROOT
list(APPEND CMAKE_PREFIX_PATH $ENV{ROOTSYS})
find_package(ROOT 6.18 REQUIRED COMPONENTS RIO Tree ROOTVecOps ROOTDataFrame MathCore)
#include_directories(${VDT_INCLUDE_DIRS})
include(${ROOT_USE_FILE})

# pybind11
set(PYBIND11_CPP_STANDARD -std=c++14)
add_subdirectory(pybind11)
pybind11_add_module(_watchopticalcpp watchoptical/watchopticalcpp/_watchopticalcpp.cxx)
target_link_libraries(_watchopticalcpp PRIVATE ${ROOT_LIBRARIES})

install(TARGETS _watchopticalcpp LIBRARY DESTINATION watchoptical/watchopticalcpp)
