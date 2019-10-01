import requests, json
from lxml import html
from lxml.html.soupparser import fromstring

def query(keywords):
	end_point = 'https://www.canada.ca/en/sr/srb/sra.html?_charset_=UTF-8&fqocct=title_t&allq='+keywords # Restricted to matching all words (not exact phrase) in title
	response = requests.get(end_point)
	tree = html.fromstring(response.text)
	matches = tree.xpath("//article")

	results = []
	for match in matches:
		title = match.xpath(".//h3/a/text()")[0]
		url = match.xpath(".//p/span[@class='text-success']/text()")[0]
		date = match.xpath(".//p[2]/text()")[0]
		results.append([title, url, date])

	return results

def test():
	results = query("apricot cancer")
	for result in results:
		print result

if __name__ == '__main__':
	test()