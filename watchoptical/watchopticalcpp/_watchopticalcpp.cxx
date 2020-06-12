#include <iostream>

#include <pybind11/pybind11.h>
#include "RAT/DS/EV.hh"

#include "TFile.h"
#include "ROOT/RDataFrame.hxx"

int add(int i, int j) {
    return i + j;
}

void open(std::string filename) {
    TFile(filename.c_str()).Print();
    ROOT::RDataFrame rdf("T", filename);
    rdf.Range(0, 10).Foreach(
        [](RAT::DS::EV* event){ std::cout << event->GetID() << std::endl; },
        {"ds.ev"}
    );

}

PYBIND11_MODULE(_watchopticalcpp, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring
    m.def("add", &add, "A function which adds two numbers");
    m.def("open", &open, "Open a ROOT file");
}