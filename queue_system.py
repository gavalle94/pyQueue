import simpy
import qs_stats
from qs_utilities import *
import input_controls as ic

# Costanti di utility per la libreria
INF = simpy.core.Infinity


class QueueSystem(object):
    """
    La classe modellizza il sistema coda (Queue), utilizzando la notazione di Kendall per la sua descrizione
    """

    # TODO: in futuro, si possono implementare priorita' di QL e servers
    def __init__(self, arrivals='M', services='M', servers=1, capacity=INF, population=INF, schedule_policy='FIFO',
                 batches=1, log_file=None, service_callback=None, callback_params=None):
        """
        I parametri di input sono:
        - "env": l'ambiente di simulazione simpy
        - da "arrivals" a "schedulePolicy": quelli richiesti dalla notazione di Kendall (da 'A' ad 'f')
        - "batches": serve a stabilire, di volta in volta, il numero di richieste che arrivano al
            sistema in contemporanea (modellizzato come variabile casuale con pdf uniforme). Questo 
            parametro puo' essere un numero intero "b", oppure una tupla "(a, b)": nel primo caso 
            il valore di batch viene calcolato come U(1, b), mentre nel secondo come U(a, b)
        - "log": path del file di output (in alternativa, l'output viene visualizzato a schermo)
        """

        # Controllo dei parametri di input
        try:
            # Arrivals
            check_pdf(arrivals, 'arrivals')
            # Services
            check_pdf(services, 'services')
        except PDF_Exception:
            raise
        # Servers
        if servers != INF:
            if not isinstance(servers, (int, long)):
                raise TypeError('"servers" parameter must be an integer number')
            if servers < 1:
                raise ValueError('"servers" parameter is not valid. Insert a positive integer value')
        # Capacity
        if capacity != INF:
            if not isinstance(capacity, (int, long)):
                raise TypeError('"capacity" parameter must be an integer number')
            if capacity < 0:
                raise ValueError(
                    '"capacity" parameter is not valid. Insert a non-negative integer number (or nothing, if you want '
                    'infinite capacity)')
        # Population
        if population != INF:
            if not isinstance(population, (int, long)):
                raise TypeError('"population" parameter must be an integer number')
            if population < 1:
                raise ValueError(
                    '"population" parameter is not valid. Insert a positive integer number (or nothing, if you want '
                    'infinite population)')
        # Schedule Policy
        if schedule_policy not in SCHEDULES:
            raise ValueError('"scedulePolicy" parameter is not valid (unknown value)')
        # Batches
        if isinstance(batches, (int, long)):
            # Caso 1: "batches" viene definito come intero, indicando il range [1, batches] da cui
            # estrarre, di volta in volta, il suo valore
            if batches < 1:
                raise ValueError('"batches" parameter is not valid. If integer, insert a number greater than zero')
            if population != INF and batches > population:
                raise ValueError(
                    '"batches" parameter is not valid. If integer, insert a number not greater than the "population" '
                    'parameter value')
            # OK: definisco batches come tupla
            batches = (1, batches)
        elif isinstance(batches, tuple):
            # Caso 2: "batches" viene definito come tupla, indicando il range [a, b] da cui estrarre,
            # di volta in volta, il suo valore
            if len(batches) != 2:
                raise ValueError('"batches" parameter is not valid. If tuple, it must have exactly two values')
            # Controllo "a"
            a = batches[0]
            if not isinstance(a, (int, long)):
                raise TypeError(
                    '"batches" parameter is not valid. If tuple, its first value must be a positive integer number')
            if a < 1:
                raise ValueError(
                    '"batches" parameter is not valid. If tuple, its first value must be an integer number greater '
                    'than zero')
            # Controllo "b"
            b = batches[1]
            if not isinstance(b, (int, long)):
                raise TypeError(
                    '"batches" parameter is not valid. If tuple, its second value must be a positive integer number')
            if b < 1:
                raise ValueError(
                    '"batches" parameter is not valid. If tuple, its second value must be an integer number greater '
                    'than zero')
            if b < a:
                raise ValueError(
                    '"batches" parameter is not valid. If tuple, its second value must be an integer number greater '
                    'than its first value')
            if population != INF and b > population:
                raise ValueError(
                    '"batches" parameter is not valid. If tuple, its second value must be an integer number not '
                    'greater than the "population" parameter value')
        else:
            # Il tipo della variabile "batches" non va bene
            raise TypeError('"batches" parameter must be an integer number or a tuple with two values')
        # File di output
        self.logFile = log_file
        self.logFileIsOpen = False
        if log_file is None:
            self.fp = None
            self.logFileIsOpen = None
        else:
            self.open_log_file('w')
        # Callback
        if service_callback is not None:
            ic.check_function(service_callback, 'serviceCallback')
            if callback_params is not None:
                ic.check_dict(callback_params, 'callbackParams')
        # Calcolo la capacita' complessiva del sistema
        if capacity == INF or servers == INF:
            system_capacity = INF
        else:
            system_capacity = capacity + servers

        # I parametri di input sono ok: li salvo
        self.pdfArrivals = arrivals
        self.pdfServices = services
        self.servers = servers
        self.capacity = system_capacity
        self.population = population
        self.schedulePolicy = schedule_policy
        self.batches = batches
        # Creo l'ambiente di test
        self.set_environment()
        # Callback chiamata non appena un cliente viene servito
        self.serviceCallback = service_callback
        self.callbackParams = callback_params
        # Messaggio di aiuto
        self.help = readme
        # ID della prossima richiesta in arrivo
        self.i = 0
        # Parametri richiesti dalla pdf
        print('-- Arrivals parameters --')
        self.arrivalParams = get_pdf_params(self.pdfArrivals)
        print('\n-- Service parameters --')
        self.serviceParams = get_pdf_params(self.pdfServices)
        # Preparo la simulazione
        self.prepare()

    # noinspection PyAttributeOutsideInit
    def set_environment(self, env=None, lock=False, p=1):
        """
        La funzione associa l'ambiente di test alla coda: se non specificato, l'ambiente viene creato al volo
        - "env" e' l'ambiente di simulazione
        - "lock" e' in booleano, indica se l'arrivo di richieste e' controllato dalla coda precedente
        - "p" e' la probabilita' con cui viene accettata la richiesta in arrivo (valore compreso tra 0 ed 1)
        """
        # Controllo dell'input
        ic.check_number(p, 'probability to accept a request', 0, 1)

        if env is None:
            # Creo al volo l'ambiente di test
            env = simpy.Environment()
        # Associazione
        self.env = env
        # Modulo per le statistiche
        self.stats = qs_stats.QS_StatsManager(self.env)
        # Sistema nel complesso e server interni sono modellizzati come risorse condivise
        self._QS = simpy.Resource(self.env, capacity=self.capacity)
        self._S = simpy.Resource(self.env, capacity=self.servers)
        # La popolazione viene modellizzata come contenitore di risorse condivise
        self._P = simpy.Container(self.env, capacity=self.population, init=self.population)
        # Se richiesto, e' possibile fare in modo che l'arrivo di una richiesta sia comandato dall'esterno (es: chained)
        if lock:
            self._LockedQueue = simpy.Container(self.env, capacity=INF, init=0)
            self.probToArrive = p
        else:
            # Nota: in questo caso, la coda di blocco e' totalmente ininfluente
            self._LockedQueue = simpy.Container(self.env, capacity=INF, init=INF)
            self.probToArrive = 1

    def unlock(self, n=1):
        """
        La funzione sblocca la coda, permettendo l'arrivo in ingresso di "n" richieste utente
        """
        self._LockedQueue.put(n)

    # noinspection PyPep8Naming
    def N(self):
        """
        Numero di utenti nel sistema coda (queuing line + servers)
        """
        return self._QS.count

    # noinspection PyPep8Naming
    def N_S(self):
        """
        Numero di utenti in elaborazione nei server
        """
        return self._S.count

    # noinspection PyPep8Naming
    def N_W(self):
        """
        Numero di utenti in coda (queuing line)
        """
        return self.N() - self.N_S()

    def prepare(self):
        """
        La funzione prepara la coda alla simulazione
        """
        self.env.process(self.start())

    def run(self, until, graphs=True):
        """
        Lancia una simulazione, chiamando il metodo "run" dell'ambiente di test simpy
        """
        try:
            # Inizializzo il nuovo batch
            self.stats.new_batch()
            # Lancio la simulazione vera e propria
            self.env.run(until=until)
            # Statistiche di simulazione
            self.info(until, graphs)
            # Chiudo il file di output, se specificato
            self.close_log_file()
        except:
            print('An error occured during the simulation.')
            raise

    def start(self):
        """
        Processo per generare l'arrivo di richieste da parte di clienti e, se non scartate, la loro elaborazione
        """
        if self.schedulePolicy is 'FIFO':
            while True:
                # La prima cosa da fare e' estrarre il valore del batch (il numero di utenti
                # che faranno contemporaneamente una richiesta al sistema)
                batch = self.new_batch()

                # A questo punto, controllo di poter ricevere le richieste utente (coda sbloccata: utile nel caso
                # "chained", ininfluente altrimenti)
                # NOTA: per code "chained" bloccate, il batch estratto varra' sempre 1. Ma per non perdere in
                # generalita', consideriamo anche il caso di code controllanti dalle quali le richieste elaborate
                # escono come batch
                yield self._LockedQueue.get(batch)
                # Nel caso di code controllate, la richiesta in arrivo e' comunque subordinata ad un valore di
                # probabilita'. Occorre quindi verificare che la richiesta arrivi correttamente alla coda
                for r in range(batch):
                    p = random.random()
                    if p > self.probToArrive:
                        # La richiesta non arriva al sistema
                        self.log('Customer request #%d does not reach the system' % self.i)
                        self.stats.unarrived_requests(1)
                        self.i += 1
                        batch -= 1
                if batch == 0:
                    continue

                # Dopodiche', mi accerto che la popolazione di utenti non sia interamente nel sistema
                yield self._P.get(batch)

                # Arrivo dei clienti
                time_to_arrive = pdf_random(self.pdfArrivals, self.arrivalParams)
                arrival_proc = self.env.timeout(time_to_arrive)
                yield arrival_proc
                self.print_arrivals(self.i, batch)

                # I clienti tentano di accedere al sistema: se la coda ed i server sono pieni (o si riempiono),
                # la loro richiesta viene scartata.
                # Calcolo quindi il numero di posti disponibili
                if self.capacity == INF:
                    places = batch  # Significa: ho posto per tutti (capacita' del sistema infinita)
                else:
                    places = self.capacity - self.N()

                # ID delle richieste in arrivo
                delta_i = min(places, batch)
                ids = list(range(self.i, self.i + delta_i))
                self.i += delta_i
                # Aggiorno le statistiche, causa accettazione di richieste utente
                self.stats.accept(ids)
                # Log degli arrivi e presa in carico delle richieste da parte dei server
                for req_id in ids:
                    # Questi utenti vengono accettati nel sistema e messi in coda
                    request_proc = self._QS.request()
                    yield request_proc
                    self.log('Customer request #%d has been accepted into the system' % req_id)
                    # La richiesta del cliente verra' presa in carico appena possibile
                    # noinspection PyUnusedLocal
                    service_proc = self.env.process(self.process_customer(req_id, request_proc))

                ids = []
                # Vediamo ora se ci sono stati utenti rifiutati...
                if batch > places:
                    for user in range(batch - places):
                        # Questi utenti vengono rifiutati dal sistema: la coda e' piena
                        self.log(
                            'Customer request #%d has been rejected by the system, because the queue is full' % self.i)
                        ids.append(self.i)
                        # Prossimo cliente
                        self.i += 1
                # Aggiorno le statistiche, causa rifiuto di richieste utente
                self.stats.reject(ids)
        else:
            # TODO: se necessario, sviluppare il codice per altre scheduling policies ??
            pass

    def process_customer(self, i, request_proc):
        """
        Quando un cliente entra nel sistema, rimane in attesa per essere processato da uno dei server
        """
        with self._S.request() as serviceReq:
            # Il cliente sta occupando un posto in coda: aspetta quindi che si liberi un server
            yield serviceReq
            # Il cliente viene servito dal server
            self.log('Customer #%d starts to be served at t = %d' % (i, self.env.now))
            self.stats.start_to_serve([i])
            time_to_serve = pdf_random(self.pdfServices, self.serviceParams)
            service_proc = self.env.timeout(time_to_serve)
            yield service_proc
            # Il cliente e' stato servito: esce quindi dal sistema
            self.log('Customer #%d is served at t = %d' % (i, self.env.now))
            self.stats.end_to_serve([i])
            yield self._QS.release(request_proc)
            if self._P.level != INF:
                yield self._P.put(1)
            # Se definita, viene attivata la callback (con o senza i parametri, a seconda che questi siano stati
            # specificati)
            if self.serviceCallback is not None:
                if self.callbackParams is not None:
                    self.serviceCallback(self.callbackParams)
                else:
                    self.serviceCallback()

    def new_batch(self):
        """
        Questo metodo estrae un valore per il batch: in altre parole, decide casualmente
        (pdf uniforme) quanti clienti arriveranno al sistema in contemporanea
        """
        # RISULTATO: batch = U(a, b)
        a = self.batches[0]
        # Population requirements
        if self._P.level != INF:
            b = max(a, min(self.batches[1], self._P.level))
        else:
            b = self.batches[1]
        batch_values = list(range(a, b + 1))
        return random.choice(batch_values)

    def print_arrivals(self, customer_number, batches):
        """
        Stampa a schermo il messaggio di arrivo relativo ad un batch di richieste
        """
        if batches > 1:
            self.log(
                '%d customer requests (from #%d to #%d) arrive at t = %d. There are %d user(s) in the system, '
                '%d of them in the server(s)' % (
                    batches, customer_number, customer_number + batches - 1, self.env.now, self.N(), self.N_S()))
        else:
            self.log(
                'Customer request #%d arrive at t = %d. There are %d user(s) in the system, %d of them in the server(s)'
                % (customer_number, self.env.now, self.N(), self.N_S()))

    def info(self, until, graphs=True):
        """
        La funzione permette di visualizzare le statistiche del sistema
        """
        # Aggiorno i valore di tempo di inizio/fine simulazione (globale e batch)
        self.stats.update_end_time(until)
        # Elaboro i dati delle statistiche
        self.stats.results(graphs)

    def get_stats(self):
        """
        La funzione ritorna tutte le statistiche elaborate per il batch corrente
        """
        return self.stats.current_batch()

    def log(self, msg):
        """
        Stampa in output il messaggio "msg": su file o a schermo, a seconda del valore di "logFile"
        """
        if self.logFile is None:
            print(msg)
        else:
            self.open_log_file()
            self.fp.write(msg + '\n')

    def open_log_file(self, how='a'):
        """
        Se il file di log e' stato chiuso, viene riaperto (default: in modalita' "append"): se invece e' gia' aperto, 
        non faccio nulla
        """
        if self.logFileIsOpen is None:
            # Non e' previsto l'output su file
            return
        if self.logFileIsOpen:
            # Il file di output e' gia' stato aperto in precedenza
            return
        # Apro il file di log
        try:
            self.fp = open(self.logFile, how)
        except:
            print('An error occured trying to open/create the log output file')
            raise
        self.logFileIsOpen = True

    def close_log_file(self):
        """
        Chiude il file di output (se previsto e se aperto)
        """
        if self.fp is not None:
            if self.logFileIsOpen:
                self.fp.close()
                self.logFileIsOpen = False

    def set_callback(self, f, **params):
        """
        La funzione permette di settare una callback per l'elaborazione delle richieste
        """
        self.serviceCallback = f
        self.callbackParams = params

    def plots(self):
        """
        Stampa a schermo i grafici richiesti
        """
        self.stats.plots()

    def confidence_intervals(self, confidence_level):
        """
        La funzione calcola tutti gli intervalli di confidenza che il modulo "stats" mette a disposizione.
        - "confidence_level" e' il livello di confidenza desiderato
        """
        self.stats.confidence_intervals(confidence_level)


