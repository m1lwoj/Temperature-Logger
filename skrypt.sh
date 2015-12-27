#!/bin/bash

rm .tempdata

for i in {1..100}
do
	./Adafruit_DHT 11 4 >> .tempdata
	sleep 1
done

TEMPERATURE=`cat .tempdata | grep "Temp" | awk -F " " '{print $3}' | head -n 1`

if [ ! -z "$TEMPERATURE" -a "$TEMPERATURE" != " " ]; then
	sudo sqlite3 /var/www/templog.db "insert into temperature (timestamp, value) values (CURRENT_TIMESTAMP, '$TEMPERATURE');"

	MINMAX=`sudo sqlite3 /var/www/templog.db "select * from configuration limit 1"`

	MIN=`echo $MINMAX | awk '{split($0,a,"|"); print a[1]}'`
	MAX=`echo $MINMAX | awk '{split($0,a,"|"); print a[2]}'`
	
	echo "From: limoand2@gmail.com" > EmailMessage.txt
	echo "To: m1l@g.pl" >> EmailMessage.txt
	echo "Subject: Temperature alert" >> EmailMessage.txt
	echo " " >> EmailMessage.txt
	
	if [ $((TEMPERATURE - $MIN)) -lt 0 ]
        	then
        	echo "ALARM temperature is below " $MIN >> EmailMessage.txt
		ssmtp m1l@g.pl < EmailMessage.txt
	fi

	if [ $((TEMPERATURE - $MAX)) -gt 0 ]
        	then
        	echo "ALARM temperature is above " $MAX >> EmailMessage.txt
		ssmtp m1l@g.pl < EmailMessage.txt	
	fi
else
        echo "error - temperature not found" >> .tempdata
fi


