from matplotlib import pyplot


def figure(rows=1, cols=1, title=''):
    """
    Questo metodo prepara la finestra grafica, in cui andremo a stampare i grafici 
    richiesti. Per poter realizzare i subplots, la finestra grafica viene realizzata
    come una tabella
    - "rows" e' il numero di righe della finestra grafica
    - "columns" e' il numero di colonne della finestra grafica
    - "title" e' il titolo della finestra grafica, comune a tutti i grafici
    - "hold" e' un booleano, che indica la volonta' di sovraporre grafici tra loro
    """
    # TODO: probabilmente, hold non e' necessario come parametro (modifica la docstring)

    # Controllo dell'input
    # Rows
    if not isinstance(rows, (int, long)):
        raise TypeError('"rows" parameter must be a positive integer')
    if rows < 1:
        raise ValueError('"rows" parameter is not valid: its value must be an integer greater then 1')
    # Cols
    if not isinstance(cols, (int, long)):
        raise TypeError('"cols" parameter must be a positive integer')
    if cols < 1:
        raise ValueError('"cols" parameter is not valid: its value must be an integer greater then 1')
    # Title
    if not isinstance(title, basestring):
        raise TypeError('if specified, "title" parameter must be a string')

    # Creo i puntatori alla finestra ed i grafici interni
    fig, g = pyplot.subplots(rows, cols)
    # Imposto il titolo
    pyplot.suptitle(title)
    # Correzioni grafiche
    fig.tight_layout()
    fig.subplots_adjust(left=None, bottom=None, right=None, top=0.92, wspace=None, hspace=0.5)
    # pyplot.hold(hold)
    # Ritorno i puntatori
    return fig, g


def show():
    """
    Stampa a schermo la finestra grafica ed il suo contenuto
    """
    pyplot.show()


def plot(area, array, x_label, y_label, style='', legend_label='', missing=False):
    """
    Stampa a schermo un grafico:
    - "area" e' la porzione di finestra grafica da usare
    - "array" e' il vettore il cui contenuto viene usato come ordinate dei punti del grafico
    - "x_label" e' il nome dell'asse delle ascisse
    - "y_label" e' il nome dell'asse delle ordinate
    - "style" e' lo stile del grafico (colore, tratteggio.. ecc)
    - "legend_label" e' il titolo per la legenda
    - "missing" e' un valore booleano; se vero, stampa i valori mancanti per l'asse X come delle crocette
    """
    plot2(area, range(0, len(array)), array, x_label, y_label, style, legend_label, missing)


def plot2(area, array_x, array_y, x_label, y_label, style='', legend_label='', missing=False):
    """
    Stampa a schermo un grafico a gradini, a partire da due array
    - "area" e' la porzione di finestra grafica da usare
    - "array_x" e' il vettore il cui contenuto viene usato come ascisse dei punti del grafico
    - "array_y" e' il vettore il cui contenuto viene usato come ordinate dei punti del grafico
    - "x_label" e' il nome dell'asse delle ascisse
    - "y_label" e' il nome dell'asse delle ordinate
    - "style" e' lo stile del grafico (colore, tratteggio.. ecc)
    - "legend_label" e' il titolo per la legenda
    - "missing" e' un valore booleano; se vero, stampa i valori mancanti per l'asse X come delle crocette
    """
    try:
        # Preparo le coordinate dei punti
        area.plot(array_x, array_y, style, label=legend_label)
        if missing:
            missed = list(range(0, array_x[-1] + 1))
            for x in array_x:
                missed.remove(x)
            m = len(missed)
            if m > 0:
                area.plot(missed, [0] * m, 'rx')
        # Nomi degli assi cartesiani
        area.set_xlabel(x_label)
        area.set_ylabel(y_label)
        # Abbellimenti grafici
        area.title.set_fontsize(10)
        area.title.set_position((0.5, -0.2))
        # Legenda
        if legend_label != '':
            area.legend()
    except:
        print('An error occured. Impossible to print the requested graph')
        raise


def step_plot(area, array, x_label, y_label, legend_label='', style=''):
    """
    Stampa a schermo un grafico a gradini, a partire da un array
    - "area" e' la porzione di finestra grafica da usare
    - "array" e' il vettore il cui contenuto viene usato come ordinate dei punti del grafico
    - "x_label" e' il nome dell'asse delle ascisse
    - "y_label" e' il nome dell'asse delle ordinate
    - "legend_label" e' il titolo per la legenda
    - "style" e' lo stile del grafico (colore, tratteggio...), nel formato previsto da pyplot
    """
    step_plot2(area, range(0, len(array)), array, x_label, y_label, legend_label, style)


