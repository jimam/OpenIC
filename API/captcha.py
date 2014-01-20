import urllib2
def captcha(data_string):
	xml = urllib2.urlopen("http://api.wolframalpha.com/v2/query?input=captcha+%s&appid=%s"%(data_string.replace(' ', "+"), "H6PUWK-XWR9P6A3HK"))
	return "<img src='" + xml.read().split("<img src='")[-1].split("'\n")[0]+" width='298' height='54' />"

