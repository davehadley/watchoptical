//
// Created by dave on 17/06/2020.
//

#ifndef WATCHOPTICAL_ITEREVENTS_HXX
#define WATCHOPTICAL_ITEREVENTS_HXX

#include "TFile.h"
#include "TTreeReader.h"

namespace watchoptical {
    class IterEvents {
    public:
        IterEvents(std::string g4file, std::string bonsaifile) :
                g4file(TFile::Open(g4file.c_str())),
                bonsaifile(TFile::Open(bonsaifile.c_str())),
                g4reader("T", this->g4file.get()),
                bonsaireader("data", this->bonsaifile.get()),
                eventindex(-1),
                ratevents(g4reader, "ev"),
                bonsai_n9(bonsaireader, "n9")
                {
        }

        bool next() {
            bool result = true;
            if(eventindex < 0) {
                result = g4reader.Next();
                if(!result) { return false; }
            }
            eventindex += 1;
            if(eventindex < ratevents->size()) {
                bonsaireader.Next();
            } else {
                eventindex = -1;
            }
            return result;
        }

    private:
        std::unique_ptr<TFile> g4file;
        std::unique_ptr<TFile> bonsaifile;
        TTreeReader g4reader;
        TTreeReader bonsaireader;
        int eventindex;
        TTreeReaderValue<std::vector<RAT::DS::EV>> ratevents;
    public:
        RAT::DS::EV* ratevent() { return ratevents->size()<eventindex ? &ratevents->at(eventindex):0; }
        TTreeReaderValue<double> bonsai_n9;
    };
}

#endif //WATCHOPTICAL_ITEREVENTS_HXX
