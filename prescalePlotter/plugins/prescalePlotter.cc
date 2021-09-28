// -*- C++ -*-
//
// Package:    PPSTools/prescalePlotter
// Class:      prescalePlotter
//
/**\class prescalePlotter prescalePlotter.cc PPSTools/prescalePlotter/plugins/prescalePlotter.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Andrea Bellora
//         Created:  Tue, 21 Sep 2021 10:28:45 GMT
//
//

// system include files
#include <memory>
#include <string>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "HLTrigger/HLTcore/interface/HLTPrescaleProvider.h"
//
// class declaration
//

// If the analyzer does not use TFileService, please remove
// the template argument to the base class so the class inherits
// from  edm::one::EDAnalyzer<>
// This will improve performance in multithreaded jobs.

class prescalePlotter : public edm::stream::EDAnalyzer<> {
public:
  explicit prescalePlotter(const edm::ParameterSet&);
  ~prescalePlotter() override;

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void endRun(edm::Run const&, edm::EventSetup const&) override;
  void beginRun(edm::Run const& iRun, edm::EventSetup const& iSetup) override;
  void analyze(const edm::Event&, const edm::EventSetup&) override;

  // ----------member data ---------------------------
  std::string processName_, triggerName_;
  HLTPrescaleProvider hltPrescaleProvider_;
};

prescalePlotter::prescalePlotter(const edm::ParameterSet& iConfig)
    : hltPrescaleProvider_(iConfig, consumesCollector(), *this) {
  processName_ = iConfig.getParameter<std::string>("processName");
  triggerName_ = iConfig.getParameter<std::string>("triggerName");
}

prescalePlotter::~prescalePlotter() = default;

void prescalePlotter::endRun(edm::Run const&, edm::EventSetup const&) {}

// ------------ method called for each event  ------------
void prescalePlotter::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup) {
  using namespace edm;
  using namespace std;

  const std::pair<int, int> prescales(hltPrescaleProvider_.prescaleValues(iEvent, iSetup, triggerName_));
  LogInfo("PPS") << "prescalePlotter::analyzeTrigger: path " << triggerName_ << " "
                 << "prescales L1T,HLT: " << prescales.first << "," << prescales.second;
}

void prescalePlotter::beginRun(edm::Run const& iRun, edm::EventSetup const& iSetup) {
  using namespace edm;
  bool changed(true);
  if (hltPrescaleProvider_.init(iRun, iSetup, processName_, changed)) {
    HLTConfigProvider const& hltConfig = hltPrescaleProvider_.hltConfigProvider();
    // if init returns TRUE, initialisation has succeeded!
    if (changed) {
      LogInfo("PPS") << "HLT configuration changed between runs";
      const unsigned int n(hltConfig.size());
      const unsigned int triggerIndex(hltConfig.triggerIndex(triggerName_));
      if (triggerIndex >= n) {
        LogInfo("PPS") << "prescalePlotter::analyze:"
                       << " TriggerName " << triggerName_ << " not available in (new) config!" << endl;
        LogInfo("PPS") << "Available TriggerNames are: " << endl;
        hltConfig.dump("Triggers");
      }
    }
  } else {
    LogError("PPS") << " HLT config extraction failure with process name " << processName_;
  }
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void prescalePlotter::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.add<std::string>("processName", "HLTX");
  desc.add<std::string>("triggerName", "HLT_CTPPSFilter_v2");
  desc.add<unsigned int>("stageL1Trigger", 2);
  descriptions.add("prescalePlotter", desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(prescalePlotter);
