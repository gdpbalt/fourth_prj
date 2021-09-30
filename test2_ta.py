import urllib3
url = "https://www.facebook.com/hellomeets/events"

html = urllib3.urlopen(url).read()
print(html[:1024])
