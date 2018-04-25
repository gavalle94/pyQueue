import numpy
from scipy.stats import t as students_t
import qs_plots
import input_controls as ic
from timed_structures import *


class ComputedStats(object):
    """
    La classe contiene tutte le statistiche computate, per un batch o globalmente
    """

    def __init__(self):
        self._d = {
            # Timestamp
            'startTime': 0,  # Tempo di inizio simulazione
            'endTime': 0,  # Tempo di fine elaborazione
            # ID richieste
            'initialRequestId': 0,  # Identificativo della prima richiesta non ancora servita
            'finalRequestId': 0,  # Identificativo dell'ultima richiesta da servire
            # Contatori richieste
            'totalRequests': 0,  # numero di richieste cliente arrivate al sistema
            'lostRequests': 0,  # numero di richieste cliente perse (sistema saturo)
            'notArrivedRequests': 0,  # numero di richieste non pervenute al sistema
            'satisfiedRequests': 0,  # numero di richieste cliente elaborate correttamente
            # Utenti nel sistema
            'initialOccupancy': 0,  # numero di utenti nel sistema, a inizio simulazione
            'finalOccupancy': 0,  # numero di utenti nel sistema, a fine simulazione
            'initialQueueOccupancy': 0,  # numero di utenti nella queueing line, a inizio simulazione
            'finalQueueOccupancy': 0,  # numero di utenti nella queueing line, a fine simulazione
            # Statistiche finali
            'N': -1.0,
            'N_W': -1.0,
            'N_S': -1.0,
            'T': -1.0,
            'T_W': -1.0,
            'T_S': -1.0
        }

    def set_start_time(self, start_time):
        self._d['startTime'] = start_time

    def get_start_time(self):
        return self._d['startTime']

    def set_end_time(self, end_time):
        self._d['endTime'] = end_time

    def get_end_time(self):
        return self._d['endTime']

    def set_initial_request_id(self, req_id):
        self._d['initialRequestId'] = req_id

    def get_initial_request_id(self):
        return self._d['initialRequestId']

    def set_final_request_id(self, req_id):
        self._d['finalRequestId'] = req_id

    def get_final_request_id(self):
        return self._d['finalRequestId']

    def set_total_requests(self, t):
        self._d['totalRequests'] = t

    def get_total_requests(self):
        return self._d['totalRequests']

    def set_lost_requests(self, l):
        self._d['lostRequests'] = l

    def get_lost_requests(self):
        return self._d['lostRequests']

    def set_not_arrived_requests(self, nar):
        self._d['notArrivedRequests'] = nar

    def get_not_arrived_requests(self):
        return self._d['notArrivedRequests']

    def set_satisfied_requests(self, sr):
        self._d['satisfiedRequests'] = sr

    def get_satisfied_requests(self):
        return self._d['satisfiedRequests']

    def set_initial_occupancy(self, o):
        self._d['initialOccupancy'] = o

    def get_initial_occupancy(self):
        return self._d['initialOccupancy']

    def set_final_occupancy(self, o):
        self._d['finalOccupancy'] = o

    def get_final_occupancy(self):
        return self._d['finalOccupancy']

    def set_initial_queue_occupancy(self, qo):
        self._d['initialQueueOccupancy'] = qo

    def get_initial_queue_occupancy(self):
        return self._d['initialQueueOccupancy']

    def set_final_queue_occupancy(self, qo):
        self._d['finalQueueOccupancy'] = qo

    def get_final_queue_occupancy(self):
        return self._d['finalQueueOccupancy']

    # noinspection PyPep8Naming
    def get_N(self):
        return self._d['N']

    # noinspection PyPep8Naming
    def set_N(self, n):
        self._d['N'] = n

    # noinspection PyPep8Naming
    def get_N_W(self):
        return self._d['N_W']

    # noinspection PyPep8Naming
    def set_N_W(self, n_w):
        self._d['N_W'] = n_w

    # noinspection PyPep8Naming
    def get_N_S(self):
        return self._d['N_S']

    # noinspection PyPep8Naming
    def set_N_S(self, n_s):
        self._d['N_S'] = n_s

    # noinspection PyPep8Naming
    def get_T(self):
        return self._d['T']

    # noinspection PyPep8Naming
    def set_T(self, t):
        self._d['T'] = t

    # noinspection PyPep8Naming
    def get_T_W(self):
        return self._d['T_W']

    # noinspection PyPep8Naming
    def set_T_W(self, t_w):
        self._d['T_W'] = t_w

    # noinspection PyPep8Naming
    def get_T_S(self):
        return self._d['T_S']

    # noinspection PyPep8Naming
    def set_T_S(self, t_s):
        self._d['T_S'] = t_s

    def increment_total_requests(self, n):
        self._d['totalRequests'] += n
        self.increment_final_request_id(n)

    def increment_lost_requests(self, n):
        self._d['lostRequests'] += n

    def increment_not_arrived_requests(self, n):
        self._d['notArrivedRequests'] += n
        self.increment_total_requests(n)

    def increment_satisfied_requests(self, n):
        self._d['satisfiedRequests'] += n

    def increment_final_occupancy(self, n):
        self._d['finalOccupancy'] += n

    def increment_final_queue_occupancy(self, n):
        self._d['finalQueueOccupancy'] += n

    def increment_final_request_id(self, n):
        self._d['finalRequestId'] += n

    def compute_stats(self, occupancy, queue_occupancy, waited_for, served_in, end_time):
        """
        La funzione attribuisce al batch le statistiche elaborate a fine simulazione
        """
        # ID delle richieste da considerare per le analisi
        range_ids = (
            self.get_initial_request_id(),
            self.get_final_request_id()
        )
        range_times = (
            self.get_start_time(),
            self.get_end_time()
        )
        # Vettori di appoggio
        occupancy_batch = occupancy.filter_time_range(range_times[0], range_times[1])
        queue_occupancy_batch = queue_occupancy.filter_time_range(range_times[0], range_times[1])
        waited_for_batch = waited_for.filter_data_range(range_ids[0], range_ids[1])
        served_in_batch = served_in.filter_data_range(range_ids[0], range_ids[1])
        # Valutazioni
        n = integral_mean(occupancy_batch, end_time)
        n_w = integral_mean(queue_occupancy_batch, end_time)
        n_s = n - n_w
        t_w = mean(waited_for_batch.get_time_list())
        t_s = mean(served_in_batch.get_time_list())
        t = mean(
            # Qui, ottengo un vettore contenente i tempi di attraversamento per ogni richiesta
            map(
                # Il vettore che vado a calcolare e' formato da tuple: waitingTime, serviceTime
                # Il tempo di attraversamento della richiesta e' dato dalla somma di questi due valori
                (lambda x: x[0] + x[1]),
                zip(
                    # "zip" fornisce in uscita un vettore di lunghezza pari al minimo di quelle di ingresso
                    waited_for_batch.get_time_list(),
                    served_in_batch.get_time_list()
                )
            )
        )
        # Salvo i risultati
        self.set_N(n)
        self.set_N_S(n_s)
        self.set_N_W(n_w)
        self.set_T(t)
        self.set_T_S(t_s)
        self.set_T_W(t_w)


