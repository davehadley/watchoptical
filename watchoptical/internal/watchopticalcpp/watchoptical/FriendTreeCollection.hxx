#ifndef WATCHOPTICAL_FRIENDTREECOLLECTION_HXX
#define WATCHOPTICAL_FRIENDTREECOLLECTION_HXX

class FriendTreeCollection {

public:
    explicit FriendTreeCollection(const std::map<std::string, std::string>& fileNameToTreeName) {
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

#endif