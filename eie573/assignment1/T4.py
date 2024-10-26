import numpy as np

# Constants
F = 2406735*1e-6
d = 200
d0 = 1 
gamma = 3.5  
sigmaPsiDB = np.sqrt(10) 
Pt = 1
K = 10**(-30/10) 

ptDBm = 10 * np.log10(Pt * 1000)

# Calculate PL
PL = (10 * np.log10(K) + 10 * gamma * np.log10(d0/d))

# Generate Psi-db
numRealizations = int(F * 1e7)
psiDB = np.random.normal(0, sigmaPsiDB , numRealizations)

# Calculate received power ina dBm for each realization
prDBm  = ptDBm + PL + psiDB 

# Calculate outage probability for different thresholds
thresholds = np.arange(-90, -60, 5)
for PMinDBm in thresholds:
    outageCount = np.sum(prDBm  < PMinDBm)
    outageProbability = outageCount / numRealizations
    print(f"Outage Probability [PMin = {PMinDBm} dBm]: {outageProbability:.5f}")
