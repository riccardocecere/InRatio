import cv2
import numpy

def add_white_padding(img,width=260,height=100):
    """
        Aggiunge un bordo bianco in alto e a destra fino a raggiungere
        le width e height desiderate
    """
    top = max(0, height - img.shape[0])
    right = max(0, width - img.shape[1])
    return cv2.copyMakeBorder(img, top=top, bottom=0, left=0, right=right, borderType=cv2.BORDER_CONSTANT, value=255)

def crop_white_space(image, threshold=255):
    """
        rimuove lo spazio bianco eccedente, in alto, in basso, a dx e a sx.
        NB: funziona solo se l'immagine e' in grayscale
    """
    # una maschera di valori booleani. Ha la stessa struttura dell'immagine.
    # True se il pixel non e' bianco.
    img_mask = image < threshold
    # mask.any(1), mask.any(0) producono rispettivamente le maschere per righe e colonne:
    # True se la riga (o la colonna) contiene almeno un pixel nero.
    # sono monodimensionali.
    row_mask = img_mask.any(1)
    col_mask = img_mask.any(0)
    # np.ix_ costruisce gli indici che genereranno il prodotto fra le due maschere
    return image[numpy.ix_(row_mask, col_mask)]