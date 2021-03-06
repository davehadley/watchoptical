cmake_minimum_required(VERSION 3.13.0)

project(watchopticalcpp)

set(CMAKE_CXX_STANDARD 17)

# For easier debugging
set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_VERBOSE_MAKEFILE ON)

# ROOT
list(APPEND CMAKE_PREFIX_PATH $ENV{ROOTSYS})
find_package(ROOT 6.18 REQUIRED COMPONENTS RIO Tree ROOTVecOps ROOTDataFrame MathCore)
#include_directories(${VDT_INCLUDE_DIRS})
include(${ROOT_USE_FILE})

# RAT
if(NOT DEFINED ENV{RATROOT})
    message(FATAL_ERROR "RATROOT environment variable is not set.")
endif()
set(RATROOT $ENV{RATROOT})

# pybind11
set(PYBIND11_CPP_STANDARD -std=c++11)
find_package(pybind11 REQUIRED)
pybind11_add_module(_watchopticalcpp watchopticalcpp/_watchopticalcpp.cxx)
target_link_libraries(_watchopticalcpp PRIVATE ${ROOT_LIBRARIES})
target_link_libraries(_watchopticalcpp PRIVATE ${RATROOT}/lib/libRATEvent.so)
target_include_directories(_watchopticalcpp PRIVATE ${RATROOT}/include)
target_link_options(_watchopticalcpp PRIVATE -Wl,--no-as-needed)

install(TARGETS _watchopticalcpp LIBRARY DESTINATION watchopticalcpp)
