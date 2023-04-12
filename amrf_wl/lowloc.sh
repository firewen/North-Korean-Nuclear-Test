#!/bin/bash

saclst stla stlo f *.sac | while read one
do
	fnm=$(echo $one | awk '{print $1}')
	stla=$(echo $one | awk '{printf("%6.2f", $2)}')
	stlo=$(echo $one | awk '{printf("%6.2f", $3)}')

	echo $fnm $stla $stlo
sac << EOF
r $fnm
ch STLA $stla STLO $stlo
w over
quit
EOF

done
