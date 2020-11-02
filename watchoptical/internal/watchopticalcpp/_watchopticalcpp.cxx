#include <iostream>

#include <pybind11/pybind11.h>
#include "RAT/DS/EV.hh"
#include "RAT/DS/MC.hh"
#include "RAT/DS/PMTInfo.hh"


#include "TFile.h"
#include "ROOT/RDataFrame.hxx"

#include "watchoptical/FriendTreeCollection.hxx"


void open(std::string filename) {
    ROOT::RDataFrame rdf("T", filename, {"ev"});
    rdf
    .Filter([](std::vector<RAT::DS::EV>& events){ return events.size() > 0; })
    .Foreach(
        [](std::vector<RAT::DS::EV>& events){ std::cout << "EventID:" << events.at(0).GetID() << ", totalQ:" << events.at(0).GetTotalCharge() << std::endl; });
}

std::vector<double> gettotalcharge(const std::vector<RAT::DS::EV>& ev) {
    std::vector<double> result;
    std::transform(ev.begin(), ev.end(), std::back_inserter(result),
                   [](const RAT::DS::EV& e) {
                       return e.GetTotalCharge();
                   });
    return result;
}

std::vector<double> getpmt_time(std::vector<RAT::DS::EV>& ev) {
    std::vector<double> result;
    for(auto& e : ev) {
        for(int i = 0; i < e.GetPMTCount(); ++i) {
            auto pmt = e.GetPMT(i);
            result.push_back(pmt->GetTime());
        }
    }
    return result;
}

std::vector<double> getpmt_x(std::vector<RAT::DS::EV>& ev, RAT::DS::PMTInfo& pmtinfo) {
    std::vector<double> result;
    for(auto& e : ev) {
        for(int i = 0; i < e.GetPMTCount(); ++i) {
            auto pmt = e.GetPMT(i);
            auto x = pmtinfo.GetPosition(pmt->GetID()).X();
            result.push_back(x);
        }
    }
    return result;
}

std::vector<double> getpmt_charge(std::vector<RAT::DS::EV>& ev) {
    std::vector<double> result;
    for(auto& e : ev) {
        for(int i = 0; i < e.GetPMTCount(); ++i) {
            auto pmt = e.GetPMT(i);
            result.push_back(pmt->GetCharge());
        }
    }
    return result;
}

std::vector<double> getpmt_id(std::vector<RAT::DS::EV>& ev) {
    std::vector<double> result;
    for(auto& e : ev) {
        for(int i = 0; i < e.GetPMTCount(); ++i) {
            auto pmt = e.GetPMT(i);
            result.push_back(pmt->GetID());
        }
    }
    return result;
}

std::vector<double> getpmt_eventid(std::vector<RAT::DS::EV>& ev) {
    std::vector<double> result;
    for(auto& e : ev) {
        for(int i = 0; i < e.GetPMTCount(); ++i) {
            result.push_back(e.GetID());
        }
    }
    return result;
}

std::vector<double> getmc_t(std::vector<RAT::DS::MC>& ev) {
    std::vector<double> result;
    return result;
}

RAT::DS::PMTInfo load_pmt_info(std::string ratpacfilename) {
    TFile file(ratpacfilename.c_str());
    TTreeReader reader("runT", &file);
    TTreeReaderValue<std::vector<RAT::DS::PMTInfo>> branch(reader, "pmtinfo");
    while(reader.Next()) {
        return branch->at(0);
    }
    throw std::runtime_error("failed to load PMT INFO from " + ratpacfilename);
}

void convert_ratpacbonsai_to_analysis(std::string ratpac, std::string bonsai, std::string analysisfile) {
    auto pmtinfo = load_pmt_info(ratpac);
    watchoptical::FriendTreeCollection dataset({{ratpac, "T"}});
    ROOT::RDataFrame rdf(dataset.tree(), {"ev"});
    auto pipeline = rdf
    .Define("total_charge", ::gettotalcharge)
    .Define("pmt_t", ::getpmt_time)
    .Define("pmt_x", [&](std::vector<RAT::DS::EV>& ev) { return getpmt_x(ev, pmtinfo); })
    .Define("pmt_q", ::getpmt_charge)
    .Define("pmt_id", ::getpmt_id)
    .Define("pmt_eventid", ::getpmt_eventid)
    .Define("mc_t", ::getmc_t, {"mc"})
    ;
    pipeline.Snapshot("watchopticalanalysis", analysisfile, {
        "total_charge", 
        "pmt_t", 
        "pmt_x", 
        "pmt_q", 
        "pmt_id", 
        "pmt_eventid"
    });
    return;
}

PYBIND11_MODULE(_watchopticalcpp, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring
    m.def("open", &open, "Open a ROOT file");
    m.def("convert_ratpacbonsai_to_analysis", &convert_ratpacbonsai_to_analysis, "Convert a RATPAC and BONSAI pair into the watchoptical analysis file format.");
}