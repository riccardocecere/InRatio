import image_utils as imgutil
import segmentation_utils as segmutil
import numpy as np
import os, cv2

ROOT_IMAGE_FOLDER = 'not_code/'
BINARIZED_PAGES_FOLDER = ROOT_IMAGE_FOLDER + 'img/pages_binarized/'
SAMPLES_ROOT_FOLDER = ROOT_IMAGE_FOLDER + 'datasets/2017-02-17/img/sources/training/'

def page_to_lines(filename):
    """
        Suddivide una pagina (ritagliata) in righe.
        input: il path completo all'immagine della pagina
        output: lista di coppie (immagine_riga, top_y_coordinate)
    """
    page = imgutil.open_grayscale_img(filename)
    black_px_per_row = imgutil.count_black_pixels_per_row(page)
    threshold = np.average(black_px_per_row)
    ixs = np.argwhere(black_px_per_row < threshold)
    ixs_grouped = segmutil.group_consecutive_values(ixs, threshold=7)

    min_ixs = [int(np.average(ixs)) for ixs in ixs_grouped]
    lines = []

    for i in range(0, len(min_ixs)-1):
        top_y = min_ixs[i]
        bottom_y = min_ixs[i+1]
        line = page[top_y:bottom_y]
        lines.append((line, top_y))

    return np.array(lines)

def line_to_words(line, top_y):
    """
        suddivide una linea di testo in parole.
        input: la linea e la sua posizione y
        output: una lista di triple (parola, top_y, left_x)
    """
    black_pixels = imgutil.count_black_pixels_per_column(line)
    space_ixs = imgutil.space_start_ixs(black_pixels, space_width=2)
    ixs_grouped = [0] + [min(ixs) for ixs in segmutil.group_consecutive_values(space_ixs)] + [line.shape[1]-1]
    words = []

    for i in range(0, len(ixs_grouped)-1):
        left_x = ixs_grouped[i]
        right_x = ixs_grouped[i+1]
        word = line[:,left_x:right_x]
        words.append((word, left_x, top_y))

    return np.array(words)

def _prune_cut_points(cut_points, min_margin=7):
    # pruning dei nodi troppo vicini alle estremita',
    # escludendo il primo e l'ultimo cut point
    to_prune = cut_points[1:len(cut_points)-1]
    pruning_filter = (to_prune>min_margin) & (to_prune<(cut_points[len(cut_points)-1] - min_margin))
    pruned = to_prune[pruning_filter]
    # ri-inserisco il primo e l'ultimo cut point nell'array filtrato
    pruned = np.insert(pruned, 0, cut_points[0])
    pruned = np.append(pruned, cut_points[len(cut_points)-1])

    if cut_points[0] != 0:
        pruned = np.insert(pruned, 0, 0)

    return pruned

def gen_nodes_edges(word, min_width=7, max_width=35):
    """
        input: word
        output: (cut_points, windows) aka nodi e archi
    """
    #NB DUPLICA il metodo _init_nodes ed _edges in word.Word (word.py) perche' l'oggetto
    #   Word va ripensato.
    nodes = []
    edges = []

    if (word.shape[0] > 0) and (word.shape[1] > 0):
        black_pixels = imgutil.count_black_pixels_per_column(word)
        loc_min_ixs = segmutil.find_local_minima(black_pixels)
        not_pruned = segmutil.merge_adjacent_split_points(loc_min_ixs, black_pixels)
        nodes = _prune_cut_points(not_pruned)

        for cut_point in nodes:
            offset_min = cut_point + min_width
            offset_max = cut_point + max_width
            segment = nodes[(nodes>offset_min) & (nodes<offset_max)]
            edges += zip([cut_point]*len(segment), segment)

    return nodes, edges

def crop_img(src_img, crop_start, crop_end, max_height=56):
    window = src_img[:,crop_start:crop_end]
    # occorre assicurarsi che la finestra non sia + alta di 56 px:
    if window.shape[0] > max_height:
        window = imgutil.crop_white_space(window)
        # NB l'eliminazione degli spazi bianchi potrebbe non bastare a ridurre l'immagine nel formato (56,34).
        # in questo caso la si scala.
        if window.shape[0] > max_height:
            window = cv2.resize(window, (window.shape[1], max_height))
    return window


def word_to_all_windows(word, left_x, top_y):
    """
        estrae tutte le finestre determinate dai cut point sui minimi locali in un intervallo.
        input: una parola e le sue coordinate
        output: una lista di tuple (segmento, absolute_left_x, absolute_top_y, width, height)
    """

    _, segments = gen_nodes_edges(word)

    all_windows = []
    for cut_start, cut_end in segments:
        absolute_left_x = left_x + cut_start
        all_window = word[:, cut_start:cut_end]
        width = all_window.shape[1]
        height = all_window.shape[0]
        all_windows.append((all_window, absolute_left_x, top_y, width, height))

    return all_windows

