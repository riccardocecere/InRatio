import cv2
import numpy as np

def open_grayscale_img(filename, crop=False):
    if crop:
        return crop_white_space(cv2.imread(filename, cv2.IMREAD_GRAYSCALE))
    return cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

def open_sample(filename):
    return add_white_padding_center(cv2.imread(filename, cv2.IMREAD_GRAYSCALE))

def open_many_samples(filenames):
    samples_images = []

    for filename in filenames:
        samples_images.append(open_sample(filename))

    return np.array(samples_images)

def open_many_samples_center(filenames):
    samples_images = []

    for filename in filenames:
        samples_images.append(add_white_padding_center(open_grayscale_img(filename, crop=True)))

    return np.array(samples_images)

def write_image(image, filename):
    cv2.imwrite(filename, image)

def extract_sample_from_coordinates(page, coordinates, clean=True):
    if isinstance(page, str):
        page = open_grayscale_img(page)

    x, y, w, h = coordinates

    crop = page[y:y+h, x:x+w]
    if clean:
        crop = clean_unconnected_noise(crop)
        black_pixels = count_black_pixels_per_column(crop)
        white_space_ixs = space_start_ixs(black_pixels)
        # rimozione dello spazio in eccesso
        for space_start in white_space_ixs:
            if(space_start > crop.shape[1]/3):
                crop = crop[:,:space_start]
        if(np.any(crop == 0)):
            crop = crop_white_space(crop)

    return crop

def count_black_pixels(image):
    return (image.shape[0]*image.shape[1]) - cv2.countNonZero(image)

def clean_unconnected_noise(image, strength=0.3):
    # copia dell'immagine, invertita per trovare i contorni
    image = cv2.copyMakeBorder(image, top=1, bottom=1, left=1, right=1, borderType=cv2.BORDER_CONSTANT, value=255)
    image_copy = cv2.bitwise_not(image.copy())

    # cv2.imshow('segment', image_copy)
    # cv2.waitKey(0)

    _, contours, hierarchy = cv2.findContours(image_copy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        max_area = max([cv2.contourArea(c) for c in contours])
        threshold = max_area*strength

        for cnt in contours:
            if (cv2.contourArea(cnt) < threshold):
                cv2.fillPoly(image, [cnt], (255,255,255))
    # cv2.imshow('segment', cv2.resize(image, (0,0), fx=4.0,fy=4.0))
    # cv2.waitKey(0)
    return image

def space_start_ixs(black_pixels, space_width=3, tolerance=0):
    """
        ritorna una lista di indici in corrispondenza dei quali
        c'e uno spazio <= a tolerance di dimensione space_width
    """
    ixs = []
    for i in range(0, len(black_pixels)-space_width):
        sub_array = np.array(black_pixels[i:i+space_width])
        if np.all(sub_array <= tolerance):
            ixs.append(i)
    return ixs


def character_height(segment, top_baseline, bottom_baseline):
    upper_half = segment[:top_baseline]
    lower_half = segment[bottom_baseline:]

    upper_elements = upper_half.shape[0]*upper_half.shape[1]
    lower_elements = lower_half.shape[0]*lower_half.shape[1]

    if (cv2.countNonZero(upper_half) < upper_elements) and (cv2.countNonZero(lower_half) == lower_elements):
        return 'high'
    if (cv2.countNonZero(upper_half) == upper_elements) and (cv2.countNonZero(lower_half) < lower_elements):
        return 'low'
    if (cv2.countNonZero(upper_half) == upper_elements) and (cv2.countNonZero(lower_half) == lower_elements):
        return 'mid'

def find_baseline(image, margin=5, min_line_height=10):
    """
        trova i limiti superiori e inferiori dei caratteri mediani.
        margin determina la tolleranza rispetto al valore trovato,
        min_line_height la distanza minima fra un picco e l'altro.
    """
    black_count = count_black_pixels_per_row(image)
    max_1st_ix = np.argmax(black_count) # prima baseline
    # ora occorre stabilire se la successiva baseline si trova al di sopra o al di sotto di essa:
    # considero le righe al di sopra e al di sotto della prima baseline con un margine
    # pari a min_line_height (controllando di non eccedere la dimensione dell'immagine)
    start = (max_1st_ix + min_line_height)
    end = (max_1st_ix - min_line_height)
    if end < 1:
        end = 1
    if start > image.shape[0]-1:
        start = image.shape[0]-1

    upper_half = black_count[:end]
    lower_half = black_count[start:]
    # considero i valori massimi per questi sottoinsiemi
    upper_max_ix = np.argmax(upper_half)
    lower_max_ix = np.argmax(lower_half) + (len(black_count)-len(lower_half))

    max_2nd_ix = lower_max_ix # seconda baseline
    # scelgo l'indice della colonna con piu' pixel neri
    if black_count[upper_max_ix] > black_count[lower_max_ix]:
        max_2nd_ix = upper_max_ix

    # l'indice con valore piu' basso sara' la baseline piu' alta, e viceversa
    upper_bound, lower_bound = sorted((max_1st_ix, max_2nd_ix))

    result = [upper_bound-5, lower_bound+5]
    if result[0] < 0:
        result[0] = 0
    if result[1] > image.shape[0]-1:
        result[1] = image.shape[0]-1
    return result

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
    return image[np.ix_(row_mask, col_mask)]

def add_white_padding(img,width=34,height=56):
    #inizially was (widthxheight)=34x56
    """
        Aggiunge un bordo bianco in alto e a destra fino a raggiungere
        le width e height desiderate
    """
    top = max(0, height - img.shape[0])
    right = max(0, width - img.shape[1])
    return cv2.copyMakeBorder(img, top=top, bottom=0, left=0, right=right, borderType=cv2.BORDER_CONSTANT, value=255)

def add_white_padding_center(img, width=34, height=56):
    """
        Aggiunge una cornice bianca attorno all'immagine
        fino a raggiungere le width e height desiderate
    """
    vertical_border = max(0, height - img.shape[0])
    horizontal_border = max(0, width - img.shape[1])
    top = vertical_border/2
    bottom = vertical_border - top
    left = horizontal_border/2
    right = horizontal_border - left
    return cv2.copyMakeBorder(img, top=top, bottom=bottom, left=left, right=right, borderType=cv2.BORDER_CONSTANT, value=255)

def count_black_pixels_per_column(image):
    """
        conta i pixel neri di ciascuna colonna dell'immagine.
        ritorna un array 1D contenente i valori di nero in ordine:
        a[0] corrisponde al conteggio di pixel neri della prima colonna da sx.
    """
    black_counts = []
    for i in np.arange(image.shape[1]):
        # pixel totali - pixel diversi da 0 (= neri)
        black_pixels = len(image[:,i]) - cv2.countNonZero(image[:,i])
        black_counts.append(black_pixels)

    return np.array(black_counts)

def count_black_pixels_per_row(image):
    """
        conta i pixel neri di ciascuna riga dell'immagine.
        ritorna un array 1D contenente i valori di nero in ordine:
        a[0] corrisponde al conteggio di pixel neri della prima riga dall'alto.
    """
    black_counts = []
    for row in image:
        black_pixels = len(row) - cv2.countNonZero(row)
        black_counts.append(black_pixels)

    return np.array(black_counts)
