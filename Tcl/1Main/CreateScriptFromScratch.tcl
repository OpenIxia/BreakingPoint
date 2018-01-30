#!/usr/bin/tclsh

# Written by: Hubert Gee
#
# Description
#
#   Sample script creating a script from scratch.
#
# Note: 
#    The interface number is mapped to the order of ports reserved
#
# Creating a chassis object
# Creating a Network Neighborhood
# Creating an App Profile
# Creating Super Flows
# Creating an Attack Plan
# Creating a Strike List
# Creating a Load Profile
# Creating a Test
# Creating a Test Series
# Creating a Multi-box Test
# Creating a Test Component
# Returning test results

set username admin
set password admin
#set bps_host 10.219.117.81
#set port_list "1/0 1/1" ;# slot0/port1, slot0/port2
#set port1 1
#set port2 2

set bps_host 10.219.117.88
set port_list "0/0 0/9" ;# slot0/port1, slot0/port2
set port1 1
set port2 2

set neighborhoodName hgee_neighborhood
set appProfileTemplate "Cisco EMIX 2012"
set appProfileName hgee_appProfile


proc getStats { args } {
    global fileId 

    set stats [lindex $args 1];
    set p [dict get $stats progress];

    puts \n
    foreach {stat counter} [lindex $args 1] {
	puts "\t${stat}: $counter"
    }
    puts \n

    if { $p > 1 && $p < 100 } {
	set prog [format %3.0f [dict get $stats progress]];
	if {[dict exists $stats appAttempted] == 1} {
	    set attempted [dict get $stats appAttempted];
	} else {
	    set attempted 0
	}
	if {[dict exists $stats appSuccessful] == 1} {
	    set successful [dict get $stats appSuccessful];
	} else {
	    set successful 0
	}
	if {[dict exists $stats tcpClientEstablishRate] == 1} {
	    set tcp_rate [format %-8.0f [dict get $stats tcpClientEstablishRate]];
	} else {
	    set tcp_rate 0
	}
	if {[dict exists $stats appTxFrameDataRate] == 1} {
	    set tx_data_rate [dict get $stats appTxFrameDataRate];
	} else {
	    set tx_data_rate 0
	}
	if {[dict exists $stats ethRxFrameDataRate] == 1} {
	    set rx_data_rate [dict get $stats ethRxFrameDataRate];
	} else {
	    set rx_data_rate 0
	}
	if {[dict exists $stats appAttemptedRate] == 1} {
	    set attempted_rate [format %0.0f [dict get $stats appAttemptedRate]];
	} else {
	    set attempted_rate 0
	}
	if {[dict exists $stats appSuccessfulRate] == 1} {
	    set successful_rate [format %0.0f [dict get $stats appSuccessfulRate]];
	} else {
	    set successful_rate 0
	}

	puts "----------------------------------------";
	puts "\nProgress: $prog%"
	puts "  Flows Attempted/Successful: $attempted/$successful";
	puts "  TCP Rate Achieved: $tcp_rate";
	puts "  Throughput: $rx_data_rate";
	puts "  CPS Attempted/Successful: $attempted_rate/$successful_rate";

	#if { $p > 40 && $p < 80 } {
	#    incr avg_bw_counter
	#    set avg_bw [expr $avg_bw + $rx_data_rate]
	#    incr avg_cps_counter
	#    set avg_cps [expr $avg_cps + $successful_rate]
	    #puts "avg_bw_counter: $avg_bw_counter"
	    #puts "avg_bw: $avg"
	#}	
    } elseif {$p == 0} {
	puts "Initializing...";
    }
    
    puts $fileId ""
    dict for {var val} $stats {
    	puts $fileId "$var: $val"
    }
}

# Connect to the BPS
if {[info exists bps]} {
    itcl::delete object $bps
    unset bps
}

puts -nonewline "\nConnecting to $bps_host as $username $password..."

if {[catch {set bps [bps::connect $bps_host $username $password -onclose exit]} errInfo]} {
    puts "\nError connecting: $errInfo"
    exit
}

