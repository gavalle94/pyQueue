import random
from qs_exceptions import *

AB_VALUES = {  # Possibili distribuzioni per la generazione dei tempi di arrivo/elaborazione
    'M': ['Exponential', ['rate']],
    'Chain': ['Chained queues', []],
    # TODO: In futuro, puoi implementare queste pdf
    'G': ['General', None],
    'GI': ['General and Independent', None],
    'Geom': ['Geometric', None],
    'En': ['Erlang-n', None],
    'Hn': ['Hyper-exponential', None],
    'D': ['Deterministic', None]
}
SCHEDULES = ['FIFO']  # Possibili discipline di scheduling della coda


def check_pdf(pdf, param_to_check='(generic_check)'):
    """
    Verifica che la pdf passata come parametro sia valida per la libreria
    """
    if pdf not in AB_VALUES.keys():
        raise PDF_Exception(param_to_check, pdf)


def get_pdf_params(pdf):
    """
    La funzione ritorna in output, come lista, i parametri richiesti dalla pdf di arrivi/elaborazione clienti
    per generare numeri casuali (secondo la pdf dichiarata).
    Questi parametri vengono prelevati come input utente, da tastiera
    """
    # Controllo di integrita' del parametro di input
    check_pdf(pdf)
    # A seconda del tipo di PDF, decido come procedere
    if pdf is 'M':
        # PDF esponenziale: vuole il rate come unico parametro
        print('Exponential PDF')
        while True:
            try:
                rate = float(input('Insert the rate: '))
                break
            except:
                print('\nIncorrect value: the rate must be a number')
        # Risultato: necessariamente sottoforma di vettore
        return [rate]
    if pdf is 'Chain':
        # La coda riceve in ingresso l'output di quella precedente, a cui e' direttamente colegata
        # Non e' una vera e propria pdf, pertanto non ho parametri
        return []

    # TODO: In futuro, puoi dare supporto anche per queste pdf
    if pdf is 'G':
        # pdf generica
        pass
    if pdf is 'GI':
        # pdf generica, con campioni indipendenti
        pass
    if pdf is 'Geom':
        # pdf geometrica
        pass
    if pdf is 'En':
        # pdf Erlang-n
        pass
    if pdf is 'Hn':
        # pdf iper-esponenziale
        pass
    if pdf is 'D':
        # pdf deterministica
        pass

    # In caso di errore, ritorno None
    return None


def pdf_random(pdf, params):
    """
    Genera un numero casuale, secondo la pdf indicata
    """
    # Controllo di integrita' dei parametri di input
    # PDF
    check_pdf(pdf)
    # Parametri della PDF
    if not isinstance(params, (list, tuple)):
        raise TypeError('"params" parameter is not valid. It must be an array')

    # Funzione usata per ricavare il numero di parametri richiesti dalla PDF
    def how_many_params(p):
        return len(AB_VALUES.get(p)[1])

    # Ricavo un'istanza come variabile casuale
    if pdf is 'M':
        # pdf esponenziale: vuole come unico parametro il rate (lambda, oppure mu)
        # Controllo il numero di parametri passati
        n_parameters = how_many_params(pdf)
        if len(params) != n_parameters:
            raise ValueError('"params" parameter is invalid. This tuple must contain %d values' & n_parameters)
        # Controllo che il rate sia valido
        rate = params[0]
        if not isinstance(rate, float):
            raise TypeError('the rate of the exponential pdf is invalid. It must be a real number')
        if rate <= 0:
            raise ValueError('the rate of the exponential pdf must be a real number greater than zero')
        # OK: creo un'istanza di variabile casuale esponenziale
        return int(random.expovariate(lambd=rate) + 0.5)
    if pdf is 'Chain':
        # La coda riceve in ingresso (immediatamente) l'output della coda precedente
        return 0

    # TODO: in futuro, puoi andare a definire anche queste pdf
    if pdf is 'G':
        # pdf generica
        pass
    if pdf is 'GI':
        # pdf generica, con campioni indipendenti
        pass
    if pdf is 'Geom':
        # pdf geometrica
        pass
    if pdf is 'En':
        # pdf Erlang-n
        pass
    if pdf is 'Hn':
        # pdf iper-esponenziale
        pass
    if pdf is 'D':
        # pdf deterministica
        pass

    # In caso di errore, ritorno None
    return None


def available_pdfs():
    """
    Elenco e spiegazione delle pdf implementabili per la coda
    """
    print('Available PDFs:')
    # Elenco delle pdf disponibili
    for pdf_short_name in AB_VALUES.keys():
        # Ricavo nome esteso ed array dei parametri dal dizionario
        pdf_long_name = AB_VALUES.get(pdf_short_name)[0]
        parameters_list = AB_VALUES.get(pdf_short_name)[1]
        # Se l'array vale None, salto la pdf in quanto ancora da implementare
        if parameters_list is None:
            continue
        # Se invece la pdf e' valida, allora ricavo l'elenco esteso dei parametri da questa richiesti
        if not (parameters_list == []):
            pdf_parameters = ''
            for par in parameters_list:
                if pdf_parameters is not '':
                    pdf_parameters += ', '
                pdf_parameters += '"%s"' % par
            pdf_parameters = 'requested parameters are ' + pdf_parameters
        else:
            pdf_parameters = 'no parameters are requested'
        # Ricavato l'elenco esteso, stampo le informazioni a schermo
        print('- "%s" (%s): %s' % (pdf_short_name, pdf_long_name, pdf_parameters))


def available_schedulings():
    """
    Elenco delle discipline di scheduling implementabili per la coda
    """
    print('Available scheduling policies:')
    for sp in SCHEDULES:
        # Stampo a schermo il nome (esteso)
        print('- %s' % sp)
