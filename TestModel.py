import machineLearningDTW
import os


if __name__=='__main__':
	cwd=os.getcwd()
	directory_images=cwd+'\saves\imageWords'
	os.chdir(cwd+'\saves')
	with open("testTheModel.txt", "r") as file:
		lines=file.readlines()
		for line in lines:
			if line!="":
				words=line.split()
				prediction ,vector = machineLearningDTW.predict_result(directory_images+'\\'+words[0], directory_images+'\\'+words[1])
				print words[0], words[1], words[2], 'prediction =',prediction, vector
