#!/usr/bin/env python
# Written by: Brian Berg - Xexzy
# Special thanks to Troy Hunt for the API and to everyone that's worked on the theharvester over the years

import requests,time,json
import xml.etree.ElementTree as ET
import subprocess
import os
from sys import argv
from xml.etree.ElementTree import Element, Comment, SubElement, tostring 	#writing xlm	
from xml.dom import minidom								#prettyup xml

def getPwned(email):
	ran = False
	results = {}
	while ran == False:
		r = requests.get("https://haveibeenpwned.com/api/v2/breachedaccount/"+email, headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.0) Gecko/20100101 Firefox/51.0"})
		
		if r.status_code == 200:
			ran = True
			response = r.text
			response = json.loads(response)
			print "\nWe might have somethin juicy..."
			print email,"appears to have been compromised on the following sites"
			for breach in response:
				references = []
				print "\nTitle:",breach['Title']
				print "Domain:",breach['Domain']
				print "Type of info in breach:", ", ".join(breach['DataClasses'])
				print "Date of breach:",breach['BreachDate']
				print "Date of disclosure:",breach['AddedDate']
				if "<a href=" in breach['Description']:
					tmp = breach['Description'].split("<a href=\"")
					for link in tmp:
						if "http" in link:
							references.append(link.split("\"")[0])
					print "References:", ", ".join(references)
				results[breach['Title'].encode('utf8')] = {'Domain':breach['Domain'].encode('utf8'), 'DataClass':breach['DataClasses'],'DoB':breach['BreachDate'],'DoD':breach['AddedDate'],'References':references}
			print "#"*30+"\n"
			
		elif r.status_code == 404:
			ran = True
			results = "has not been pwned"
			print email,results,"\nGood for them"
			print "#"*30+"\n"
		
		elif r.status_code == 429:
			print "Too many requests...taking a quick 5 then trying again"
			time.sleep(2)
			
	time.sleep(1.59) #the hibp API requires a 1.5 sec delay
	return results

def harvest(domain):
	domain = domain.replace("https://", "").replace("http://", "").replace("www.", "")
	outFile = "harvestResults_"+domain
	print domain,"will be harvested"
	print "Harvester results will be saved to",outFile
	try:
		harvester = subprocess.check_call("theharvester -d %s -b all -l 300 -f %s" %(domain, outFile), shell=True)
	except:
		print("Unable to perform the harvester on",domain)
		exit()
	return outFile

def parseHarvest(outfile):
	outfile = outfile.strip(".com")
	outfile = outfile+".xml"
	print "parsing",outfile
	tree = ET.parse(outfile)
	root = tree.getroot()
	emails = []
	for email in root.findall('email'):
		print email.text
		if email.text not in " ".join(emails):
			emails.append(email.text)
	return emails


def prettify(elem):									
	rough_string = ET.tostring(elem, 'utf-8')
	reparsed = minidom.parseString(rough_string)
	return reparsed.toprettyxml(indent="    ")

def writeXML(totes, outfile):
	top = Element("PwnList")
	for email in totes.keys():
		if "has not been pwned" not in totes[email]:
			emailNode = SubElement(top,'email',{'address':email})
			for title in totes[email].keys():
				titleNode = SubElement(emailNode,"breach",{"title":title,"domain":totes[email][title]['Domain'],"DateOfBreach":totes[email][title]['DoB'],"DateOfDisclosure":totes[email][title]['DoD']})
				infoNode = SubElement(titleNode,"info")
				for info in totes[email][title]['DataClass']:
					infoNode = SubElement(titleNode,"info")
					infoNode.text = info
				
				referenceNode = SubElement(titleNode,"references")
				for reference in totes[email][title]['References']:
					referenceNode = SubElement(titleNode,"references")
					referenceNode.text = reference
				
	print "Saving XML results to",outfile			
	with open(outfile,'w') as of:
		of.write(prettify(top))


