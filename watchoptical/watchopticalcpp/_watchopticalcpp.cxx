#include <iostream>

#include <pybind11/pybind11.h>
#include "RAT/DS/EV.hh"

#include "TFile.h"
#include "ROOT/RDataFrame.hxx"

int add(int i, int j) {
    return i + j;
}

void open(std::string filename) {
    ROOT::RDataFrame rdf("T", filename, {"ev"});
    rdf
    .Filter([](std::vector<RAT::DS::EV>& events){ return events.size() > 0; })
    .Range(0, 10)
    .Foreach(
        [](std::vector<RAT::DS::EV>& events){ std::cout << "EventID:" << events.at(0).GetID() << ", totalQ:" << events.at(0).GetTotalCharge() << std::endl; });
}

PYBIND11_MODULE(_watchopticalcpp, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring
    m.def("add", &add, "A function which adds two numbers");
    m.def("open", &open, "Open a ROOT file");
}