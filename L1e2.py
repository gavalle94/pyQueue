# LAB 01 - ex 2

import queue_system as QS
import input_controls as ic


def decor(msg):
    print('*** ' + msg + ' ***')


SIM_TIME = 100
P = 0.1

# Crea la prima coda
FOUT_1 = 'res01.txt'
decor('Init the first queue (Mx/M/1/B)')
B = ic.input_int('Insert the buffer capacity (a positive integer value)', 0)
x_min = ic.input_int('Insert the minimum size of a batch (positive integer value)', 1)
x_max = ic.input_int('Insert the maximum size of a batch (positive integer value)', x_min)
q1 = QS.QueueSystem(capacity=B, batches=(x_min, x_max), log_file=FOUT_1)

# Crea la seconda coda
FOUT_2 = 'res02.txt'
print('\n\n')
decor('Init the second queue (Chain/M/1/B)')
B = ic.input_int('Insert the buffer capacity (a positive integer value)', 0)
q2 = QS.QueueSystem(arrivals='Chain', capacity=B, log_file=FOUT_2)

# Concatena le code in un unico sistema
sys = QS.ChainedQueueSystem([q1, q2], [P])
# Lancia la simulazione
sys.run(SIM_TIME)
