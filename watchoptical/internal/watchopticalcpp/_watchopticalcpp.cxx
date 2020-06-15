#include <iostream>

#include <pybind11/pybind11.h>
#include "RAT/DS/EV.hh"


#include "TFile.h"
#include "ROOT/RDataFrame.hxx"


class TFileTreeCollection {

public:
    explicit TFileTreeCollection(const std::map<std::string, std::string>& fileNameToTreeName) {
        if(fileNameToTreeName.size()==0) { throw std::runtime_error("no files/trees provided."); }
        for(auto& p: fileNameToTreeName) {
            auto tfile = TFile::Open(p.first.c_str());
            rawfile.emplace_back(tfile);
            if(tfile->IsOpen()) {
                auto tree = tfile->Get<TTree>(p.second.c_str());
                if(!tree) {
                    throw std::runtime_error("file " + p.first + " has no tree" + p.second);
                }
                rawtree.emplace_back(tree);
            }
        }
        for(int index = 0; index < rawtree.size(); ++index) {
            rawtree.at(0)->AddFriend(rawtree.at(index));
        }
    }

    TTree& tree() { return *rawtree.at(0); }
private:
    std::vector<std::unique_ptr<TFile>> rawfile;
    std::vector<TTree*> rawtree;
};

int add(int i, int j) {
    return i + j;
}

void open(std::string filename) {
    ROOT::RDataFrame rdf("T", filename, {"ev"});
    rdf
    .Filter([](std::vector<RAT::DS::EV>& events){ return events.size() > 0; })
    .Foreach(
        [](std::vector<RAT::DS::EV>& events){ std::cout << "EventID:" << events.at(0).GetID() << ", totalQ:" << events.at(0).GetTotalCharge() << std::endl; });
}

void convert_ratpacbonsai_to_analysis(std::string ratpac, std::string bonsai, std::string analysisfile) {
    TFileTreeCollection dataset({{ratpac,"T"}, {bonsai,"data"}});
    ROOT::RDataFrame rdf(dataset.tree());
    auto pipeline = rdf
    .Define("total_charge", [](const std::vector<RAT::DS::EV>& ev){
        std::vector<double> result;
        std::transform(ev.begin(), ev.end(), std::back_inserter(result),
                [](const RAT::DS::EV& e) {
            return e.GetTotalCharge();
        });
        return result;
        }, {"ev"});
    pipeline.Snapshot("watchopticalanalysis", analysisfile, {"total_charge"});
    return;
}

PYBIND11_MODULE(_watchopticalcpp, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring
    m.def("add", &add, "A function which adds two numbers");
    m.def("open", &open, "Open a ROOT file");
    m.def("convert_ratpacbonsai_to_analysis", &convert_ratpacbonsai_to_analysis, "Convert a RATPAC and BONSAI pair into the watchoptical analysis file format.");
}