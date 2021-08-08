import requests
import re
from os import mkdir, remove
from yaml import safe_load,dump
from datetime import datetime
from PIL import Image
from PyPDF2 import PdfFileMerger

def log(message): #define logging function to prevent repeated code
	currentTime = str(datetime.now().time())
	print("["+currentTime+"] "+message)

def textRange(textRange):
	ranges=textRange.split(",")
	for n in range(len(ranges)):
		ranges[n]=ranges[n].split("-")
		if len(ranges[n])==1:
			yield int(ranges[n][0])
		elif len(ranges[n])==2:
			for n in range(int(ranges[n][0]),int(ranges[n][1])+1):
				yield n

regexes=safe_load(open("Regexes.yaml","r").read())

class BeastarsMangas:
	def __init__(self):
		self.chapterRegex=regexes["getChapter"]
		self.url="https://w17.read-beastarsmanga.com/"
		self.subUrl="manga/beastars-chapter-{}/"
		self.get()

	def get(self):
		self.content=requests.get(self.url).text
		self.chapters=list(dict.fromkeys(re.findall(self.chapterRegex,self.content)))

class BeastarsManga:
	def __init__(self,link):
		self.finderRegex=regexes["getImage"]
		self.titleRegex=regexes["getTitle"]
		self.nameRegex=regexes["getChapterName"]
		self.url=link
		self.get()

	def get(self):
		self.content=requests.get(self.url).text
		self.pages=re.findall(self.finderRegex,self.content)
		self.chapter=re.findall(self.nameRegex,self.url)[0]
		if self.pages==[]:
			self.available=False #not translated
			return
		else:
			self.available=True

		try:
			self.title=re.findall(self.titleRegex,self.content)[0]
		except IndexError:
			log("could not find title of {}".format(self.chapter))
			self.title="Beastars Manga, Chapter {}".format(self.chapter.split("-")[-1])

	def downloadTo(self,dir):
		try:
			mkdir(dir)
		except OSError:
			pass

		merger = PdfFileMerger()
		for page in range(len(self.pages)):
			pagePage=requests.get(self.pages[page]).content
			jpgFile="{}/{}-{}.jpg".format(dir,self.chapter,page)
			pdfFile="{}/{}-{}.pdf".format(dir,self.chapter,page)
			open(jpgFile,'wb').write(pagePage)

			image=Image.open(jpgFile).convert('RGB')
			image.save(pdfFile)
			remove(jpgFile)

			merger.append(pdfFile)
			remove(pdfFile)

		merger.write("{}/{}.pdf".format(dir,self.title.replace(" ","_")))
		merger.close()

log("getting BeastarsMangas object")
mangas=BeastarsMangas()

nameRegex=regexes["getChapterName"]
for chapter in mangas.chapters:
	log("getting BeastarsManga object for chapter {}".format(re.findall(nameRegex,chapter)[0]))
	manga=BeastarsManga(chapter)

	if manga.available:
		log("downloading manga '{}'".format(manga.title))
		manga.downloadTo("./chapters")
	else:
		log("manga has not been translated yet!")