import numpy
from PIL import Image
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from matplotlib.widgets import Button
import DTW
import os
import errno
import random
import cv2
import ImagesManagment as im

class Answer(object):
	answer=None

	def no(self, event):
		plt.close()
    		self.answer = 'n'

	def yes(self, event):
    		plt.close()
    		self.answer = 'y'

	def close(self, event):
    		plt.close()
   		self.answer = 'c'

def show(directory):
	image = Image.open(directory).convert('L')
	array_image = numpy.array(image)
	cutted_array_image = im.crop_white_space(array_image)
	right_size_array_image = im.add_white_padding(cutted_array_image)
	return right_size_array_image

def comparable(directory,file1,file2):
	os.chdir(directory)
	#se non sono lo stesso file o hanno lunghezze molto diverse
	image1 = Image.open(file1)
	array_image1=numpy.array(image1)
	image2 = Image.open(file2)
	array_image2=numpy.array(image2)
	cutted_image1 = im.crop_white_space(array_image1)
	cutted_image2 = im.crop_white_space(array_image2)
	paragonabili=True
	_, width1 = cutted_image1.shape
	_, width2 = cutted_image2.shape
	if image1==image2 or width1>3*width2/2 or width2>3*width1/2 or width1<25 or width2<25:
		paragonabili=False
	return paragonabili

def inizializeResultsTxt(directory):
	if not os.path.exists(os.path.dirname(directory)):
	    try:
	        os.makedirs(os.path.dirname(directory))
	    except OSError as exc: # Guard against race condition
	        if exc.errno != errno.EEXIST:
	            raise

def inizializePairsTxt(directory,directory1):
	#estrazione delle immagini dalla cartella repository
	files = [ii for ii in os.listdir(directory1)]
	#inizializzazione dell file che contiene la lista dei confronti da fare
	if not os.path.exists(os.path.dirname(directory)):
	    try:
	        os.mkdir(directory)
	    except OSError as exc: # Guard against race condition
	        if exc.errno != errno.EEXIST:
	            raise
	os.chdir(directory)
	with open("listOfPairs.txt", "a"):
		with open("listOfPairs.txt", "r") as file:
			if os.path.getsize("listOfPairs.txt")==0:
				lines=file.readlines()
				print 'Downloading...'
				for i in range (0,len(files)):
					for j in range(i,len(files)):
						if comparable(directory1,files[i],files[j]):
							lines.append(files[i]+"	"+files[j]+"\n")

				lines=random.sample(lines, len(lines))
				os.chdir(directory)
				with open("listOfPairs.txt", "w") as file:
					file.writelines(lines)

def applicationTest(directory,directory1,directory2,directory3):
	#se il file e' vuoto
	inizializePairsTxt(directory,directory1)
	inizializeResultsTxt(directory3)
	os.chdir(directory)
	with open("listOfResults.txt","a") as results:
		with open("listOfPairs.txt","r") as pairs:
			lines = pairs.readlines()
			print 'Welcome on Roma3s CrowdSourcing Platform!'
			print 'Questions to complete from the manuscript:	', len(lines)
			print 'Lets start with answering the following 10 questions....'
			for number, line in zip(range(0,50),lines):
				if line!="":
					image1=line.split()[0]
					image2=line.split()[1]
					answer=None
					fig, axes = plt.subplots()
					fig.suptitle('Are they the same word?(y/n)', fontsize=16)
					plt.subplot(2,1,1)
					plt.axis('off')
					ax1 = plt.imshow(show(directory1+image1),cmap=cm.Greys_r,aspect='auto',extent=(4,2,3,4))
					plt.subplot(2,1,2)
					plt.axis('off')
					ax2 = plt.imshow(show(directory1+image2),cmap=cm.Greys_r,aspect='auto',extent=(4,2,3,4))
					#plt.subplot(1,2,)
					plt.subplots_adjust(bottom=0.2)
					callback = Answer()
					axyes = plt.axes([0.7, 0.05, 0.1, 0.075])
					axno = plt.axes([0.81, 0.05, 0.1, 0.075])
					axclose = plt.axes([0.15, 0.05, 0.1, 0.075])
					bno = Button(axno, 'No',hovercolor='red')
					bno.on_clicked(callback.no)
					byes = Button(axyes, 'Yes',hovercolor='green')
					byes.on_clicked(callback.yes)
					bclose = Button(axclose, 'Close',hovercolor='yellow')
					bclose.on_clicked(callback.close)
					plt.show()
					answer = callback.answer
					if answer=='c':
						break
					lines[number]=""
					results.write(image1+"	"+image2+"	"+str(answer)+"\n")
	print 'Thanks for your attention!'
	print 'See you soon'+'\n'
	with open("listOfPairs.txt","w") as pairs:
		pairs.writelines(lines)
				

if __name__ == '__main__':
	cwd = os.getcwd()
	directory=cwd+'\saves'
	directory1=directory+'\imageWords\\'
	directory2=directory+'\listOfPairs.txt'
	directory3=directory+'\listOfResults.txt'
	applicationTest(directory, directory1, directory2, directory3)

"""
	taglia le pagine
	migliorare il training
	studiare il valore dei pesi

"""