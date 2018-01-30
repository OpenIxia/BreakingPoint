########################################################
#
#  Description: 
#  This test case will run a user provided test case 
#  from the Tcl API with custom parameters. The user 
#  must set the parameters for the BPS host, username, 
#  password, slot/port, and test case name.
#
#  Usage:
#  1) Modify the parameters below
#  2) Start the BPS Tcl API
#  3) Enter 'source modified_profile_bps_test.tcl' at the Tcl prompt
#
#  Example:
#  % source modified_profile_bps_test.tcl
#
#  BreakingPoint Systems
#  10/08/2010
#
########################################################

#  Modify these parameters:

# Set the BPS IP address or host name
set bps_host "172.27.53.91"

# Set the BPS Username
set bps_username "admin"

# Set the BPS Password
set bps_password "12345678"

# Set the BPS Testcase Name
set bps_testcase_name "STBU Application Profile"

# Set the NEW BPS Testcase Name
set new_bps_testcase_name "MODIFIED STBU Application Profile"

# Set the old App Profile Name 
set old_app_profile "BreakingPoint Service Provider"

# Set the NEW App ProfileName
set modified_app_profile "MODIFIED Application Profile"

#
########################################################

puts -nonewline "\n=====================================================================\n\n";
puts "\nSTARTING TEST EXECUTION...\n\nBPS Test Case: $bps_testcase_name\nBPS Host: $bps_host\nUsername: $bps_username\n"; 

# Clear BPS Tcl object
if {[info exists bps]} {itcl::delete object $bps; unset bps;}

# Connect to the BPS
puts -nonewline "=====================================================================\n\n";
puts -nonewline "Connecting to BreakingPoint Elite: $bps_host..."
set bps [bps::connect $bps_host $bps_username $bps_password -onclose exit]
puts "COMPLETED.\n"

# Create a temporary instance of the test case
puts -nonewline "Searching for test case $bps_testcase_name..."
set test [$bps createTest -template $bps_testcase_name -name $new_bps_testcase_name];
puts "COMPLETED.\n"

puts -nonewline "Load, modify, and save the application profile..."
set app_profile [$bps createAppProfile -template $old_app_profile -name $modified_app_profile]
$app_profile removeSuperflow {BreakingPoint eDonkey Data Transfer}
$app_profile removeSuperflow {BreakingPoint BitTorrent Data Transfer}
$app_profile addSuperflow {BreakingPoint AOL Instant Messenger} 100 350
$app_profile save -name $modified_app_profile -force
puts "COMPLETED.\n"

puts -nonewline "Assign the modified application profile to the test case..."
set comp [dict get [$test getComponents] appsim_1]
$comp configure -profile $modified_app_profile
puts "COMPLETED.\n"

# Save the modified test case
puts -nonewline "Saving the modified test case $new_bps_testcase_name..."
$test save
puts "COMPLETED.\n"

# Run the test case and display test progress 
puts -nonewline "======================================================================================\n";
puts -nonewline "Test Case ($bps_testcase_name)...STARTED\n\n"
$test run -progress "bps::textprogress stdout"
puts "--------------------------------------------------------------------------------------";
puts "Progress: 100%\t    Compiling Test Results...COMPLETED.";
puts "--------------------------------------------------------------------------------------\n";
puts "Test Case ($bps_testcase_name)...COMPLETED.\n";
puts -nonewline "=====================================================================\n\n";

itcl::delete object $bps; unset bps;

########################################################
