#set bps [bps::connect 192.168.1.250 admin admin -checkversion false]
#source createVlanNetwork.tcl
#createVlanNetwork  VLAN4000 4000

set bps [bps::connect 10.205.4.222 admin admin]

proc createVlanNetwork { name {maxVLANs 5} {doDouble 0} } {
    
    global bps
    set n [$bps createNetwork]

    # Interface1 = port number
    $n add interface -id Interface1 -number 1 
    $n begin

    if { $doDouble == 1 } {
	puts "Creating objects for logical interface 1"
    }
    set prevCommit 0
    for { set i 1 } { $i <= $maxVLANs } { incr i } {
	puts $i
	set octet1 [expr $i / 254]
	set octet2 [expr $i % 254]
	incr octet2
	puts "\n--- octet2: $octet2 ; prevCommit: $prevCommit ; doDouble: $doDouble ---"
	$n add vlan -id vlan$i -default_container Interface1 -inner_vlan $i -mac_address 02:1a:c5:01:00:00
	$n add ip_static_hosts -id Range$i -default_container vlan$i -tags Interface1 -count 1 -ip_address  10.$octet1.$octet2.2 -netmask 8
	if { [expr $i - $prevCommit] > 200 } {
	    set prevCommit $i
	    $n commit
	    $n begin
	}
    }

    if { $doDouble == 1 } {
	puts "Creating objects for logical interface 2"
	$n commit
	$n add interface -id Interface2 -number 2
	$n begin
	set prevCommit 0
	for { set i 1 } { $i <= $maxVLANs } { incr i } {
	    puts $i
	    set octet1 [expr $i / 254]
	    set octet2 [expr $i % 254];     incr octet2
	    $n add vlan -id x_vlan$i -default_container Interface2 -inner_vlan $i -mac_address 04:1a:c5:01:00:00
	    set xx [expr $octet1 + 200]
	    $n add ip_static_hosts -id x_Range$i -default_container x_vlan$i -tags Interface2 -count 1 -ip_address  10.$xx.$octet2.2 -netmask 8
	    if { [expr $i - $prevCommit] > 200 } {
		set prevCommit $i
		$n commit
		$n begin
	    }
	}
    }
    $n commit
    $n save -name $name -force
    itcl::delete object $n
}

createVlanNetwork  VLAN1500 1500 1

puts "DONE."
exit

## Never works
## createVlanNetwork  VLAN4000 4000 1
## createVlanNetwork  VLAN2000 2000 1
## createVlanNetwork  VLAN1200 1200 1
## createVlanNetwork  VLAN1195 1195 1

## Sometimes works
## createVlanNetwork  VLAN1185 1185 1
## createVlanNetwork  VLAN1180 1180 1
## createVlanNetwork  VLAN1176 1176 1
## createVlanNetwork  VLAN1177 1177 1
## createVlanNetwork  VLAN1178 1178 1
## createVlanNetwork  VLAN1179 1179 1
## createVlanNetwork  VLAN1174 1174 1
## createVlanNetwork  VLAN1173 1173 1
## createVlanNetwork  VLAN1172 1172 1
## createVlanNetwork  VLAN1171 1171 1

## Always seems to work
## createVlanNetwork  VLAN1170 1170 1
## createVlanNetwork  VLAN1169 1169 1
## createVlanNetwork  VLAN1168 1168 1
## createVlanNetwork  VLAN1167 1167 1
## createVlanNetwork  VLAN1166 1166 1
## createVlanNetwork  VLAN1165 1165 1
## createVlanNetwork  VLAN1164 1164 1
## createVlanNetwork  VLAN1163 1163 1
## createVlanNetwork  VLAN1162 1162 1
## createVlanNetwork  VLAN1161 1161 1