# noinspection PyPep8Naming
class CQS_StatsManager(object):
    """
    Gestore delle statistiche per un sistema di code concatenate tra loro
    """

    def __init__(self, queues):
        """
        L'unico parametro richiesto e' l'elenco delle code di cui il sistema si compone
        """
        self.queues = queues

    def resume(self, until):
        """
        La funzione elabora tutte le statistiche richieste, sia per le code che per il sistema nel complesso
        """
        # Statistiche per le code
        for queue in self.queues:
            queue.info(until)
        # Statistiche del sistema, nel complesso
        print('\n\n*** SYSTEM STATS ***')
        end_time = self.queues[0].stats.get_global_stats().get_end_time()
        N = sum(map(lambda q: integral_mean(q.stats.occupancy, end_time), self.queues))
        NW = sum(map(lambda q: integral_mean(q.stats.queueOccupancy, end_time), self.queues))
        NS = N - NW
        print('Average number of customers into the system: %.2f' % N)
        print('Average number of customers into the queuing lines: %.2f' % NW)
        print('Average number of customers into the servers: %.2f' % NS)

        # X contiene il numero di richieste servite dal sistema alla coda i-esima
        X = map(lambda q: q.stats.not_arrived_requests(),
                self.queues[1:])  # Richieste elaborate che non hanno raggiunto le code successive
        # Richieste elaborate dall'ultima coda, che hanno quindi attraversato l'intero sistema
        X.append(self.queues[-1].stats.served_requests())
        s = sum(X)
        if s > 0:
            print('\nConsidering only served requests:')
            # Ricavo il tempo speso all'interno delle QLs
            TWQ = map(lambda q: mean(q.stats.waitedFor.get_time_list()),
                      self.queues)  # Tempi di attesa nelle singole code
            TW = 0.0
            for i in range(len(X)):
                TW += sum(TWQ[:i + 1]) * X[i]
            TW /= s
            print('- Average time spent by a customer into queuing line(s): %.2f' % TW)
            # Ricavo il tempo speso all'interno dei server
            TSQ = map(lambda q: mean(q.stats.servedIn.get_time_list()),
                      self.queues)  # Tempi di elaborazione nelle singole code
            TS = 0.0
            for i in range(len(X)):
                TS += sum(TSQ[:i + 1]) * X[i]
            TS /= s
            print('- Average time spent by a customer into the server(s): %.2f' % TS)
            # Ricavo il tempo speso all'interno del sistema
            T = TS + TW
            print('=> Average time spent by a customer into the whole system: %.2f' % T)


