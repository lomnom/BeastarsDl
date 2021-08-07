import requests
import re
from os import mkdir, remove
from datetime import datetime
from PIL import Image
from PyPDF2 import PdfFileMerger

def log(message): #define logging function to prevent repeated code
	currentTime = str(datetime.now().time())
	print("["+currentTime+"] "+message)

class BeastarsMangas:
	def __init__(self):
		self.chapterRegex=open("ChapterRegex.re",'r').read()
		self.url="https://w17.read-beastarsmanga.com/"
		self.subUrl="manga/beastars-chapter-{}/"
		self.get()

	def get(self):
		self.content=requests.get(self.url).text
		self.lastChapter=int(re.findall(self.chapterRegex,self.content)[0])

	class BeastarsManga:
		def __init__(self,link,chapter):
			self.finderRegex=open("GetLink.re",'r').read()
			self.chapter=chapter
			self.url=link
			self.get()

		def get(self):
			self.content=requests.get(self.url).text
			self.pages=re.findall(self.finderRegex,self.content)

		def downloadTo(self,dir):
			try:
				mkdir(dir)
			except OSError:
				pass

			merger = PdfFileMerger()
			for page in range(len(self.pages)):
				pagePage=requests.get(self.pages[page]).content
				jpgFile="{}/{}.jpg".format(dir,page)
				pdfFile="{}/{}.pdf".format(dir,page)
				open(jpgFile,'wb').write(pagePage)

				image=Image.open(jpgFile).convert('RGB')
				image.save(pdfFile)
				remove(jpgFile)

				merger.append(pdfFile)
				remove(pdfFile)

			merger.write("{}/chapter-{}.pdf".format(dir,self.chapter))
			merger.close()

	def manga(self,chapter):
		if chapter>self.lastChapter or chapter < 1:
			raise ValueError
		return self.BeastarsManga(self.url+(self.subUrl.format(chapter)),chapter)

log("getting BeastarsMangas object")
mangas=BeastarsMangas()

for chapter in range(1,mangas.lastChapter+1):
	log("getting BeastarsManga object for chapter {}".format(chapter))
	manga=mangas.manga(chapter)
	log("downloading manga...")
	manga.downloadTo("./chapters")