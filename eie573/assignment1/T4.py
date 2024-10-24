import numpy as np

# Constants
d = 200  
K = 10**(-30/10)  # K in linear scale (converted from -30 dB)
d0 = 1  
gamma = 3.5  
sigma_psi_dB = np.sqrt(10) 
Pt = 1  
F = 24.067358  

# Convert Pt to dBm
Pt_dBm = 10 * np.log10(Pt * 1000)

# Generate realizations
num_realizations = int(F * 1e7)  # F * 10^7 realizations
psi_dB = np.random.normal(0, sigma_psi_dB, num_realizations)

# Calculate path loss
PL = -(10 * np.log10(K) + 10 * gamma * np.log10(d0/d))

# Calculate received power in dBm for each realization
Pr_dBm = Pt_dBm - PL + psi_dB


# Calculate outage probability for different thresholds
thresholds = np.arange(-90, -60, 5)
for P_min_dBm in thresholds:
    outage_count = np.sum(Pr_dBm < P_min_dBm)
    outage_probability = outage_count / num_realizations
    print(f"Outage Probability (P_min = {P_min_dBm} dBm): {outage_probability:.6f}")
