#this script will create a csv file containing all the strikes (with ID,names,reference, protocol, direction and path) for each canned BreakingPoint strike List 

itcl::body bps::BPSConnection::_strikeDict {xmlnode} {
  set ret {}
  dict set ret name [$xmlnode @name]
  if {[$xmlnode hasAttribute protocol]} {
    dict set ret protocol [$xmlnode @protocol]
  }
  if {[$xmlnode hasAttribute direction]} {
    dict set ret direction [$xmlnode @direction]
  }
  if {[$xmlnode hasAttribute id]} {
    dict set ret id [$xmlnode @id]
  }
  dict set ret category [[$xmlnode selectNodes category/child::node()] asXML]
  set descnode [$xmlnode selectNodes desc/child::*/child::node()]
  if {$descnode != ""} {
    dict set ret description [$descnode asXML]
  }

  set keywords {}
  foreach kw [$xmlnode selectNodes keyword] {
    lappend keywords [$kw @name]
  }
  dict set ret keywords $keywords

  set references {}
  foreach ref [$xmlnode selectNodes reference] {
    lappend references [list \
       type [$ref @type] \
       value [$ref @value] ]
  }
  dict set ret references $references
  return $ret
}

itcl::body bps::StrikeListClient::getStrikes {} {
	if {[getQuery] != ""} {
		set query [getQuery]
		set reply [$_bpsobj _execXml [subst {<searchStrikes limit="35000" offset="0" >
    <searchString>$query</searchString>
</searchStrikes> } ] ]
		dom parse $reply doc
		set root [$doc documentElement]
		set ret {}
		foreach sNode [$root selectNodes strike] {
			lappend ret [$sNode @path]
		}
		return $ret
	}
  set ret {}
  foreach item [$_xmlroot selectNodes \
      "list\[@id = 'attackPlan'\]/struct\[@id='Strikes'\]/list\[@id='strikes'\]/struct/param"] {
    lappend ret [[$item selectNodes child::node()] asText]
  }
  return $ret
}

set bps [bps::connect 10.1.1.61 tdever tdever10]


puts "retrieving the info for all strikes, please wait half a minute or 30 seconds "
set numOfStrikes 0
set strikeInfo {}
set offset 0
while { 1 } {
	set strikesInThisLoop 0
	foreach {strike strikeDesc } [$bps listStrikes -limit 1000 -offset $offset] {
		incr numOfStrikes
		dict set strikeInfo $strike $strikeDesc
		incr strikesInThisLoop
	}
	if { $strikesInThisLoop < 1000 } { break}
	incr offset $strikesInThisLoop
}
puts "$numOfStrikes strikes searched\n";

proc listStrikesForSL { strikeName } {
	global strikeInfo bps
	regsub {\/} $strikeName {_} fileName
	set fileName "strike_output/$fileName"
	append fileName ".csv"
	puts "creating $fileName"
	set fd [open "$fileName" w]
	set sl [$bps createStrikeList -template $strikeName]
	foreach strike [$sl getStrikes] {
		set name [dict get $strikeInfo $strike name]
		set reference "none"
		foreach reference [dict get $strikeInfo $strike references] { 
			set ref ""
			foreach {e f } $reference {
				if { $ref != "" } { append ref " " }
				append ref $f
			}
			set reference $ref
			break
		}
		set proto "n/a"
		if { [dict exist $strikeInfo $strike protocol] } {
			set proto [dict get $strikeInfo $strike protocol]
		}
		set direction "n/a"
		if { [dict exist $strikeInfo $strike direction] } {
			set direction [dict get $strikeInfo $strike direction]
		}
		set id "n/a"
		if { [dict exist $strikeInfo $strike id] } {
			set id [dict get $strikeInfo $strike id]
		}
		puts $fd "\"$id\",\"$name\",\"$reference\",\"$proto\",\"$direction\",$strike"
	}
	itcl::delete object $sl
	close $fd
}
#creating Strike Level 5
foreach e [$bps listAttackSeries -class canned] { 
	listStrikesForSL $e
}