# noinspection PyPep8Naming
class QS_StatsManager(object):
    """
    Gestore delle statistiche per un sistema coda
    """

    def __init__(self, env):
        # Ambiente di test
        self._env = env

        # Statistiche dell'intero arco temporale
        self._globalStats = ComputedStats()
        # Statistiche per ogni batch di simulazione
        self._batchStats = []

        # Richieste cliente interne
        self.pendingRequests = TimedArray()  # richieste nella queuing line
        self.pendingServices = TimedArray()  # richieste in elaborazione nei server
        # Tempi di attesa/elaborazione
        self.waitedFor = TimedArray(False)  # tempi di attesa (in coda) per le richieste
        self.servedIn = TimedArray(False)  # tempi di elaborazione (nei server) per le richieste
        # Utenti nel sistema
        self.currentOccupancy = 0  # numero di utenti attualmente nell'intero sistema
        self.currentQueueOccupancy = 0  # numero di utenti attualmente nella sola queuing line
        self.occupancy = TimedArray(empty=False)  # numero di utenti nell'intero sistema, nei vari istanti di tempo
        self.queueOccupancy = TimedArray(empty=False)  # numero di utenti nella sola QL, nei vari istanti di tempo
        # ID della prossima richiesta in arrivo
        self.next_request_id = 0

    def current_batch(self):
        return self._batchStats[-1]

    def get_global_stats(self):
        """
        La funzione ritorna le statistiche globali di simulazione 
        """
        return self._globalStats

    def get_batches_stats(self):
        """
        La funzione ritorna, come lista, le statistiche di simulazione per ogni batch
        """
        return self._batchStats

    def get_batch_stats(self, i):
        """
        La funzione ritorna, come lista, le statistiche di simulazione relative all'i-esimo batch 
        """
        return self._batchStats[i]

    def get_n_batches(self):
        """
        La funzione ritorna il numero di batch lanciati in simulazione
        """
        return len(self._batchStats)

    def new_batch(self):
        """
        Creo un nuovo batch di simulazione
        """
        # Creo il batch vuoto
        batch = ComputedStats()
        # Dati dalla simulazione precedente
        prev_end_time = self._globalStats.get_end_time()
        prev_to_serve_id = self.next_request_id
        prev_occupancy = self._globalStats.get_final_occupancy()
        prev_queue_occupancy = self._globalStats.get_final_queue_occupancy()
        # Update
        batch.set_start_time(prev_end_time)
        batch.set_end_time(prev_end_time)
        batch.set_initial_request_id(prev_to_serve_id)
        batch.set_final_request_id(prev_to_serve_id)
        batch.set_initial_occupancy(prev_occupancy)
        batch.set_final_occupancy(prev_occupancy)
        batch.set_initial_queue_occupancy(prev_queue_occupancy)
        batch.set_final_queue_occupancy(prev_queue_occupancy)
        # Memorizzo il batch per l'utilizzo
        self._batchStats.append(batch)

    def now(self):
        """
        La funzione ritorna il timestamp corrente del simulatore 
        """
        return int(self._env.now)

    def accept(self, ids):
        """
        Questo metodo viene chiamato quando il sistema accetta nuove richieste
        - "ids" e' un vettore contenente l'elenco degli identificativi delle richieste accettate
        """
        # Controllo dei parametri di input: "ids"
        if not isinstance(ids, (list, tuple)):
            raise TypeError('"ids" parameter is invalid. It must be an array')
        # Calcolo il numero di richieste accettate
        n = len(ids)
        if n > 0:
            # Calcolo il timestamp
            timestamp = self.now()
            # Registro le nuove richieste
            self.accept_requests(n)
            for i in ids:
                item = TimedData(i, timestamp)
                self.pendingRequests.append(item)
            # Aggiorno i riferimenti temporali per i valori di occupazione
            # NOTA: potrei avere ingressi e uscite di utenti dal sistema nello stesso timestamp!
            # Pertanto... se il timestamp esiste gia' devo aggiornare il record, invece di crearne uno nuovo
            time_vectors = [self.occupancy, self.queueOccupancy]
            new_occupancies = [self.currentOccupancy, self.currentQueueOccupancy]
            for i in range(2):
                vect = time_vectors[i]
                new_occupancy = new_occupancies[i]
                if vect.contains(timestamp):
                    # Aggiorno il valore di occupazione esistente
                    vect.update(timestamp, new_occupancy)
                else:
                    # Nuovo valore di occupazione
                    item = TimedData(new_occupancy, timestamp)
                    vect.append(item)

    def reject(self, ids):
        """
        Questo metodo viene chiamato quando il sistema rifiuta nuove richieste, perche' saturo
        - "ids" e' un vettore contenente l'elenco degli identificativi delle richieste rifiutate
        """
        # Controllo dei parametri di input: "ids"
        if not isinstance(ids, (list, tuple)):
            raise TypeError('"ids" parameter is invalid. It must be an array')
        # Calcolo il numero di richieste rifiutate
        n = len(ids)
        if n > 0:
            self.reject_requests(n)

    def start_to_serve(self, ids):
        """
        Questo metodo viene chiamato quando i server del sistema iniziano ad elaborare alcune richieste in coda
        - "ids" e' un vettore contenente l'elenco degli identificativi delle richieste prese in carico dai server
        """
        # Controllo dei parametri di input: "ids"
        if not isinstance(ids, (list, tuple)):
            raise TypeError('"ids" parameter is invalid. It must be an array')
        # Calcolo il numero di richieste prese in carico
        n = len(ids)
        if n > 0:
            # Calcolo il timestamp
            timestamp = self.now()
            # Aggiorno l'occupazione corrente della coda
            self.update_queue_occupancy(-n)
            # Aggiorno il riferimento temporale per il valore di occupazione
            # NOTA: potrei avere ingressi e uscite di utenti dalla coda nello stesso timestamp!
            # Pertanto... se il timestamp esiste gia' devo aggiornare il record, invece di crearne uno nuovo
            if self.queueOccupancy.contains(timestamp):
                # Aggiorno il valore di occupazione esistente
                self.queueOccupancy.update(timestamp, self.currentQueueOccupancy)
            else:
                # Nuovo valore di occupazione
                item = TimedData(self.currentQueueOccupancy, timestamp)
                self.queueOccupancy.append(item)
            # Ricavo l'elenco di richieste in uscita dalla coda
            not_pending_anymore = self.pendingRequests.search_by_datas(ids)
            for x in not_pending_anymore:
                # Tengo traccia del loro tempo di coda effettivo
                tmp = TimedData(x.data, timestamp - x.time, timestamp=False)
                self.waitedFor.append(tmp)
                # La richiesta entra nel server
                tmp = TimedData(x.data, timestamp)
                self.pendingServices.append(tmp)
            # Non mi serve piu' tenere traccia delle risorse, una volta uscite dalla coda
            self.pendingRequests.remove_all(not_pending_anymore)

    def end_to_serve(self, ids):
        """
        Questo metodo viene chiamato quando i server del sistema finiscono di elaborare alcune richieste in coda
        - "ids" e' un vettore contenente l'elenco degli identificativi delle richieste elaborate dai server
        """
        # Controllo dei parametri di input: "ids"
        if not isinstance(ids, (list, tuple)):
            raise TypeError('"ids" parameter is invalid. It must be an array')
        # Calcolo il numero di richieste elaborate
        n = len(ids)
        if n > 0:
            # Calcolo il timestamp
            timestamp = self.now()
            # Aggiorno i contatori per richieste elaborate e clienti nel sistema
            self.satisfied_requests(n)
            # Aggiorno il riferimento temporale per il valore di occupazione
            # NOTA: potrei avere ingressi e uscite di utenti dal sistema nello stesso timestamp!
            # Pertanto... se il timestamp esiste gia' devo aggiornare il record, invece di crearne uno nuovo
            if self.occupancy.contains(timestamp):
                # Aggiorno il valore di occupazione esistente
                self.occupancy.update(timestamp, self.currentOccupancy)
            else:
                # Nuovo valore di occupazione
                item = TimedData(self.currentOccupancy, timestamp)
                self.occupancy.append(item)
            # Ricavo l'elenco di richieste in uscita dal sistema
            not_pending_anymore = self.pendingServices.search_by_datas(ids)
            for x in not_pending_anymore:
                # Tengo traccia del loro tempo di elaborazione effettivo
                tmp = TimedData(x.data, timestamp - x.time, timestamp=False)
                self.servedIn.append(tmp)
            # Non mi serve piu' tenere traccia delle richieste, una volta elaborate
            self.pendingServices.remove_all(not_pending_anymore)

    def not_arrived_requests(self):
        return self.current_batch().get_not_arrived_requests()

    def not_arrived_requests_perc(self):
        return _perc(
            self.not_arrived_requests(),
            self.received_requests()
        )

    def not_arrived_total_requests(self):
        return self._globalStats.get_not_arrived_requests()

    def not_arrived_total_requests_perc(self):
        return _perc(
            self.not_arrived_total_requests(),
            self.received_total_requests()
        )

    def received_requests(self):
        return self.current_batch().get_total_requests()

    def received_requests_perc(self):
        return _perc(
            self.received_requests() - self.not_arrived_requests(),
            self.received_requests()
        )

    def received_total_requests(self):
        return self._globalStats.get_total_requests()

    def received_total_requests_perc(self):
        return _perc(
            self.received_total_requests() - self.not_arrived_total_requests(),
            self.received_total_requests()
        )

    def accepted_requests(self):
        return self.received_requests() - self.rejected_requests() - self.not_arrived_requests()

    def accepted_requests_perc(self):
        return _perc(
            self.accepted_requests(),
            self.received_requests() - self.not_arrived_requests()
        )

    def accepted_total_requests(self):
        return self.received_total_requests() - self.rejected_total_requests()

    def accepted_total_requests_perc(self):
        return _perc(
            self.accepted_total_requests(),
            self.received_total_requests() - self.not_arrived_total_requests()
        )

    def rejected_requests(self):
        return self.current_batch().get_lost_requests()

    def rejected_requests_perc(self):
        return _perc(
            self.rejected_requests(),
            self.received_requests() - self.not_arrived_requests()
        )

    def rejected_total_requests(self):
        return self._globalStats.get_lost_requests()

    def rejected_total_requests_perc(self):
        return _perc(
            self.rejected_total_requests(),
            self.received_total_requests() - self.not_arrived_total_requests()
        )

    def served_requests(self):
        return self.current_batch().get_satisfied_requests()

    def served_requests_perc(self):
        return _perc(
            self.served_requests(),
            self.accepted_requests()
        )

    def served_total_requests(self):
        return self._globalStats.get_satisfied_requests()

    def served_total_requests_perc(self):
        return _perc(
            self.served_total_requests(),
            self.accepted_total_requests()
        )

    def results(self, graphs=True):
        """
        La funzione stampa a schermo tutte le statistiche elaborate per il sistema in questione
        """
        # VARIABILI
        # Durata della simulazione
        start_time = self.current_batch().get_start_time()
        end_time = self.current_batch().get_end_time()
        # Utenti al momento nel sistema
        n_users = self.currentOccupancy
        n_users_ql = self.currentQueueOccupancy
        # Richieste non giunte al sistema
        req_not_arrived = self.not_arrived_requests()
        req_not_arrived_perc = self.not_arrived_requests_perc()
        req_not_arrived_tot = self.not_arrived_total_requests()
        req_not_arrived_perc_tot = self.not_arrived_total_requests_perc()
        # Richieste giunte al sistema
        req_arrived = self.received_requests() - self.not_arrived_requests()  # ZIO
        req_arrived_perc = self.received_requests_perc()
        req_arrived_tot = self.received_total_requests() - self.not_arrived_total_requests()  # ZIO
        req_arrived_perc_tot = self.received_total_requests_perc()
        # Parte delle richieste arrivate che e' stata accettata
        req_accepted = self.accepted_requests()
        req_accepted_perc = self.accepted_requests_perc()
        req_accepted_tot = self.accepted_total_requests()
        req_accepted_perc_tot = self.accepted_total_requests_perc()
        # Parte delle richieste arrivate che e' stata rifiutata
        req_rejected = self.rejected_requests()
        req_rejected_perc = self.rejected_requests_perc()
        req_rejected_tot = self.rejected_total_requests()
        req_rejected_perc_tot = self.rejected_total_requests_perc()
        # Parte delle richieste arrivate che e' stata servita
        req_served = self.served_requests()
        req_served_perc = self.served_requests_perc()
        req_served_tot = self.served_total_requests()
        req_served_perc_tot = self.served_total_requests_perc()
        # VALORI MEDI
        # Globali
        self._globalStats.compute_stats(self.occupancy, self.queueOccupancy, self.waitedFor, self.servedIn, end_time)
        # Per il batch
        self.current_batch().compute_stats(self.occupancy, self.queueOccupancy, self.waitedFor, self.servedIn, end_time)

        # Creo i nodi di fine simulazione (utili per i grafici a schermo)
        self.occupancy.append(
            TimedData(self.currentOccupancy, end_time)
        )
        self.queueOccupancy.append(
            TimedData(self.currentQueueOccupancy, end_time)
        )
        # OUTPUT DEI RISULTATI
        print('\n\n*** QUEUE STATS ***')
        print('Simulation ran from t0 = %d to t1 = %d' % (start_time, end_time))
        # Clienti rimasti all'interno del sistema
        print('At the moment, there are %d clients in the system (%d in the queuing line)' % (n_users, n_users_ql))
        # Statistiche sulle richieste: totali, accettate, rifiutate ed elaborate
        print('\nRequests that have not reached the system:')
        print('- %d (%s %%) now' % (req_not_arrived, req_not_arrived_perc))
        print('- %d (%s %%) in total' % (req_not_arrived_tot, req_not_arrived_perc_tot))
        print('Received requests:')
        print('- %d (%s %%) now' % (req_arrived, req_arrived_perc))
        print('- %d (%s %%) in total' % (req_arrived_tot, req_arrived_perc_tot))
        # Statistiche specifiche del batch
        if req_arrived > 0:
            print('\n-- LOCAL RESULTS --')
            print('About received requests:')
            print('- %d have been accepted (%s %%)' % (req_accepted, req_accepted_perc))
            print('- %d have been rejected (%s %%)' % (req_rejected, req_rejected_perc))
            print('=> %d over %d (%s %%) accepted requests have been served correctly' %
                  (req_served, req_accepted, req_served_perc))
            # Occupazione media di sistema e QL
            print('\nAverage number of clients into the queuing line: %s' % self.current_batch().get_N_W())
            print('Average number of clients into the server(s): %s' % self.current_batch().get_N_S())
            print('=> Average number of clients into the queue system: %s' % self.current_batch().get_N())
            # Tempi medi di attesa ed elaborazione
            print('\nWithout considering the client requests still in the queuing line and/or into the server(s): ')
            print('- Mean value for the waiting time, into the queuing line: %s' % self.current_batch().get_T_W())
            print('- Mean value for the service time, into a server: %s (only for served ones)' %
                  self.current_batch().get_T_S())
            # NOTA: questo valore e' calcolato considerando solo parte dei waiting time (ovvero, quelli per richieste
            # che sono state servite correttamente
            print('- Mean value for the traversing time, into the queue system: %s (only for served ones)' %
                  self.current_batch().get_T())
        # Statistiche globali del sistema, nel corso delle varie simulazioni
        if req_arrived_tot > req_arrived:
            print('\n-- GLOBAL RESULTS --')
            print('About all the received requests:')
            print('- %d have been accepted (%s %%)' % (req_accepted_tot, req_accepted_perc_tot))
            print('- %d have been rejected (%s %%)' % (req_rejected_tot, req_rejected_perc_tot))
            print('=> %d over %d (%s %%) accepted requests have been served correctly' %
                  (req_served_tot, req_accepted_tot, req_served_perc_tot))
            # Occupazione media di sistema e QL
            print('\nAverage number of clients into the queuing line: %s' % self._globalStats.get_N_W())
            print('Average number of clients into the server(s): %s' % self._globalStats.get_N_S())
            print('=> Average number of clients into the queue system: %s' % self._globalStats.get_N())
            # Tempi medi di attesa ed elaborazione
            print('\nWithout considering the client requests still in the queuing line and/or into the server(s): ')
            print('- Mean value for the waiting time, into the queuing line: %s' % self._globalStats.get_T_W())
            print('- Mean value for the service time, into a server: %s (only for served ones)' %
                  self._globalStats.get_T_S())
            # NOTA: questo valore e' calcolato considerando solo parte dei waiting time (ovvero, quelli per richieste
            # che sono state servite correttamente
            print('- Mean value for the traversing time, into the queue system: %s (only for served ones)' %
                  self._globalStats.get_T())
        # GRAFICI
        if graphs:
            self.plots()

    def plots(self):
        """
        Stampa a schermo i grafici richiesti
        """
        # Utenti nel sistema
        fig_users_sys, area_users_sys = qs_plots.figure(title='Clients in the system')
        qs_plots.step_plot2(area_users_sys, self.occupancy.get_time_list(), self.occupancy.get_data_list(),
                            'Time units', 'Number of clients')
        # Utenti nella queuing line
        fig_users_queue, area_users_queue = qs_plots.figure(title='Clients in the queuing line')
        qs_plots.step_plot2(area_users_queue, self.queueOccupancy.get_time_list(),
                            self.queueOccupancy.get_data_list(),
                            'Time units', 'Number of clients', style='c')
        # Tempi di attesa in QL
        fig_time_queue, area_time_queue = qs_plots.figure(title='Waiting time per request, in the queuing line')
        qs_plots.plot2(area_time_queue, self.waitedFor.get_data_list(), self.waitedFor.get_time_list(),
                       'Request ID', 'Time units', style='g--o', missing=True)
        # Tempi di elaborazione nei server
        fig_time_service, area_time_service = qs_plots.figure(title='Service time per request, into a server')
        qs_plots.plot2(area_time_service, self.servedIn.get_data_list(), self.servedIn.get_time_list(),
                       'Request ID', 'Time units', style='y--o', missing=True)
        # Stime correnti e globali per i valor medi di occupazione
        fig_avg_occupancy, area_avg_occupancy = qs_plots.figure(title='Occupancy average values')
        local_occs = [self.current_batch().get_N(),
                      self.current_batch().get_N_W(),
                      self.current_batch().get_N_S()]
        global_occs = [self._globalStats.get_N(),
                       self._globalStats.get_N_W(),
                       self._globalStats.get_N_S()]
        qs_plots.bar(area_avg_occupancy, [0, 3, 6], local_occs, 'N, N_W and N_S avg. values', '#Requests',
                     legend_label='Current batch', color='b')
        qs_plots.bar(area_avg_occupancy, [1, 4, 7], global_occs, 'N, N_W and N_S avg. values', '#Requests',
                     legend_label='Global values', color='c')
        # Stime correnti e globali per i timing delle richieste
        fig_avg_timing, area_avg_timing = qs_plots.figure(title='Time average values')
        local_times = [self.current_batch().get_T(),
                       self.current_batch().get_T_W(),
                       self.current_batch().get_T_S()]
        global_times = [self._globalStats.get_T(),
                        self._globalStats.get_T_W(),
                        self._globalStats.get_T_S()]
        qs_plots.bar(area_avg_timing, [0, 3, 6], local_times, 'T, T_W and T_S avg. values', 'Time units',
                     legend_label='Current batch', color='r')
        qs_plots.bar(area_avg_timing, [1, 4, 7], global_times, 'T, T_W and T_S avg. values', 'Time units',
                     legend_label='Global values', color='m')
        # Stampo a schermo tutti i grafici
        qs_plots.show()

    def update_end_time(self, until):
        """
        La funzione aggiorna il valore di fine simulazione
        """
        self.current_batch().set_end_time(until)
        self._globalStats.set_end_time(until)

    def accept_requests(self, n):
        """
        Segnala che il sistema ha accettato n richieste utente per l'elaborazione, mettendole in coda
        """
        self.new_requests(n)
        self.update_occupancy(n)
        self.update_queue_occupancy(n)

    def new_requests(self, n):
        """
        Segnala l'arrivo di n nuove richieste al sistema coda
        """
        self.current_batch().increment_total_requests(n)
        self._globalStats.increment_total_requests(n)
        self.next_request_id += n

    def reject_requests(self, n):
        """
        Segnala che n richieste sono arrivate al sistema, ma sono state perse perche' pieno
        """
        self.new_requests(n)
        self.current_batch().increment_lost_requests(n)
        self._globalStats.increment_lost_requests(n)

    def unarrived_requests(self, n):
        """
        La funzione segnala che n richieste non sono giunte al sistema coda
        """
        self.current_batch().increment_not_arrived_requests(n)
        self._globalStats.increment_not_arrived_requests(n)

    def satisfied_requests(self, n):
        """
        La funzione segnala che n richieste sono state correttamente servite
        """
        self.current_batch().increment_satisfied_requests(n)
        self._globalStats.increment_satisfied_requests(n)
        self.update_occupancy(-n)

    def update_occupancy(self, n):
        """
        Aggiorna il numero di utenti nel sistema: ho degli arrivi se n > 0, partenze se n < 0 
        """
        self.current_batch().increment_final_occupancy(n)
        self._globalStats.increment_final_occupancy(n)
        self.currentOccupancy += n

    def update_queue_occupancy(self, n):
        """
        Aggiorna il numero di utenti nella sola queuing line: ho degli arrivi se n > 0, partenze se n < 0 
        """
        self.current_batch().increment_final_queue_occupancy(n)
        self._globalStats.increment_final_queue_occupancy(n)
        self.currentQueueOccupancy += n

    def response_time_confidence_interval(self, confidence_level):
        """
        La funzione ritorna l'intervallo di confidenza associato ai valori di "T", stimati per i vari batch di 
        simulazione, con il livello di confidenza desiderato "confidence_level"
        NOTA: il primo batch viene escluso, per non considerare il periodo di transitorio
        """
        values = map(lambda x: x.get_T(), self._batchStats[1:])
        return confidence_interval(values, confidence_level)

    def buffer_occupancy_confidence_interval(self, confidence_level):
        """
        La funzione ritorna l'intervallo di confidenza associato ai valori di "N_W", stimati per i vari batch di 
        simulazione, con il livello di confidenza desiderato "confidence_level"
        NOTA: il primo batch viene escluso, per non considerare il periodo di transitorio
        """
        values = map(lambda x: x.get_N_W(), self._batchStats[1:])
        return confidence_interval(values, confidence_level)

    def rejected_requests_confidence_interval(self, confidence_level):
        """
        La funzione ritorna l'intervallo di confidenza associato ai valori di "lost_requests", stimati per i vari 
        batch di simulazione, con il livello di confidenza desiderato "confidence_level"
        NOTA: il primo batch viene escluso, per non considerare il periodo di transitorio
        """
        values = map(lambda x: x.get_lost_requests(), self._batchStats[1:])
        return confidence_interval(values, confidence_level)

    def confidence_intervals(self, confidence_level):
        """
        La funzione ricava gli intervalli di confidenza per response time, buffer occupancy e rejected requests, 
        specificando "confidence_level" come livello di confidenza desiderato. Le informazioni ottenute vengono
        stampate a schermo
        """
        print('\n\n*** CONFIDENCE INTERVALS ***')
        rt = self.response_time_confidence_interval(confidence_level)
        bo = self.buffer_occupancy_confidence_interval(confidence_level)
        rr = self.rejected_requests_confidence_interval(confidence_level)
        print('Desired confidence level is %.2f %%' % (confidence_level * 100))
        print('Response time confidence interval: (%.2f, %.2f)' % rt)
        print('Buffer occupancy confidence interval: (%.2f, %.2f)' % bo)
        print('Rejected requests confidence interval: (%.2f, %.2f)' % rr)


