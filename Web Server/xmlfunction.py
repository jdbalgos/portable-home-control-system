#import bs4 as bs

def registerUsertoXML():
	xml = open("/var/www/FlaskApp/FlaskApp/templates/configs/users.xml","r")
	lines = xml.readlines()
	xml.close()
	return lines
