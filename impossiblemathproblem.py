import numpy as np
import pandas as pd
import scipy as sp
import math
import matplotlib
import matplotlib.pyplot as plt

from pylab import *

matplotlib.rcParams['figure.figsize'] = (12,12)
matplotlib.rcParams.update({'font.size':22})
matplotlib.rc('xtick', labelsize = 14)
matplotlib.rc('ytick', labelsize = 14)

stop = 1000
out = pd.DataFrame({"Start":np.zeros(stop-1), "Count":np.zeros(stop-1), "Maximum":np.zeros(stop-1), "Log_Maximum":np.zeros(stop-1)})
i = 2

while i <= stop:
#     print(i)s
    count = 0
    temp = []
    intermediate = i
    while intermediate > 1:
        if intermediate % 2 == 0:
            intermediate = intermediate / 2
        else:
            intermediate = intermediate * 3 + 1
#         print(intermediate)
        temp.append(intermediate)
        count += 1
    out.Start[i-2] = i
    out.Count[i-2] = count
    out.Maximum[i-2] = max(temp)
    out.Log_Maximum[i-2] = math.log(max(temp))
    i+=1

print(out)

figure(1)
plt.plot(out.Start, out.Log_Maximum)
grid(True)
plt.show()