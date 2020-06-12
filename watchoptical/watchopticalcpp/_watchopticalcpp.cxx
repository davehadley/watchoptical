#include <pybind11/pybind11.h>

#include "TFile.h"

int add(int i, int j) {
    return i + j;
}

void open(std::string filename) { TFile(filename.c_str()).Print(); }

PYBIND11_MODULE(_watchopticalcpp, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring

    m.def("add", &add, "A function which adds two numbers");
    m.def("open", &open, "Open a ROOT file");
}