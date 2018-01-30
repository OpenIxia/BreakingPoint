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
#  3) Enter 'source run_2544_test.tcl' at the Tcl prompt
#
#  Example:
#  % source run_2544_test.tcl
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

#
########################################################

puts -nonewline "\n=====================================================================\n\n";
puts "\nSTARTING TEST EXECUTION...\n\nBPS Host: $bps_host\nUsername: $bps_username\n"; 

# Clear BPS Tcl object
if {[info exists bps]} {itcl::delete object $bps; unset bps;}

# Connect to the BPS
puts -nonewline "=====================================================================\n\n";
puts -nonewline "Connecting to BreakingPoint Elite: $bps_host..."
set bps [bps::connect $bps_host $bps_username $bps_password -onclose exit]
puts "COMPLETED.\n"

# Create a temporary instance of the test case
puts -nonewline "Creating RFC 2544 test case..."
set test [$bps createRFC2544Test];
puts "COMPLETED.\n"

# Configure the RFC 2544 test case
puts -nonewline "Configuring the RFC 2544 test case..."
$test configure -packetType Ether
$test configure -customSteps {64, 512, 1024, 1380, 1518}
puts "COMPLETED.\n"

# Run the test case and display test progress 
puts -nonewline "======================================================================================\n";
puts -nonewline "RFC 2544 Test Case...STARTED\n\n"
$test run -progress "bps::textprogress stdout"
puts "--------------------------------------------------------------------------------------";
puts "Progress: 100%\t    Compiling Test Results...COMPLETED.";
puts "--------------------------------------------------------------------------------------\n";
puts "RFC 2544 Test Case...COMPLETED.\n";
puts -nonewline "=====================================================================\n\n";

itcl::delete object $bps; unset bps;

########################################################
