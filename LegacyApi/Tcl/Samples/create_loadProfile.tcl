########################################################
#
#  Description: 
#  This script will create a custom Load Profile.
#  
#   
#  The user must set the parameters for the BPS host, username, 
#  password, and Load Profile parameters.
#
#  Usage:
#  1) Modify the parameters below
#  2) Start the BPS Tcl API
#  3) Enter 'source create_loadProfile.tcl' at the Tcl prompt
#
#  Example:
#  % source create_loadProfile.tcl
#
#  BreakingPoint Systems
#  10/25/2010
#
########################################################

#  Modify these parameters:

# Set the BPS IP address or host name
set bps_host "10.1.2.102"

# Set the BPS Username
set bps_username "admin"

# Set the BPS Password
set bps_password "admin"

# Set the BPS Load Profile Name
set loadprofile_name "Step_up5000"

# Set the Number of Phases to create (max 300)
set numPhases "300"

# Set the Maximum Sessions= startAt+amntIncrement 
set maxSessions "500+15" 

# Set the Sessions per Second= startAt+amntIncrement 
set SpS "500+15"

# Set the Interface Data Rate max
set IntRate "10000"

#Set the length (in sec) for each phase
set phaselen "1"
#
########################################################

puts -nonewline "\n=====================================================================\n\n";

# Clear BPS Tcl object
if {[info exists bps]} {itcl::delete object $bps; unset bps;}

# Connect to the BPS
puts -nonewline "=====================================================================\n\n";
puts -nonewline "Connecting to BreakingPoint Storm CTM: $bps_host..."
set bps [bps::connect $bps_host $bps_username $bps_password -onclose exit]
puts "COMPLETED.\n"


# Create a new load profile 
proc lp_create {lpName phases args } {
	global bps
	catch { $bps deleteLoadProfile -force $lpName } 
	set objName "::bps::BPSConnection::${bps}::$lpName"
	catch {itcl::delete object $objName}
	set lp [$bps createLoadProfile -name $lpName]
	for {set i 2 } { $i <= $phases } { incr i } {
		$lp addPhase $i
		puts -nonewline "$i.."
		}	
	
	for { set i 0 } { $i <= $phases } { incr i } {
		set cmdparams [list $lp modifyPhase $i]
		foreach {k v} $args {
			if { [regexp {^([^\+]+)\+(.*)} $v unused base increment] } {
				lappend cmdparams $k [expr $base + $increment * $i]
			} else {
				lappend cmdparams $k $v
			}
		}
		eval $cmdparams
	}

	if { [catch {$lp save -force} err ] } { puts "error saving: $err "}
	itcl::delete object $lp
}
puts -nonewline "Creating load profile...number of phases= $numPhases...might take a while so wait for completed message......"

if {$numPhases > 300} {puts -nonewline "select smaller number (<300) of phases and restart"}

lp_create $loadprofile_name $numPhases -sessions.max $maxSessions -sessions.maxPerSecond $SpS -rateDist.min $IntRate -duration $phaselen

puts -nonewline "COMPLETED.\n"


itcl::delete object $bps; unset bps;

########################################################
