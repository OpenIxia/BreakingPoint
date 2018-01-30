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
#  3) Enter 'source run_session_test.tcl' at the Tcl prompt
#
#  Example:
#  % source run_session_test.tcl
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
set bps_testcase_name "STBU Session Sender"

# Set the new CPS rate
set new_cps_rate 5000

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
set test [$bps createTest -template $bps_testcase_name -name $bps_testcase_name];
puts "COMPLETED.\n"

# Modify the CPS value
puts -nonewline "Configuring the CPS rate for $new_cps_rate..."
set comp [dict get [$test getComponents] sessionsender_1]
$comp configure -sessions.maxPerSecond $new_cps_rate
puts "COMPLETED.\n"

# Save the modified test case
puts -nonewline "Saving the modified test case $bps_testcase_name..."
$test save -force
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
