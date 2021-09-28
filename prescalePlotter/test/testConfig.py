import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Modifier_ctpps_2018_cff import ctpps_2018
from Configuration.ProcessModifiers.run2_miniAOD_UL_cff import run2_miniAOD_UL
process = cms.Process('TEST', ctpps_2018, run2_miniAOD_UL)
#process = cms.Process('TEST', eras.Run2_$year, eras.run2_miniAOD_devel)

from conditions import *

def SetConditions(process):
  # chose GT
  process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
  process.GlobalTag = GlobalTag(process.GlobalTag, "120X_dataRun2_v2")

  # chose LHCInfo
  UseLHCInfoGT(process)
  #UseLHCInfoLocal(process)
  #UseLHCInfoDB(process, "frontier://FrontierProd/CMS_CONDITIONS", "LHCInfoEndFill_prompt_v2")

  # chose alignment
  UseAlignmentGT(process)
  #UseAlignmentLocal(process)
  #UseAlignmentFile(process, "sqlite_file:/afs/cern.ch/user/c/cmora/public/CTPPSDB/AlignmentSQlite/CTPPSRPRealAlignment_v13Jun19_v1.db", "PPSRPRealAlignment_v13Jun19")
  #UseAlignmentDB(process, "frontier://FrontierProd/CMS_CONDITIONS", "CTPPSRPAlignment_real_offline_v7")

  # chose optics
  UseOpticsGT(process)
  #UseOpticsLocal(process)
  #UseOpticsFile(process, "sqlite_file:/afs/cern.ch/user/w/wcarvalh/public/CTPPS/optical_functions/PPSOpticalFunctions_2016-2018_v9.db", "PPSOpticalFunctions_test")
  #UseOpticsDB(process, "frontier://FrontierProd/CMS_CONDITIONS", "PPSOpticalFunctions_offline_v6")

# minimum of logs
process.MessageLogger = cms.Service("MessageLogger",
  statistics = cms.untracked.vstring(),
  destinations = cms.untracked.vstring("cout"),
  cout = cms.untracked.PSet(
    threshold = cms.untracked.string("INFO")
  )
)

# raw data source
process.source = cms.Source("PoolSource",
  fileNames = cms.untracked.vstring(
    "file:/afs/cern.ch/work/m/maaraujo/public/output/output_Cal.root"
    # "root://eoscms.cern.ch//eos/cms/store/group/phys_pps/sw_test_input/4E7ABE07-FE4C-E811-9395-FA163EC5FAA0.root"
    ),

  # inputCommands = cms.untracked.vstring(
  #   'drop *',
  #   'keep FEDRawDataCollection_*_*_*'
  # )

  inputCommands = cms.untracked.vstring(
    'keep *'
  )
  
)

process.maxEvents = cms.untracked.PSet(
  input = cms.untracked.int32(-1)
)

# load default alignment settings
process.load("CalibPPS.ESProducers.ctppsAlignment_cff")

# raw-to-digi conversion
process.load("EventFilter.CTPPSRawToDigi.ctppsRawToDigi_cff")

# local RP reconstruction chain with standard settings
process.load("RecoPPS.Configuration.recoCTPPS_cff")

# define conditions
SetConditions(process)
CheckConditions()

# reconstruction plotter
process.ctppsProtonReconstructionPlotter = cms.EDAnalyzer("CTPPSProtonReconstructionPlotter",
  tagTracks = cms.InputTag("ctppsLocalTrackLiteProducer"),
  tagRecoProtonsSingleRP = cms.InputTag("ctppsProtons", "singleRP"),
  tagRecoProtonsMultiRP = cms.InputTag("ctppsProtons", "multiRP"),

  rpId_45_F = cms.uint32(23),
  rpId_45_N = cms.uint32(3),
  rpId_56_N = cms.uint32(103),
  rpId_56_F = cms.uint32(123),

  association_cuts_45 = process.ctppsProtons.association_cuts_45,
  association_cuts_56 = process.ctppsProtons.association_cuts_56,

  outputFile = cms.string("testMarianaOutput.root")
)

## load DQM framework
process.load("DQM.Integration.config.environment_cfi")
process.dqmEnv.subSystemFolder = "CTPPS"
process.dqmEnv.eventInfoFolder = "EventInfo"
process.dqmSaver.path = ""
process.dqmSaver.tag = "CTPPS"

## CTPPS DQM modules
process.load("DQM.CTPPS.ctppsDQM_cff")

# Modify to match Mariana's product name
process.ctppsPixelDigis.inputLabel = cms.InputTag("hltPPSCalibrationRaw","","HLTX")

# Comply with events not passing the HLT not having the RAW data
process.options = cms.PSet(
  SkipEvent = cms.untracked.vstring('ProductNotFound')
)

# Prescale plotter
process.load("PPSTools.prescalePlotter.prescalePlotter_cfi")
process.prescalePlotter.processName = cms.string("HLTX")

# processing sequences
process.path = cms.Path(
  process.ctppsRawToDigi
  * process.recoCTPPS
  * process.ctppsProtonReconstructionPlotter
  * process.prescalePlotter
  * process.ctppsDQMOfflineSource
  * process.ctppsDQMOfflineHarvest
)

process.end_path = cms.EndPath(
  process.dqmEnv +
  process.dqmSaver
)
