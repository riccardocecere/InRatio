import numpy
from PIL import Image
from matplotlib import pyplot as plt
import ImagesManagment as im

def horizontalMaxs(a):
	"""
		metodo che data in ingresso un array 'a' riporti in uscita 
		le posizioni e i valori dei 2 elementi di 'a' che hanno valore
		massimo tra i massimi locali		
	"""
	max1, max2 = 0,0
	posMax1, posMax2 = 0,0
	for i in range(1,len(a)-1):
		if a[i]>a[i+1] and a[i]>a[i-1]:
			if a[i]>max1:
				max1 = a[i]
				posMax1 = i
	for i in range(1,len(a)-1):
		if a[i]>a[i+1] and a[i]>a[i-1]:		
			if a[i]>max2 and a[i]<max1:
				max2 = a[i]
				posMax2 = i
	#print posMax1, posMax2
	#plt.plot(a)
	#plt.plot(posMax1, max1, marker='o')
	#plt.plot(posMax2, max2, marker='o')
	#plt.show()
	return posMax1, max1, posMax2, max2

def reverse (matrix):
	"""
		metodo che inverte le righe della matrice in ingresso
	"""
	N = len(matrix)
	M = len(matrix[0])
	reverse=numpy.zeros(shape=(N,M),dtype=int)
	i=N-1
	for element in matrix:
		reverse[i]=element
		i-=1
	#print matrix.shape
	#print matrix
	#print '#############'
	#print reverse.shape
	#print reverse
	return reverse

def load_image(infilename):
	image=Image.open(infilename).convert('L')
	array_image=numpy.array(image)
	cutted_array_image = im.crop_white_space(array_image)
	right_size_array_image = im.add_white_padding(cutted_array_image)
	return right_size_array_image

def density_pixel(b):
	"""
		metodo che data in ingresso una matrice riporta in uscita un array i cui ogni elemento 
		iesimo corrisponde alla quantita di occorrenze uguali a zero (pixel neri) presenti 
		nella colonna iesima della matrie 
	"""
	s=numpy.array([])
	for i in range(0,len(b[0])):
		k=0
		for j in range(0,len(b)):
			if b[j][i]==0:
				k+=1
		s=numpy.append(s,k)
	return s

def top_distance(matrix):
	"""
		metodo che data in ingresso una matrice riporta in uscita un array i cui ogni elemento 
		iesimo corrisponde alla distanza in pixel, nella colonna iesima della matrice, tra
		il primo elemento della colonna e la prima occorrenza uguale a zero
		(distanza tra il primo pixel nero in alto e il margine superiore dell'immagine)
	"""
	top_distance=numpy.array([])
	M=len(matrix[0]) 
	N=len(matrix)
	for i in range(0,M):
		k=N
		for j in range(0,N):
			if matrix[j][i]==0:
				break
			else:
				k-=1
		if k>0:
			top_distance=numpy.append(top_distance,k)
	return top_distance

def bottom_distance(matrix):
	"""
		metodo che data in ingresso una matrice riporta in uscita un array i cui ogni elemento 
		iesimo corrisponde alla distanza in pixel, nella colonna iesima della matrice, tra
		l'ultimo elemento della colonna e la ultima occorrenza uguale a zero
		(distanza tra il primo pixel nero in basso e il margine inferiore dell'immagine)
	"""
	reversedMatrix=reverse(matrix)
	bottom_distance=numpy.array([])
	M=len(reversedMatrix[0])
	N=len(reversedMatrix)
	for i in range(0,M):
		for j in range(0,N):
			if reversedMatrix[j][i]==0:
				break 
		#if j>0:
		bottom_distance=numpy.append(bottom_distance,j)	
	return bottom_distance	

def image2Array(imgfile):
	"""
		metodo che data in ingresso un immagine riporta in uscita 4 array ognuno descritto nei vari metodi
		richiamati di seguito
	"""
	matrix=load_image(imgfile)
	density=density_pixel(matrix)
	horizontal=density_pixel(matrix.transpose())
	#plt.imshow(matrix)
	#plt.show()
	top=top_distance(matrix)
	bottom=bottom_distance(matrix)
	#plt.plot(density)
	#plt.show()
	#plt.plot(horizontal)
	#plt.plot(posBaseDown, baseDown, marker= 'o')
	#plt.plot(posBaseup, baseUp, marker= 'o')
	#plt.show()
	#plt.plot(top)
	#plt.plot(bottom)
	#plt.show()
	#print posBaseDown
	#print posBaseDown
	return density, top, bottom, horizontal

def main():
	image2Array("abbas(1).png")

if __name__=='__main__':
	main()