def step_plot2(area, array_x, array_y, x_label, y_label, legend_label='', style=''):
    """
    Stampa a schermo un grafico a gradini, a partire da due array
    - "area" e' la porzione di finestra grafica da usare
    - "array_x" e' il vettore il cui contenuto viene usato come ascisse dei punti del grafico
    - "array_y" e' il vettore il cui contenuto viene usato come ordinate dei punti del grafico
    - "x_label" e' il nome dell'asse delle ascisse
    - "y_label" e' il nome dell'asse delle ordinate
    - "legend_label" e' il titolo per la legenda
    - "style" e' lo stile del grafico (colore, tratteggio...), nel formato previsto da pyplot
    """
    try:
        # Preparo le coordinate dei punti
        area.step(array_x, array_y, style, where='post', label=legend_label)
        # Nomi degli assi cartesiani
        area.set_xlabel(x_label)
        area.set_ylabel(y_label)
        # Abbellimenti grafici
        area.title.set_fontsize(10)
        area.title.set_position((0.5, -0.2))
        # Legenda
        if legend_label != '':
            area.legend()
    except:
        print('An error occured. Impossible to print the requested graph')
        raise


def pdf_plot(area, array, x_label, legend_label='', bins=100):
    """
    Stampa a schermo il grafico per una PDF
    - "area" e' la porzione di finestra grafica da usare
    - "array" e' il vettore di partenza
    - "x_label" e' il titolo per l'asse delle ascisse
    - "legend_label" e' il titolo per la legenda
    - "bins" e' il numero di intervalli da usare per creare l'istogramma
    """
    try:
        # Creo l'istogramma
        area.hist(array, bins=bins, normed=True, label=legend_label)
        # Nomi degli assi cartesiani
        area.set_xlabel(x_label)
        area.set_ylabel('Density')
        # Legenda
        if legend_label != '':
            area.set_label(legend_label)
            area.legend()
    except:
        print('An error occured. Impossible to print the requested PDF graph')
        raise


def cdf_plot(area, array, x_label, y_label, legend_label='', bins=100):
    """
    Stampa a schermo il grafico per una CDF
    - "area" e' la porzione di finestra grafica da usare
    - "array" e' il vettore di partenza
    - "x_label" e' il titolo per l'asse delle ascisse
    - "y_label" e' il nome della variabile casuale, usato nel titolo dell'asse delle ordinate
    - "legend_label" e' il titolo per la legenda
    - "bins" e' il numero di intervalli da usare per creare l'istogramma
    """
    try:
        # Creo l'istogramma
        area.hist(array, bins=bins, normed=True, cumulative=True, label=legend_label)
        # Nomi degli assi cartesiani
        area.set_xlabel(x_label)
        area.set_ylabel('P(' + y_label + ' <= x)')
        # Range per l'asse delle ordinate
        area.set_ybound(0, 1)
        # Legenda
        if legend_label != '':
            area.set_label(legend_label)
            area.legend()
    except:
        print('An error occured. Impossible to print the requested CDF graph')
        raise


def bar(area, left_values, y_values, x_label, y_label, legend_label='', color='b', width=1.0):
    """
    La funzione stampa a schermo un grafico a barre
    - "area" e' la porzione di finestra grafica da usare
    - "left_values" e' il vettore di riferimento per l'ase x
    - "y_values" e' il vettore da stampare come altezza delle barre
    - "x_label" e' il titolo per l'asse delle ascisse
    - "y_label" e' il nome della variabile casuale, usato nel titolo dell'asse delle ordinate
    - "legend_label" e' il titolo per la legenda
    - "color" e' il colore da attribuire al grafico
    - "width" e' l'ampiezza delle barre
    """
    try:
        # Creo il grafico
        area.bar(left_values, y_values, width=width, label=legend_label, color=color)
        # Nomi degli assi cartesiani
        area.set_xlabel(x_label)
        area.set_ylabel(y_label)
        # Legenda
        area.legend()
    except:
        print('An error occured. Impossible to print the requested CDF graph')
        raise