def word_to_cutp_windows(word, left_x, top_y):
    """
        estrae solo le finestre determinate dai cut point sui minimi locali.
        input: una parola e le sue coordinate
        output: una lista di tuple (segmento, absolute_left_x, absolute_top_y, width, height)
    """

    cut_points, _ = gen_nodes_edges(word)

    cut_points_windows = []
    for i in range(0, len(cut_points)-1):
        absolute_left_x = left_x + cut_points[i]
        cutp_window = word[:, cut_points[i]:cut_points[i+1]]
        width = cutp_window.shape[1]
        height = cutp_window.shape[0]
        cut_points_windows.append((cutp_window, absolute_left_x, top_y, width, height))

    return cut_points_windows

def save_many(windows, dest_path=SAMPLES_ROOT_FOLDER, date=''):
    for window, x, y, width, height, page in windows:
        dest_abs_path = dest_path+'RV12-'+date+'-'+page+'/'+page+'/all_windows/'

        if not os.path.isdir(dest_abs_path):
            os.makedirs(dest_abs_path)

        sample = imgutil.add_white_padding(window)
        name = '%d_%d_%d_%d.png' % (width, y, x, height)
        imgutil.write_image(sample, dest_abs_path+name)

def full_pipeline(pages, src_folder=BINARIZED_PAGES_FOLDER):
    pagenames = [src_folder + p + '.png' for p in pages]
    windows = []

    for pagename in pagenames:
        current_page = pagename.split('/')[len(pagename.split('/'))-1].split('.')[0]
        lines = page_to_lines(pagename)
        print 'lines:', len(lines)

        for line, top_y in lines:
            line = imgutil.clean_unconnected_noise(line, strength=0.015)
            words = line_to_words(line, top_y)
            #print 'words:', len(words)

            for word, left_x, top_y in words:
                all_windows = word_to_all_windows(word, left_x, top_y)

                for window, absolute_left_x, absolute_top_y, width, height in all_windows:
                    windows.append((window, absolute_left_x, absolute_top_y, width, height, current_page))

    print 'windows:', len(windows)
    return windows

def gen_webapp_folders(pages, src_folder=BINARIZED_PAGES_FOLDER, dest_folder='not_code/new_webapp/'):
    pagenames = [src_folder + p + '.png' for p in pages]

    for pagename in pagenames:
        current_page = pagename.split('/')[len(pagename.split('/'))-1].split('.')[0]
        if not os.path.isdir(dest_folder+current_page):
            os.mkdir(dest_folder+current_page)
        lines = page_to_lines(pagename)
        print 'lines:', len(lines)

        for line, top_y in lines:
            if not os.path.isdir(dest_folder+current_page+'/'+str(top_y)):
                os.mkdir(dest_folder+current_page+'/'+str(top_y))
            line = imgutil.clean_unconnected_noise(line, strength=0.015)
            words = line_to_words(line, top_y)

            for word, left_x, top_y in words:
                dest_all = dest_folder+current_page+'/'+str(top_y)+'/'+str(left_x)+'_'+str(top_y)+'/all_windows/'
                dest_cutp =  dest_folder+current_page+'/'+str(top_y)+'/'+str(left_x)+'_'+str(top_y)+'/cut_point_windows/'

                if not os.path.isdir(dest_all):
                    os.makedirs(dest_all)
                if not os.path.isdir(dest_cutp):
                    os.makedirs(dest_cutp)

                all_windows = word_to_all_windows(word, left_x, top_y)
                cut_point_windows = word_to_cutp_windows(word, left_x, top_y)

                for window, absolute_left_x, absolute_top_y, width, height in all_windows:
                    cv2.imwrite(dest_all+'%d_%d_%d_%d.png' % (absolute_left_x, absolute_top_y, width, height), window)

                for window, absolute_left_x, absolute_top_y, width, height in cut_point_windows:
                    cv2.imwrite(dest_cutp+'%d_%d_%d_%d.png' % (absolute_left_x, absolute_top_y, width, height), window)

def gen_words_from_page(pages, src_folder):
    pagenames = [src_folder + p + '.png' for p in pages]
    words = []

    for pagename in pagenames:
        current_page = pagename.split('/')[len(pagename.split('/'))-1].split('.')[0]
        lines = page_to_lines(pagename)
        print 'lines:', len(lines)

        for line, top_y in lines:
            line = imgutil.clean_unconnected_noise(line, strength=0.015)
            words_line = line_to_words(line, top_y)
            words += [word for word, x, y in words_line if word.shape[1]>0 and word.shape[0]>0]


    print 'words:', len(words)
    return words

if __name__ == '__main__':
    words = gen_words_from_page(['048r'], src_folder="pagine/")
    # print words
    # cv2.imwrite('', w)
    #for w in words:
    #    cv2.imshow('', cv2.resize(w, (0,0), fx=2.0, fy=2.0))
    #    cv2.waitKey(0)
    directory='C:\Users\Utente\Documents\Universita\Python\saves\imageWords\\'
    if not os.path.exists(os.path.dirname(directory)):
        try:
            os.makedirs(os.path.dirname(directory))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    os.chdir(directory)
    for nameNumber,image in enumerate(words):
        cv2.imwrite(str(nameNumber)+".png", image)
#cv2.imwrite() per salvare i file
#os.makedir() per creare le cartelle