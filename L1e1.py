# LAB 01 - ex 1

import queue_system as QS
import input_controls as ic
import random


def decor(msg):
    print('*** ' + msg + ' ***')


SIM_TIME = 100
BATCHES = 24
SEED = 11
# Per rendere l'esperimento ripetibile
random.seed(SEED)

# PRIMA CODA: Q1
FOUT_1 = 'res01.txt'
decor('Init the first queue (M/M/1)')
q1 = QS.QueueSystem(log_file=FOUT_1)
q1.run(SIM_TIME)

# Voglio ora valutare intervalli di confidenza per Q1: 90% e 99%
for t in range(BATCHES):
    q1.run(SIM_TIME * (t+2), graphs=False)
q1.confidence_intervals(0.9)
q1.confidence_intervals(0.99)

# Grafici finali
q1.plots()

pass


# SECONDA CODA: Q2
random.seed(SEED)
FOUT_2 = 'res02.txt'
print('\n\n')
decor('Init the second queue (Mx/M/1/B)')
B = ic.input_int('Insert the buffer capacity (a positive integer value)', 0)
x_min = ic.input_int('Insert the minimum size of a batch (positive integer value)', 1)
x_max = ic.input_int('Insert the maximum size of a batch (positive integer value)', x_min)
q2 = QS.QueueSystem(capacity=B, batches=(x_min, x_max), log_file=FOUT_2)
q2.run(SIM_TIME)

# Voglio ora valutare intervalli di confidenza per Q1: 90% e 99%
for t in range(BATCHES):
    q2.run(SIM_TIME * (t+2), graphs=False)
q2.confidence_intervals(0.9)
q2.confidence_intervals(0.99)

# Grafici finali
q2.plots()
