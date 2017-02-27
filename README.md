# haveIbeenHarvested
This should work with a default Kali install...

If you are not running this in Kali:

	*Ensure theHarvester is saved to either /usr/bin or /usr/share as "theharvester"
  
	*Ensure the python module ElementTree is installed



This script will run the harverster on a domain and submit results to the haveIbeenPwned API

Arguments:

-d [domain.com]				This will run the harvester on a domain then run the e-mails the harvester finds through the haveibeenpwned API

-df [domainFile.txt]			Accepts a list of domains separated newlines. 

-e [email@place.com]			This will return the results of haveibeenpwned API for a single e-mail

-ef [emailFile.txt]			Accepts a list of emails separated by newlines. 

-of [outputFile]			The results will be saved to specified outputFile as an HTML document.
					If -of is not specified the results will be saved to haveIbeenHarvested.html




At least one domain or email must be specified in order to run this script.

Example Uses:

haveIbeenHarvested.py -d domain.com -of results.html

	This will run the harvester on domain.com then run the e-mails the harvester finds through the haveibeenpwned API.
	The results will be saved to results.html
	
haveIbeenHarvested.py -df domains.txt -of results.html

	This is the same as before but instead of a single domain it will run the harvester on the domains specified in the file.
	The domains in this file need to be separated by a newline.

haveIbeenHarvested.py -ef emails.txt

	This will run the emails specified in this file through the haveibeenpwned API and save the results to haveIbeenHarvested.html