def writeHTML(totes,output):
	outfile = output
	with open(outfile,'w') as of:
		of.write("""<!DOCTYPE html>
	<html>
	<head>
	  <title>Pwned</title>
	</head>""")
		of.write("<body><H2>The Following have been pwned:</H2><br>")
		for email in totes.keys():
			if "has not been pwned" not in totes[email]:
				of.write("<H3>"+email+"</H3>")
				for title in totes[email].keys():
					of.write(title+":"+"<br>")
					of.write("<ul>")
					of.write("<li>Domain: "+totes[email][title]['Domain']+"</li>")
					of.write("<li>Date of Breach: "+totes[email][title]['DoB']+"</li>")
					of.write("<li>Date of Disclosure: "+totes[email][title]['DoD']+"</li>")
					of.write("<li>Info in breach:</li>")
					of.write("<ul>")
					for info in totes[email][title]['DataClass']:
					     of.write("<li>"+info+"</li>")
					of.write("</ul>")
					of.write("<li>References:</li>")
					if len(totes[email][title]['References']) > 0:
						of.write("<ul>")
						for reference in totes[email][title]['References']:
							of.write("<li><a href="+reference+">"+reference+"</a></li>")
						of.write("</ul>")
					of.write("</ul>")	
	
		of.write("</body></html>")
		
	print "Saving results to",outfile
		
if __name__ == '__main__':
	domains = []	#list of domains
	emails = []	#list of emails
	totes = {}	#dictionary of results
	output = "haveIbeenHarvested.html"
	tamper = []
	if os.path.isfile("/usr/bin/theharvester") != True and os.path.isfile("/usr/share/theharvester") != True:
		print "\"theharvester\" must be in your either /usr/bin or /usr/share"
		exit()
	
	for i in range(0, len(argv)):
		if argv[i] == "-d":
			domain = argv[i+1]
			domains = [domain.strip()]
			
		if argv[i] == "-df":
			if os.path.isfile(argv[i+1]):
				dfile = argv[i+1]
				with open(dfile,"r") as domainFile:
					for tmpDomain in domainFile:
						if tmpDomain.strip().lower() not in " ".join(domains):
							domains.append(tmpDomain.strip().lower())
			else:
				print "The specified domain list does not exist"
				exit()
		
		if argv[i] == "-e":
			emails = argv[i+1]
			emails = [emails.strip()]
			
		if argv[i] == "-of":
			if argv[i+1].split(".")[-1] == "html":
				output = argv[i+1]
			else:
				output = argv[i+1]+".html"
			
		if argv[i] == "-ef":
			if os.path.isfile(argv[i+1]):
				efile = argv[i+1]
				with open(efile,"r") as emailFile:
					for tmpEmail in emailFile:
						if tmpEmail.strip().lower() not in " ".join(emails):
							emails.append(tmpEmail.strip().lower())
			else:
				print "The specified email list does not exist"
				exit()
				
		if "--tamper" in argv[i]:
			tamper_domains = argv[i+1]
			tamper_domains = tamper_domains.split(",")
			for tdomain in tamper_domains:
				if tdomain not in tamper:
					tamper.append(tdomain)
				
		if argv[i] == "-h":
			print """
Arguments:
-d [domain.com]				This will run the harvester on a domain then run the e-mails the harvester finds through the haveibeenpwned API

-df [domainFile.txt]			[emailFile.txt] is a file of emails that are separated by a newline. 

-e [email@place.com]			This will return the results of haveibeenpwned API for a single e-mail

-ef [emailFile.txt]			[emailFile.txt] is a file of emails that are separated by a newline. 

-of [outputFile]			The results will be saved to specified outputFile as an HTML document.
					If -of is not specified the results will be saved to haveIbeenHarvested.html

--tamper [domain1.com,domain2.com,..]		This will modify and add email addresses to contain


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
	
haveIbeenHarvested.py -e test@place.com --tamper domain1.com,domain2.com,gmail.com
	This will run the test@place.com, test@domain1.com, test@domain2.com, and test@gmail.com through the HaveIbeenPwned API and save the results to haveIbeenHarvested.html
"""
	
			exit()
			
	if domains == [] and emails == []:
		print "Please specifiy at least a domain (-d) or an e-mail (-e). Use -h to see more options"
		exit()
			
	
	if domains != []:
		for domain in domains:
			outfile = harvest(domain)
			harvestMails = parseHarvest(outfile)
			
			for tmpEmail in harvestMails:
				if tmpEmail not in " ".join(emails):
					emails.append(tmpEmail)
					
		for email in emails:
			totes[email] = getPwned(email)
			for tDomain in tamper:
				tamperedEmail = email.split("@")[0]+"@"+tDomain
				totes[tamperedEmail] = getPwned(tamperedEmail)
			
	else:
		for email in emails:
			totes[email] = getPwned(email)		
			for tDomain in tamper:
				tamperedEmail = email.split("@")[0]+"@"+tDomain
				totes[tamperedEmail] = getPwned(tamperedEmail)
	
	writeHTML(totes,output)
	output = output.replace(".html",".xml")
	writeXML(totes,output)
	