def mean(array):
    """
    Calcola la media di un vettore "array"
    """
    # Controllo dell'input, tramite eccezioni
    if len(array) > 0:
        try:
            m = round(numpy.mean(array), 2)
        except TypeError:
            raise TypeError('"array" parameter must be an array of numbers')
    else:
        m = 'N/A'
    # Risultato
    return m


def integral_mean(t_array, end_time):
    """
    Calcola la media integrale di un TimedArray "tArray" (peso i valori "data" a seconda dell'intervallo "time" a 
    loro associato)
    Per il momento, la funzione e' pensata per TimedArray con timestamp = False
    """
    # Controllo dell'input
    try:
        ic.check_timed_array(t_array, 'tArray')
        s = 0.0
        total_time = 0.0
        prev_time = 0.0
        prev_value = 0.0
        val = 0.0
        has_intervals = t_array.has_time_intervals()
        for x in t_array.get_list():
            # Ricavo i campi dell'elemento in analisi
            t = x.get_time()
            d = x.get_data()
            # Il vettore puo' contenere intervalli o timestamp
            # Nel secondo caso, devo computare l'intervallo di tempo trascorso
            if not has_intervals:
                time_interval = t - prev_time
                val = prev_value
                prev_time = float(t)
                prev_value = d
            else:
                time_interval = t
            # Quindi, aggiorno i valori di somma e tempo totale
            total_time += time_interval
            s += val * time_interval
        # Ultimo dato
        total_time += end_time - prev_time
        s += prev_value * (end_time - prev_time)
        # Risultato
        m = round(s / total_time, 2)
    except TypeError:
        m = 'N/A'
    return m


def print_mean(array, msg=''):
    """
    Calcola la media di un TimedArray "tArray" e la stampa a schermo, preceduta dal messaggio "msg"
    """
    m = mean(array)
    print(str(msg) + ': ' + str(m))


def print_integral_mean(array, end_time, msg=''):
    """
    Calcola la media integrale di un vettore "array" e la stampa a schermo, preceduta dal messaggio "msg"
    """
    m = integral_mean(array, end_time)
    print(str(msg) + ': ' + str(m))


def _perc(a, b):
    """
    Funzione di utility: fa il rapporto tra "a" e "b", ritornandone la percentuale a due cifre
    """
    return 'N/A' if b == 0 else round(100.0 * a / b, 2)


def confidence_interval(values, conf_interval):
    """
    Calcola un intervallo di confidenza per la stima di un valor medio, secondo la ddp Student's t
    """
    # Numero di campioni
    n = len(values)
    # Valor medio
    m = mean(values)
    # Deviazione standard
    s = numpy.std(values)
    # Degrees of freedom
    df = n - 1
    # Quantile Student's t: t_n-1,alpha/2
    return students_t.interval(conf_interval, df, loc=m, scale=s)
