import numpy as np

def group_consecutive_values(values, threshold=2):
    """
        raggruppa valori interi consecutivi crescenti in una lista (a distanza threshold).
        ad es.: [1,2,4,6] -> [[1,2],[4],[6]] con threshold = 1
                [1,2,4,6] -> [[1,2,4,6]] con threshold = 2
    """
    run = []
    result = [run]
    last = values[0]
    for v in values:
        if v-last <= threshold:
            run.append(v)
        else:
            run = [v]
            result.append(run)
        last = v
    return result


def merge_adjacent_split_points(split_points, black_pixels, threshold=2):
    """
        Laddove gli indici sotto la soglia siano consecutivi (e quindi troppo vicini),
        viene scelto solo uno fra i punti di segmentazione proposti: quello contenente
        il minor numero di pixel neri.
    """
    # raggruppo in liste gli indici consecutivi
    adj_split_points = group_consecutive_values(split_points, threshold)
    merged_split_points = []

    for split_point in adj_split_points:
        if len(split_point) > 0:
            # creo un array di coppie [indice della colonna, numero di pixel neri corrispondenti]
            min_interval = np.array(zip(split_point, black_pixels[split_point]))
            # scelgo l'indice di colonna che corrisponde al min(black_count) nell'intervallo (primo valore)
            min_split = np.argwhere(min_interval[:,1] == np.min(min_interval[:,1]))[0,0]
            merged_split_points.append(split_point[min_split])

    return np.array(merged_split_points)


#trova i minimi locali a partire da un array che contiene in posizione i-esima il numero di pixel neri che la linea in analisi contiene nella colonna i-esima
#(insomma, l'array che nel metodo precedente era definito come black_pixels_in_area)
def find_local_minima(black_pixels_per_column_in_line):
    """
        ritorna gli indici corrispondenti ai minimi locali in un'immagine
    """

    #array che contiene i minimi locali nella forma di coppie (coordinata x, numero di pixel neri)
    local_minima = []

    # un punto e' minimo locale se e' minore dei suoi punti adiacenti;
    # nello specifico, diciamo che deve essere minore strettamente almeno di uno dei due
    # (mentre puo' essere minore o uguale all'altro)

    local_minima.append(0)

    for i in range(1, len(black_pixels_per_column_in_line)-1):

        is_local_minimum =  ((black_pixels_per_column_in_line[i] <= black_pixels_per_column_in_line[i-1] and
                              black_pixels_per_column_in_line[i] < black_pixels_per_column_in_line[i+1]) or
                             (black_pixels_per_column_in_line[i] < black_pixels_per_column_in_line[i-1] and
                              black_pixels_per_column_in_line[i] <= black_pixels_per_column_in_line[i+1]))

        if is_local_minimum:
            local_minima.append(i)

    local_minima.append(len(black_pixels_per_column_in_line)-1)

    return np.array(local_minima)
