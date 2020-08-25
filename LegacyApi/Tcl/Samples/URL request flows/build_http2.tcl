set var [bps::connect 10.10.10.23 admin admin];
set f [open "urls.txt"];
gets $f line;
for {set flowID 1} {$flowID <= 45} {incr flowID} { 
	set x [$var createSuperflow -name URL_$flowID]; 
	$x addHost {DNSserver} target DNSserver; #Make host DNS Server (1)
	$x addFlow dnsadv Client {DNSserver};	#Make flow DNS Server (1)
	set action 2;
	for {set foo 1} {$foo <= 11} {incr foo} { 
		$x addHost [expr $foo] target $line;
		$x addAction 1 client dns_resolve -domainname $foo;
		#$x modifyAction 1 -domainname $foo;
		$x addFlow httpadv Client [expr $foo]; 
		$x addAction $action client get_uri; 
		$x modifyFlow $action -to [expr $foo] -from Client -server-hostname $line; 
		$x addAction $action server response_ok; 
		gets $f line; 
		incr action; 
		puts "   little loop [expr $foo] out of 11";}
	$x save; 
	puts "BiG LOOP [expr $flowID] out of 45";}