puts "\nConnected to ${bps_host}: $bps\n"

puts "Creating Test ..."
set test [$bps createTest -name "hgee_test"]
#$test configure -totalBandwidth 50

catch {$test configure -name $neighborhoodName} errMsg
puts "Configuring Test to a Name: $errMsg\n"

# Get Chassis object
set chassisObj [$bps getChassis]
puts "\nChassisObj: $chassisObj"

# Clear ports
foreach port $port_list {
    set slot [lindex [split $port /] 0]
    set port [lindex [split $port /] 1]
    # 0:0  and 0:1

    puts "\nClearing port $slot/$port ..."
    $chassisObj unreservePort $slot $port

    puts "Reserving port $slot/$port ..."
    $chassisObj reservePort $slot $port
}


puts "Creating AppProfile ..."
set appProfile [$bps createAppProfile -template {Cisco EMIX 2012} -name $appProfileName]

puts "Saving AppProfile: $appProfile ..."
catch {$appProfile save -force} errMsg
puts "Saving appProfile result: $errMsg\n"

# Create a new Network Neighborhood
set newNetwork [$bps createNetwork]

puts "Configuring Neighborhood with name: $neighborhoodName ..."
catch {$newNetwork configure -name $neighborhoodName} errMsg
puts "Saving Neighborhood result: $errMsg\n"

puts "\nBegin newNetwork ..."
$newNetwork begin

# Interface1 is the given name to interface 1 (-number), which is port 0:0 
# or which ever port was reserved first.
puts "\nAdding interface Interface1 ..."
$newNetwork add interface -id Interface1 -number 1
$newNetwork add interface -id Interface2 -number 2

for {set vlanId 1} {$vlanId <= 10} {incr vlanId} {
    puts "Creating VlanId: $vlanId"
    set decimalToHex [format %02x $vlanId]
    $newNetwork add vlan -id vlan$vlanId -default_container Interface1 -inner_vlan $vlanId -mac_address 00:08:08:09:00:$decimalToHex
    $newNetwork add ip_static_hosts -id Range$vlanId -default_container vlan$vlanId -tags myClient -count 1 -ip_address 1.1.1.$vlanId -netmask 24 -gateway_ip_address 1.1.1.11
}

for {set vlanId 11} {$vlanId <= 20} {incr vlanId} {
    puts "Creating VlanId: $vlanId"
    set decimalToHex [format %02x $vlanId]
    $newNetwork add vlan -id vlan$vlanId -default_container Interface2 -inner_vlan $vlanId -mac_address 00:08:08:09:00:$decimalToHex
    $newNetwork add ip_static_hosts -id Range$vlanId -default_container vlan$vlanId -tags myServer -count 1 -ip_address 1.1.1.$vlanId -netmask 24 -gateway_ip_address 1.1.1.1
}

puts "Saving Neighborhood config ..."
catch {$newNetwork save -force} errMsg
puts "Save Neighborhood result: $errMsg\n"

puts "Test --> neighborhood: $neighborhoodName ..."
catch {$test configure -neighborhood $neighborhoodName} errMsg
puts "Configuring Test to a Neighborhood: $errMsg\n"


