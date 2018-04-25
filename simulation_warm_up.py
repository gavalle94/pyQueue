import numpy
import queue_system as QS
import random
import qs_plots

# Esperimento per il transitorio
q1 = QS.QueueSystem()  # M/M/1
q2 = QS.QueueSystem(servers=10)  # M/M/10
q3 = QS.QueueSystem(capacity=10)  # M/M/1/10
q4 = QS.QueueSystem(servers=5, capacity=10)  # M/M/5/10
q5 = QS.QueueSystem(batches=(1, 3))  # M/M/1, batch arrivals
q6 = QS.QueueSystem(servers=5, capacity=50, batches=(1, 4))  # M/M/5/50, batch arrivals
queues = [q1, q2, q3, q4, q5, q6]

for qx in queues:
    random.seed(11)
    qx.run(50000, graphs=False)
    R_k = []
    # Valor medio: usiamo il numero di utenti nel sistema come riferimento
    n_users = qx.stats.occupancy.get_data_list()
    x = numpy.mean(n_users)
    # Valor medio depurato dei primi k valori
    for k in range(len(n_users) - 1):
        v = n_users[k + 1:]
        x_k = numpy.mean(v)
        R_k.append((x_k - x) / x)

    # Grafico di R_k
    fig, area = qs_plots.figure(title='Initial data removal')
    qs_plots.plot(area, R_k, 'K', 'R_k')
    qs_plots.show()
