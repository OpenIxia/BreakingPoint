########################################################
#
#  Description: 
#  
#  
#  
#
#  Usage:
#  1) Modify the parameters below
#  2) Start the BreakingPoint Tcl Shell
#  3) Enter 'source session_rate_from_bandwidth.tcl' at the Tcl prompt
#
#  Example:
#  % source raytheon_set_all_params.tcl
#
#  BreakingPoint Systems
#  03/12/2010
#
########################################################


########################################################
#
#  Modify these parameters:
########################################################
# Set this variable:
#   0:  Prints out configuration parameters
#   1:  Actually configures and run tests
set validate_result 0

# Set the BreakingPoint IP address or host name
set bps_host "10.10.10.10";

# Set the BreakingPoint Username
set bps_username "admin";

# Set the BreakingPoint Password
set bps_password "admin";

# Set the BreakingPoint Testcase Name
set bps_app_profile "name_app_Profile";

# Set the BreakingPoint Data Rate and Tolerance
set bps_data_rate 10000;
set data_rate_tolerance .001

# Set the BreakingPoint Ramp Up Duration
set ramp_up_duration 30;

# Set the BreakingPoint Ramp Up Duration
set steady_duration 300;

# Set the BreakingPoint Ramp Up Duration
set ramp_down_duration 30;


######################################################
## Port Reservation Parameters
######################################################
# Set the Client Slot
set client_slot 1
set client_port 0
# Set the Server Slot
set server_slot 1
set server_port 2


########################################################

# Where all the magic happens.
# Thanks Jin!
proc app_getSessionRate { appName {dataRate $bps_data_rate} } {
	global bps
	set dataRate [expr $dataRate * 125000]; #convert it to Bps
	set ap [$bps createAppProfile -template $appName]
	set root [lindex [$ap info variable _xmlroot] 4]
	set totalWeight 0
	foreach e [$root selectNode superflow] {
		incr totalWeight [$e @weight]
	}
	set totalSessions 0
	foreach e [$root selectNode superflow] {
		set size [$e @estimate_bytes]
		set weight [$e @weight]
		set tmpDataRate [expr $dataRate / $totalWeight * $weight]
		set sessionRate [expr $tmpDataRate / $size]
		incr totalSessions $sessionRate
	}

	itcl::delete object $ap

	return $totalSessions
}

# Real-time Stats 
proc getStats {args} {
    global max_bw
    set stats [lindex $args 1];
    
    set p [dict get $stats progress];
    

    
    if { $p > 1 && $p < 100 } {
	set prog [format %3.0f [dict get $stats progress]];
	set t [format %6.0f [dict get $stats time]];
	if { [dict exists $stats ethTxFrameDataRate] } {
	    set cur_bw [format %1.1f [dict get $stats ethTxFrameDataRate]];
	} else {
	    set cur_bw 0;
	}
	puts "\n--------------------------------------------------------------------------------------";
	if { $cur_bw > $max_bw } {
	    set max_bw $cur_bw;
	}
	puts "Progress: $prog%\t    Execution Time (seconds): $t\t    Max BW Rate Achieved: $max_bw";	

    } elseif {$p == 0} {
	puts "--------------------------------------------------------------------------------------";
	puts "Initializing...";
    } elseif {$p == 100} {
	puts "--------------------------------------------------------------------------------------";
	puts "Progress:  99%\t    Compiling Test Results...";
    }
}



# Get date and timestamp 
set timestamp [clock format [clock sec] -format %m.%d.%Y.%H.%M.%S];
set month [clock format [clock sec] -format %B];
set day [clock format [clock sec] -format %d];
set year [clock format [clock sec] -format %Y];
set date "$month $day, $year";

puts -nonewline "\n=====================================================================\n\n";
puts "\nCalculating Requisite Parameters...\nApplication Profile: $bps_app_profile\nHost: $bps_host\nUsername: $bps_username\nDate: $date\n"; 

# Clear BPS Tcl object
if {[info exists bps]} {itcl::delete object $bps; unset bps;}

# Connect to the BreakingPoint
puts -nonewline "\nConnecting to $bps_host..."
if { [catch {set bps [bps::connect $bps_host $bps_username $bps_password -onclose exit]}]} {
    puts "\n\[!\] Error connecting: $errorInfo";
    puts "\nCheck the value in the \$bps_host parameter. UNABLE TO CONNECT TO BreakingPoint HOST."
    return;
}
puts "COMPLETED.\n"


# Finding Proper Parameters for the $bps_app_profile Application Profile...
puts -nonewline "Finding Proper Parameters for the $bps_app_profile Application Profile at $bps_data_rate Mbps...\n";
set max_cps_rate [app_getSessionRate $bps_app_profile $bps_data_rate];
puts "COMPLETED.  Initial CPS Rate: $max_cps_rate\n"

if { $max_cps_rate > 750000 } {
    puts "Calculated Theoretical CPS Rate Exceeds Current Capabilities.  $max_cps_rate CPS\n"
}