# 1 = interface 1 (port1) = Server
# 2 = interface 2 (port2) = Client
puts "Creating Test Component ..."
set testComponent [$test createComponent appsim #auto 1 2]
set componentList [$test getComponents]

puts "Configuring test component with -profile $appProfileName ..."
catch {$testComponent configure -profile $appProfileName} errMsg
puts "Test component result: $errMsg\n"

$testComponent configure -client_tags {"myClient"} 
$testComponent configure -server_tags {"myServer"} 

global fileId
set fileId [open perfectStorm_result w]

puts "Saving the Test ..."
catch {$test save -force} errMsg
puts "Save test result: $errMsg\n"

$test run -rtstats getStats

puts -nonewline "\n\n----------------------------------------\n\n"
puts "Progress: 100%   \[Test Run Summary Below\]\n";
puts -nonewline "----------------------------------------\n\n"

# Gather the custom test results and output to CLI
foreach {x comp} $componentList {
    if [regexp {appsim} $x] then {
	set r [$comp result];
	set attempted [$r get appAttempted];
	set success [$r get appSuccessful];
	set failed [expr $attempted - $success];
	set achieved [$r get tcpMaxClientEstablishRate];
	puts -nonewline "CPS Rate Achieved: $achieved\n";
	puts -nonewline "Flows Attempted: $attempted\n";
	puts -nonewline "Flows Successful: $success\n";
	puts -nonewline "Flows Failed: $failed\n";
	
	puts $fileId "\nResults from the Performance Test:"
	puts $fileId "============================================================="
	set result [$comp result]
	set values [$result values]

	foreach value $values {
	    set v [$result get $value] 
	    puts $fileId "   $value: $v"
	}
    }
}

puts "\nTest case...COMPLETED.\n";

puts "Closing fileId ..."
close $fileId

#puts "Exporting test result ..."
#$test exportReport -format csv -file perfectStorm_results


if 0 {
  # connect level
  bPSConnection6 _componentGroups type
  bPSConnection6 _componentParams namespace compname
  bPSConnection6 _exec cmd
  bPSConnection6 _execXml xml ?token? ?usetimeout?
  bPSConnection6 _getId
  bPSConnection6 _networkParams type
  bPSConnection6 _reserveToken
  bPSConnection6 _schemaver
  bPSConnection6 _testParams
  bPSConnection6 addUser id password name email ?group?
  bPSConnection6 backup ?arg arg ...?
  bPSConnection6 cancel ?context?
  bPSConnection6 cget -option
  bPSConnection6 clearResults ?context?
  bPSConnection6 cliVersion ?arg arg ...?
  bPSConnection6 configure ?-option? ?value -option value...?
  bPSConnection6 configureContext ctxname ?arg arg ...?
  bPSConnection6 createAppProfile ?arg arg ...?
  bPSConnection6 createAttackSeries ?arg arg ...?
  bPSConnection6 createComponent ?arg arg ...?
  bPSConnection6 createEvasionProfile ?arg arg ...?
  bPSConnection6 createLTETest ?arg arg ...?
  bPSConnection6 createLawfulInterceptTest ?arg arg ...?
  bPSConnection6 createLoadProfile ?arg arg ...?
  bPSConnection6 createMultiboxTest ?arg arg ...?
  bPSConnection6 createMulticastTest ?arg arg ...?
  bPSConnection6 createNeighborhood ?arg arg ...?
  bPSConnection6 createNetwork ?arg arg ...?
  bPSConnection6 createRFC2544Test ?arg arg ...?
  bPSConnection6 createResiliencyTest ?arg arg ...?
  bPSConnection6 createServerResiliencyTest ?arg arg ...?
  bPSConnection6 createSessionLabTest ?arg arg ...?
  bPSConnection6 createStrikeList ?arg arg ...?
  bPSConnection6 createSuperflow ?arg arg ...?
  bPSConnection6 createTest ?arg arg ...?
  bPSConnection6 createTestSeries ?arg arg ...?
  bPSConnection6 delete
  bPSConnection6 deleteAppProfile ?arg arg ...?
  bPSConnection6 deleteAttackSeries ?arg arg ...?
  bPSConnection6 deleteContext ctxname
  bPSConnection6 deleteEvasionProfile ?arg arg ...?
  bPSConnection6 deleteLoadProfile ?arg arg ...?
  bPSConnection6 deleteMultiboxTest name
  bPSConnection6 deleteNeighborhood ?arg arg ...?
  bPSConnection6 deleteStrikeList ?arg arg ...?
  bPSConnection6 deleteSuperflow ?arg arg ...?
  bPSConnection6 deleteTest name ?arg arg ...?
  bPSConnection6 deleteTestResults ?arg arg ...?
  bPSConnection6 deleteTestSeries name
  bPSConnection6 exportFlowStats ?arg arg ...?
  bPSConnection6 exportReport ?arg arg ...?
  bPSConnection6 exportTest ?arg arg ...?
  bPSConnection6 factoryRevert ?arg arg ...?
  bPSConnection6 getAggStats ?arg arg ...?
  bPSConnection6 getBuildId
  bPSConnection6 getChassis ?arg arg ...?
  bPSConnection6 getDut ?context?
  bPSConnection6 getLicenses
  bPSConnection6 getNeighborhood ?context?
  bPSConnection6 getReportComponents testid ?iterations?
  bPSConnection6 getReportContents testid ?arg arg ...?
  bPSConnection6 getReportSectionXML testid ?arg arg ...?
  bPSConnection6 getReportTable testid ?arg arg ...?
  bPSConnection6 getStrikeInfo strike
  bPSConnection6 getStrikeSetInfo strikeset
  bPSConnection6 getStrikepackId
  bPSConnection6 getSystemGlobal varname
  bPSConnection6 getSystemType
  bPSConnection6 getTest context
  bPSConnection6 getVersion
  bPSConnection6 host
  bPSConnection6 importLicense ?arg arg ...?
  bPSConnection6 importPcap name ?arg arg ...?
  bPSConnection6 importStrikelist name ?arg arg ...?
  bPSConnection6 importTest name ?arg arg ...?
  bPSConnection6 initContext ctxname ?arg arg ...?
  bPSConnection6 installStrikepack ?arg arg ...?
  bPSConnection6 installUpdate ?arg arg ...?
  bPSConnection6 isa className
  bPSConnection6 listAppProfiles ?arg arg ...?
  bPSConnection6 listAttackProfiles ?arg arg ...?
  bPSConnection6 listAttackSeries ?arg arg ...?
  bPSConnection6 listBackups ?arg arg ...?
  bPSConnection6 listDUTs ?arg arg ...?
  bPSConnection6 listEvasionProfiles ?arg arg ...?
  bPSConnection6 listLoadProfiles ?arg arg ...?
  bPSConnection6 listMultiboxTests ?arg arg ...?
  bPSConnection6 listNeighborhoods ?arg arg ...?
  bPSConnection6 listProtocols ?arg arg ...?
  bPSConnection6 listStrikeKeywords
  bPSConnection6 listStrikeSets ?arg arg ...?
  bPSConnection6 listStrikes ?arg arg ...?
  bPSConnection6 listSuperflows ?arg arg ...?
  bPSConnection6 listTestResults ?arg arg ...?
  bPSConnection6 listTestSeries ?arg arg ...?
  bPSConnection6 listTests ?arg arg ...?
  bPSConnection6 listUsers
  bPSConnection6 locale
  bPSConnection6 networkInfo ?arg arg ...?
  bPSConnection6 previousRevert ?arg arg ...?
  bPSConnection6 reboot ?arg arg ...?
  bPSConnection6 removeUser id
  bPSConnection6 restoreBackup ?arg arg ...?
  bPSConnection6 resultId ?context?
  bPSConnection6 run ?arg arg ...?
  bPSConnection6 save ?arg arg ...?
  bPSConnection6 searchStrikeLists ?arg arg ...?
  bPSConnection6 searchStrikes ?arg arg ...?
  bPSConnection6 serialNumber ?arg arg ...?
  bPSConnection6 setDut name ?context?
  bPSConnection6 setNeighborhood name ?context?
  bPSConnection6 updateNetwork ?arg arg ...?
  bPSConnection6 updateProfile ?arg arg ...?
  bPSConnection6 updateUser id ?arg arg ...?
  bPSConnection6 uptime ?arg arg ...?
  bPSConnection6 userInfo id
  bPSConnection6 userid
  bPSConnection6 wait ?context?
}

if 0 {
    # chassis level
    chassisClient7 cancelTest testid
    chassisClient7 cget -option
    chassisClient7 configure ?-option? ?value -option value...?
    chassisClient7 configurePort slot port ?arg arg ...?
    chassisClient7 exportPacketTrace dir ?arg arg ...?
    chassisClient7 expungeDB ?arg arg ...?
    chassisClient7 getDiags ?arg arg ...?
    chassisClient7 getResourceAllocation slot ?arg arg ...?
    chassisClient7 getState
    chassisClient7 getSystemErrorLog
    chassisClient7 getTests
    chassisClient7 isa className
    chassisClient7 packetTraceStatus
    chassisClient7 reservePort slot port ?arg arg ...?
    chassisClient7 setNote slot port note
    chassisClient7 setPortOrder ?arg arg ...?
    chassisClient7 unreservePort slot port
    chassisClient7 wait
}

if 0 {
    # Neighborhood
    hgee_Neighborhood _getXML
    hgee_Neighborhood addDHCPClients interface domain ?arg arg ...?
    hgee_Neighborhood addDomain interface name
    hgee_Neighborhood addENodeB interface domain ?arg arg ...?
    hgee_Neighborhood addENodeBClients interface domain ?arg arg ...?
    hgee_Neighborhood addGGSN interface domain ?arg arg ...?
    hgee_Neighborhood addHostRange interface domain ?arg arg ...?
    hgee_Neighborhood addImpairment interface ?arg arg ...?
    hgee_Neighborhood addMME interface domain ?arg arg ...?
    hgee_Neighborhood addMMEClients interface domain ?arg arg ...?
    hgee_Neighborhood addPath sourceinterface sourcedomain sourcevlan destinterface destdomain destvlan
    hgee_Neighborhood addSGSN interface domain ?arg arg ...?
    hgee_Neighborhood addSGSNClients interface domain ?arg arg ...?
    hgee_Neighborhood addSGWClients interface domain ?arg arg ...?
    hgee_Neighborhood addSubnet interface name subnet
    hgee_Neighborhood cget option
    hgee_Neighborhood configure ?arg arg ...?
    hgee_Neighborhood domainNames ?interface?
    hgee_Neighborhood getDHCPServer interface domain ?innervlan? ?outervlan?
    hgee_Neighborhood getFilters
    hgee_Neighborhood getImpairments
    hgee_Neighborhood getPaths
    hgee_Neighborhood getSubnets interface name
    hgee_Neighborhood getVlanEtherType interface
    hgee_Neighborhood isa className
    hgee_Neighborhood removeDHCPClients interface domain ?innervlan? ?outervlan?
    hgee_Neighborhood removeDomain interface name
    hgee_Neighborhood removeENodeB interface domain ?arg arg ...?
    hgee_Neighborhood removeENodeBClients interface domain ?innervlan? ?outervlan?
    hgee_Neighborhood removeFilter interface
    hgee_Neighborhood removeGGSN interface domain ?innervlan? ?outervlan?
    hgee_Neighborhood removeHostRange interface domain ?innervlan? ?outervlan?
    hgee_Neighborhood removeImpairment interface
    hgee_Neighborhood removeMME interface domain ?arg arg ...?
    hgee_Neighborhood removeMMEClients interface domain ?innervlan? ?outervlan?
    hgee_Neighborhood removePath sourceinterface sourcedomain sourcevlan destinterface destdomain destvlan
    hgee_Neighborhood removeSGSN interface domain ?arg arg ...?
    hgee_Neighborhood removeSGSNClients interface domain ?innervlan? ?outervlan?
    hgee_Neighborhood removeSGWClients interface domain ?innervlan? ?outervlan?
    hgee_Neighborhood removeSubnet interface name ?innervlan? ?outervlan?
    hgee_Neighborhood save ?arg arg ...?
    hgee_Neighborhood setDHCPServer interface domain ?arg arg ...?
    hgee_Neighborhood setFilter interface ?arg arg ...?
    hgee_Neighborhood setVlanEtherType interface value
}
