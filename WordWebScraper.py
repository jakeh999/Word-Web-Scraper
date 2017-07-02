import re
import sys
import platform
import os
from collections import Counter
import urllib.request
from urllib.parse import urlparse, urlunparse
from urllib.parse import urlsplit
from urllib.parse import urljoin
from nltk.tokenize import word_tokenize
from timeit import default_timer as timer
import datetime


def write(s):
	sys.stdout.write(s)
	sys.stdout.flush()

def clear():
	if platform.system() == "Windows":
		os.system("cls")
	else:
		os.system("clear")

class JakeParser:
	__count = Counter()
	__isWritten = False
	__urls = []
	__host = None
	__recursiveCount = 0
	__urlQueue = []
	__badExtensions = [".css", ".js", ".jpg", ".png", ".gif", ".mov", ".mp4", ".swf", ".json", ".xml", ".pdf",
							".xls", ".doc", ".ppt", ".pptx", ".xlsx", ".pptx", ".mp3", ".aac", ".docx"]
	__reFindLinks = re.compile(r'href="(.*?)"')
	__reFindExtension = re.compile(r"\.[^.]*$")
	__reGetBody = re.compile(r"<body[^>]*>((.|[\n\r])*)<\/body>")
	__reTagRemove = re.compile(r"<.*?>")
	__reJSRemove = re.compile(r"<script.*?>.*?</script>", re.DOTALL)
	__reCSSRemove = re.compile(r"<style.*?>.*?</style>", re.DOTALL)
	__reIndexCheck = re.compile(r"(.*?)/(index\.(?!.*/))")

	def __init__(self, url):
		if str(url).split() is False:
			raise ValueError("URL and word must be supplied!")
		if not re.match(r'^[a-zA-Z]+://', url):
			raise ValueError("Not a valid URL!")
		url = self.url_path_format(url)
		self.__host = self.get_host(url)
		print(url)
		print(self.__host)
		self.__urls.append(url)
		self.__get_page(url)
		while len(self.__urlQueue) > 0:
			self.__get_page(self.__urlQueue.pop())

	def url_path_format(self, url):
		urlp = urlparse(url)
		if urlp.path == "":
			url = urlunparse(urlp) + "/"
		return url

	def get_counter(self):
		return self.__count

	def get_host(self, url):
		return urlsplit(url).netloc

	def get_urls(self):
		return self.__urls

	def __get_page(self, url):
		print(str(datetime.datetime.now()) + " - Processing " + url + "...")
		website = urllib.request.Request(url)
		webopen = urllib.request.urlopen(website)
		url = webopen.geturl()
		resp = str(webopen.read(), "utf-8")
		body = str(self.__reGetBody.findall(resp)[0][0])
		body = body.replace("\n", " ").replace("\t", " ")
		body = self.__reJSRemove.sub("", body)
		body = self.__reCSSRemove.sub("", body)
		links = self.__reFindLinks.findall(body)
		body = self.__reTagRemove.sub("", body)
		body = word_tokenize(body)
		self.__count += Counter(body)
		if (len(links) + self.__recursiveCount) > 997:
			write("adding to queue...\n")
			self.__urlQueue += links
		else:
			for link in links:
				# print(link)
				link = urljoin(url, link)
				link = re.sub(r"#.*", "", link)
				link = self.url_path_format(link)
				# print(urlparse(link))
				if self.get_host(link) == self.__host:
					# print("We add this link!")
					if link not in self.__urls:
						# print("This one hasn't been processed yet!")
						ext = str(os.path.splitext(urlparse(link).path)[1])
						# print(ext)
						if ext not in self.__badExtensions:
							# print("This one has a good extension!")
							self.__urls.append(link)
							try:
								self.__recursiveCount += 1
								self.__get_page(link)
							except Exception as e:
								print(str(e) + " - Probably not a normal web page")
								pass
							self.__recursiveCount -= 1
		return


def main():
	while True:
		url = input("Enter URL: ")
		# url = "http://192.168.0.10/wordpress/"
		try:
			tmr = timer()
			jp1 = JakeParser(url)
			tmr = timer() - tmr
		except Exception as e:
			print(e)
		try:
			print("Outputting file...")
			fname = "SiteWordCounter - " + jp1.get_host(url) + " - " + str(datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")) + ".txt"
			f = open(fname, "wb")
			f.write(bytes("Site Word Counts\r\n-------------\r\n\r\n", "utf-8"))
			for count in jp1.get_counter().most_common():
				f.write(bytes(str(count[0]) + " : " + str(count[1]) + "\r\n", "utf-8"))
			f.write(bytes("\r\nSum: " + str(sum(jp1.get_counter().values())), "utf-8"))
			f.write(bytes("\r\n\r\nSite URL List\r\n-------------\r\n\r\n", "utf-8"))
			for url in jp1.get_urls():
				f.write(bytes(url + "\r\n", "utf-8"))
			f.close()
			f = None
			print("\nDONE! Wrote " + str(len(jp1.get_urls())) + " URL(s) to \"" + fname + "\" in " + str(round(tmr, 2)) + " seconds.")
			print(" ")
			jp1 = None
		except Exception as e:
			print(e)
		if input("Run a new search? (y/n): ").lower() != "y":
			break


if __name__ == "__main__":
	main()