#########################################################
# Calculate Parameters for Application Simulator Component
#########################################################
set min_cps_rate   [format %1.0f [expr $max_cps_rate / $ramp_up_duration]]
set incr_cps_rate  [format %1.0f [expr $max_cps_rate / $ramp_up_duration]]
set max_concurrent [format %1.0f [expr $max_cps_rate * .1]]
###################################
## used to calculate actual Tput
set max_bw 1  

#########################################################
# Calculate Parameters for Application Simulator Component
#########################################################
# Output Parameters for Manual Setup
puts "Application Simulator Parameters for the given setup options:\n"
puts -nonewline "Data Rate.Minimum data rate...........................$bps_data_rate\n";
puts -nonewline "Session Ramp Distribution.Ramp Up Behavior............Full Open + Data + Close\n";
puts -nonewline "Session Ramp Distribution.Ramp Up Time Interval.......$ramp_up_duration\n";
puts -nonewline "Session Ramp Distribution.Steady-State Behavior.......Open and Close Sessions\n";
puts -nonewline "Session Ramp Distribution.Steady-State Seconds........$steady_duration\n";
puts -nonewline "Session Ramp Distribution.Ramp Down Behavior..........Full Close\n";
puts -nonewline "Session Ramp Distribution.Ramp Down Seconds...........$ramp_down_duration\n";
puts -nonewline "Ramp Up Profile.Ramp Up Profile Type..................Stair Step\n";
puts -nonewline "Ramp Up Profile.Minimum Connection Rate...............$min_cps_rate\n";
puts -nonewline "Ramp Up Profile.Maximum Connection Rate...............$max_cps_rate\n";
puts -nonewline "Ramp Up Profile.Increment N connections per second....$incr_cps_rate\n";
puts -nonewline "Ramp Up Profile.Fixed time interval...................$max_cps_rate\n";
puts -nonewline "Session Configuration.Maximum Simultaneous Sessions...$max_concurrent\n";
puts -nonewline "Session Configuration.Maximum Sessions Per Second.....$max_cps_rate\n";
puts -nonewline "Session.Configuration.Unlimited Session Close Rate....true\n";