class ChainedQueueSystem(object):
    """
    La classe modellizza un sistema composto da code, connesse tra loro in serie
    """

    # noinspection PyPep8Naming
    def __init__(self, queues, probs=None):
        """
        I parametri di input sono:
        - "queues": una lista di code, da collegare tra loro nell'ordine in cui si trovano in lista
        - "probs": parametro facoltativo, e' una lista di valori di probabilita' (compresi tra 0 ed 1 inclusi)
            Indicano, per ogni coda, la probabilita' che la richiesta appena servita arrivi in ingresso alla coda
            successiva: se non specificati, si sottintende probabilita' del 100 %.
            Se la dimensione della lista eccede il numero di code - 1, i valori di probabilita' vengono ignorati: se
            invece non raggiungono questa dimensione, allora vengono forzati a 1
        """
        # Controllo dei parametri di input
        # Queues
        ic.check_array(queues, 'queues', of=QueueSystem)
        len_q = len(queues)
        if len_q < 2:
            raise ValueError('"queues" list must contain at least 2 elements')
        # Probs
        if probs is not None:
            ic.check_array(probs, 'probs', of=float)
            for p in probs:
                ic.check_number(p, 'probs value', 0, 1)
            # Completo con "1"
            to_add = len(probs) - (len_q - 1)
            if to_add > 0:
                probs += [1] * to_add
        else:
            # Vettore di "1"
            probs = [1] * (len_q - 1)

        # Salvo i parametri di input
        self.queues = queues
        self.probs = probs
        # A questo punto, occorre definire un ambiente di simulazione comune
        self.env = simpy.Environment()
        self.queues[0].set_environment(self.env, p=probs[0])
        # E collegare insieme tra loro le code, modificando opportunamente quelle dopo la prima per evitare
        # incongruenze di progetto
        for i in range(0, len_q - 1):
            # Connessione della coda con quella successiva (bloccata)
            self.queues[i].set_callback(self.traverse, arrivingQueue=self.queues[i + 1])
            # Altero le proprieta' delle code successive alla prima
            self.queues[i + 1].pdfArrivals = 'Chain'
            self.queues[i + 1].arrivalParams = get_pdf_params(self.queues[i + 1].pdfArrivals)
            self.queues[i + 1].population = INF
            self.queues[i + 1].batches = (1, 1)
            self.queues[i + 1].set_environment(self.env, lock=True, p=probs[i])
        # Definisco il gestore delle statistiche
        self.stats = qs_stats.CQS_StatsManager(self.queues)
        # Preparo i processi per lo scheduling, per ogni coda del sistema
        self.prepare()

    # noinspection PyMethodMayBeStatic
    def traverse(self, params):
        """
        La funzione viene usata in fase di passaggio di richieste da una coda all'altra
        - "arrivingQueue" e' la coda che deve ricevere la richiesta in ingresso
        """
        # Estraggo i parametri dal dizionario
        arriving_queue = params['arrivingQueue']
        # Inoltro la richiesta alla coda successiva
        arriving_queue.unlock()

    def prepare(self):
        """
        La funzione prepara le code del sistema alla simulazione
        """
        for q in self.queues:
            q.prepare()

    def run(self, until):
        """
        Lancia una simulazione, chiamando il metodo "run" dell'ambiente di test simpy
        """
        try:
            # Crea il batch di simulazione, in ogni coda
            for q in self.queues:
                q.stats.new_batch()
            # Lancio la simulazione vera e propria
            self.env.run(until=until)
            # Statistiche di simulazione (sistema nel complesso + code)
            self.info(until)
            # Chiudo il file di output per ogni coda, se specificato
            self.close_log_files()
        except:
            print('An error occured during the simulation.')
            raise

    def info(self, until):
        """
        La funzione elabora le statistiche del sistema nel complesso e per ogni soda che lo compone
        """
        self.stats.resume(until)

    def close_log_files(self):
        """
        La funzione chiude i file di log aperti per le code che compongono il sistema
        """
        for q in self.queues:
            q.close_log_file()


