#Q5
import numpy as np

def calculateAverageCapacity(L):
    # Constants
    F = 2406735*1e-6
    d = 50
    d0 = 1
    K_dB = -30
    gamma = 4
    Pt = F
    N0B_DBm = -100  
    N0B = 10**(N0B_DBm/10) * 1e-3
    
    # Calculate average channel gain
    psiDB = np.random.normal(0, F, L)
    avgChannelGain0 = K_dB + 10 * gamma * np.log10(d0/d) + psiDB
    avgChannelGain= 10**(avgChannelGain0/10)
    sigmaAlphaSquared = np.mean(avgChannelGain) / 2

    # Generate channel realizations
    H = np.random.normal(0, np.sqrt(sigmaAlphaSquared), (L, 2)).view(np.complex128)

    # Calculate capacity
    capacities = np.mean(np.log2(1 + (Pt * np.abs(H)**2) / N0B))

    return capacities

# Calculate for L1
L1 = int(2.406735 * 1e6)
C1 = calculateAverageCapacity(L1)
print(f"Average capacity C1 = {C1:.6f} bps/Hz")

# Calculate for L2
L2 = int(2.406735 * 1e7)
C2 = calculateAverageCapacity(L2)
print(f"Average capacity C2 = {C2:.6f} bps/Hz")

# Compare results
print(f"\nDifference between C1 and C2: {abs(C1 - C2):.6f} bps/Hz")
print(f"Relative difference: {abs(C1 - C2) / C1 * 100:.6f}%")