if { $validate_result } {
    
    
    
    
    
    puts "The 'validate_result' variable was set.  Iterative series now starting...";
    #########################################################
    # Port Reservation Actions
    #########################################################
    # Use 'chassis' object to reserve appropriate ports
    #puts -nonewline "Reserving Ports...\n";
    #set chassis [$bps getChassis]
    
    #$chassis unreservePort $client_slot $client_port;
    #$chassis unreservePort $server_slot $server_port;
    
    #puts -nonewline "Reserving Port $client_port on Slot $client_slot...\n";
    #$chassis reservePort $client_slot $client_port;
    #puts "COMPLETED. \n"
    #puts -nonewline "Reserving Port $server_port on Slot $server_slot...\n";
    #$chassis reservePort $server_slot $server_port;
    #puts "COMPLETED. \n"
    
    
    
    # Parameters required for initial test run
    set run_again 1;
    set previous_rate 0;
    
    set test [$bps createTest -name "Session Rate Easy Button"];
    set appsim [$test createComponent appsim "Easy Button3" 1 2]; 
    
    # Increase or Decrease the CPS to find the Max BW 
    # Set $run_again = 0 to end the testcase or $run_again = 1 to continue
    while {$run_again != 0} { 
	# Run the test case and display test progress 
	puts -nonewline "======================================================================================\n";
	puts -nonewline "Attempting CPS Rate: $max_cps_rate\n";
	puts -nonewline "Test Case...STARTED\n"
	
	#########################################################
	# Create AppSim Component and Configure
	#########################################################
	$appsim configure \
	    -rateDist.min $bps_data_rate \
	    -rampDist.upBehavior "full+data+close" \
	    -rampDist.up 5 \
	    -rampDist.steady 5 \
	    -rampDist.down 5 \
	    -rampUpProfile.type "step" \
	    -rampUpProfile.min $min_cps_rate \
	    -rampUpProfile.max $max_cps_rate \
	    -rampUpProfile.increment $incr_cps_rate \
	    -rampUpProfile.interval 1 \
	    -sessions.max $max_concurrent \
	    -sessions.maxPerSecond $max_cps_rate \
	    -sessions.closeFast true \
	    -profile $bps_app_profile;
	
	set zero [format %3.0f 0]
	
	puts "Progress: $zero%\t    Execution Time (seconds): $zero\t    Max BW Rate Achieved: $zero";	

	## Run Test Here
	$test run -rtstats getStats;

	puts "--------------------------------------------------------------------------------------";
	puts "Progress: 100%\t    Compiling Test Results...COMPLETED.";
	puts "--------------------------------------------------------------------------------------\n";
	
	# Determine if we should make another test run
	set rate_delta [expr abs([expr $max_bw - $bps_data_rate])];
	#puts "rate_delta: $rate_delta";
	set percent_different [expr $rate_delta / $bps_data_rate];
	#puts "percent_different: $percent_different";
	
	if { $percent_different <= $data_rate_tolerance } {
	    puts "Max BW acheived ($max_bw) within tolerance ($data_rate_tolerance) of Configured BW ($bps_data_rate)";
	    set run_again 0;
	} else {
	    if { $max_bw > $bps_data_rate } {
		set rate_delta [expr $rate_delta * -1];
		## Delme
		puts "Max BW > $bps_data_rate.  New delta: $rate_delta";
	    }
	    
	    
	    if { $max_cps_rate != 750000 } {
		set max_cps_rate [expr \
				      [format %1.0f $max_cps_rate] \
				      * [format %1.0f $bps_data_rate] \
				      / [format %1.0f $max_bw]]
	    }
#	    #set max_cps_rate [format %1.0f [expr $max_cps_rate * [expr $percent_different + 1]]]
	    puts "New MAX CPS rate: $max_cps_rate\n";
	    if { $max_cps_rate > 750000 } {
		puts "Theoretical Maximum Exceeded.  Attempting 750000";
		set max_cps_rate 750000

	    } elseif { $max_cps_rate == 750000 } {
		puts "Unable to acheive bandwidth under these configuration parameters";
		set run_again 0;
	    }
	    
	    set max_bw  4;
	    
	}
	
	
	#########################################################
	# Calculate Parameters for Application Simulator Component
	#########################################################
	set min_cps_rate   [format %1.0f [expr $max_cps_rate / $ramp_up_duration]]
	set incr_cps_rate  [format %1.0f [expr $max_cps_rate / $ramp_up_duration]]
	set max_concurrent [format %1.0f [expr $max_cps_rate * .1]]
	###################################
	## used to calculate actual Tput

	
	#########################################################
	# Calculate Parameters for Application Simulator Component
	#########################################################
	# Output Parameters for Manual Setup
	puts "Application Simulator Parameters for the given setup options:\n"
	puts -nonewline "Data Rate.Minimum data rate...........................$bps_data_rate\n";
	puts -nonewline "Session Ramp Distribution.Ramp Up Behavior............Full Open + Data + Close\n";
	puts -nonewline "Session Ramp Distribution.Ramp Up Time Interval.......$ramp_up_duration\n";
	puts -nonewline "Session Ramp Distribution.Steady-State Behavior.......Open and Close Sessions\n";
	puts -nonewline "Session Ramp Distribution.Steady-State Seconds........$steady_duration\n";
	puts -nonewline "Session Ramp Distribution.Ramp Down Behavior..........Full Close\n";
	puts -nonewline "Session Ramp Distribution.Ramp Down Seconds...........$ramp_down_duration\n";
	puts -nonewline "Ramp Up Profile.Ramp Up Profile Type..................Stair Step\n";
	puts -nonewline "Ramp Up Profile.Minimum Connection Rate...............$min_cps_rate\n";
	puts -nonewline "Ramp Up Profile.Maximum Connection Rate...............$max_cps_rate\n";
	puts -nonewline "Ramp Up Profile.Increment N connections per second....$incr_cps_rate\n";
	puts -nonewline "Ramp Up Profile.Fixed time interval...................$max_cps_rate\n";
	puts -nonewline "Session Configuration.Maximum Simultaneous Sessions...$max_concurrent\n";
	puts -nonewline "Session Configuration.Maximum Sessions Per Second.....$max_cps_rate\n";
	puts -nonewline "Session.Configuration.Unlimited Session Close Rate....true\n";
	
	puts "--------------------------------------------------------------------------------------";
	puts "Running Final Iteration with Full Durations";
	puts "--------------------------------------------------------------------------------------\n";
	
	#########################################################
	# Calculate Parameters for Application Simulator Component
	#########################################################
	set min_cps_rate   [format %1.0f [expr $max_cps_rate / $ramp_up_duration]]
	set incr_cps_rate  [format %1.0f [expr $max_cps_rate / $ramp_up_duration]]
	set max_concurrent [format %1.0f [expr $max_cps_rate * .1]]
	
	$appsim configure \
	    -rampDist.up $ramp_up_duration \
	    -rampDist.steady $steady_duration \
	    -rampDist.down $ramp_down_duration \
	    -rampUpProfile.type "step" \
	    -rampUpProfile.min $min_cps_rate \
	    -rampUpProfile.max $max_cps_rate \
	    -rampUpProfile.increment $incr_cps_rate \
	    -rampUpProfile.interval 1 \
	    -sessions.max $max_concurrent \
	    -sessions.maxPerSecond $max_cps_rate \
	    -sessions.closeFast true \
	    -profile $bps_app_profile;
	
	set zero [format %3.0f 0]
	
	puts "Progress: $zero%\t    Execution Time (seconds): $zero\t    Max BW Rate Achieved: $zero";	
	
	## Run Test Here
	$test run -rtstats getStats;
	
	puts "--------------------------------------------------------------------------------------";
	puts "Progress: 100%\t    Compiling Test Results...COMPLETED.";
	puts "--------------------------------------------------------------------------------------\n";


	
    }
    
    
    puts "--------------------------------------------------------------------------------------";
    puts "Completed: Found CPS rate of $max_cps_rate creating a bandwidth of $max_bw";
    puts "--------------------------------------------------------------------------------------\n";
    
    $test save -force;
}










puts -nonewline "==========================================\n\n";
itcl::delete object $bps; unset bps;
#exit
########################################################