def readme():
    """
    Guida all'uso della libreria
    """
    print('\n--- HOW TO USE ---\n')
    print(
        'With the class "QueueSystem" you can model a queue system: when you instantiate the queue, you pass as '
        'parameters the simulation environment and, according to Kendall\'s notation, the system parameters')
    print('- "env": the simulation environment (compulsary)')
    print('- "arrivals" (A): arrival times probability density function (default: exponential)')
    print('- "services" (B): service times probability density function (default: exponential)')
    print('- "servers" (c): the number of internal available servers (default: 1)')
    print(
        '- "capacity" (d): the capacity of the queuing line. The overall system capacity is indeed the sum of this '
        'value and the number of servers (default: infinity)')
    print('- "population" (e): the maximum number of users, inside and/or outside the system (default: infinity)')
    print('- "schedulePolicy" (f): the scheduling policy of the queue (default: FIFO)')
    print('- "batches": the number of users that can arrive together (default: 1), can be a tuple (v_min, v_max)')
    print('- "logFile": the name of the output text file to use')
    print('- "serviceCallback": function to be executed every time a customer is served (default: None)')
    print('- "callbackParams": dictionary, containing the parameters for the callback (default: None)\n')
    available_pdfs()
    print('')
    available_schedulings()
    print('\n------------------')
