*** Settings ***
Documentation   Load a saved config file, start traffic and get stats.
Metadata  Version  1.0

Library  BuiltIn

# This script assumes that your PYTHONPATH has the path to BpsApi.py.
# Otherwise, state the full path: /full_path_to/BreakingPoint/RestApi/Python/Modules/BpsApi.py.
Library  BpsApi.py

*** Variables ***
${chassis}   192.168.70.116
${username}  admin
${password}  admin
${filename}  ../../../../ConfigFiles/HTTP_B2B.bpt

*** Keywords ***
Get Watched Stats
    [Arguments]  ${id}
    ${watchStats}  watch stats  testid=${id}
    Log To Console  ${watchStats}

*** Test Cases ***
Load a saved config
    Log To Console  Start

    Log To Console  Login
    Login  chassis=${chassis}  username=${username}  password=${password}

    Log To Console  Upload config
    ${testname}  Upload Config  filename=${filename}  force=true

    Log To Console  Reserve ports
    ${slot}   Set Variable  1
    @{ports}  Create List  0  1
    Reserve Ports  slot=${slot}  portlist=@{ports}  force=true

    Log To Console  Watch stats
    ${rxFrames}  Set Variable  ethRxFrames
    ${txFrames}  Set Variable  ethTxFrames
    Add Stat Watch  statname=${rxFrames}
    Add Stat Watch  statname=${txFrames}

    Log To Console  Run test
    ${testid}  Run Test  testname=${testname}

    Log To Console  Get test progress
    : FOR  ${i}  IN RANGE  1  999999
      \  ${progress}  Get Test Progress  testid=${testid}
      \  Log To Console  ${progress}
      \  Run Keyword If  ${progress} > 0  Get Watched Stats  ${testid}
      \  Sleep  5s
      \  Exit For Loop If  ${progress} == 100

    Log To Console  Test Finished

    Log To Console  Get test result
    ${result}  Get Test Result  testid=${testid}
    Log To Console  ${result}

    Log To Console  Download report
    ${reportname}  Set Variable  sample_HTTP_B2B.pdf
    ${location}  Set Variable  ${CURDIR}/Reports
    Download Report  testid=${testid}  reportname=${reportname}  location=${location}

    Log To Console  Unreserve ports
    Unreserve Ports  slot=${slot}  portlist=@{ports}

    Log To Console  Logout
    logout
