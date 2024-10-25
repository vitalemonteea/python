#Q5
import numpy as np

def calculate_average_capacity(L):
    # Constants
    d = 50
    d0 = 1
    K_dB = -30
    gamma = 4
    K = 10**(K_dB/10)
    F = 2.406735
    Pt = F
    N0B_dBm = -100   
    N0B = 10**(N0B_dBm/10) * 1e-3

    # Calculate average channel gain
    psi_dB = np.random.normal(0, F, L)
    avg_channel_gain_dB = K_dB + 10 * gamma * np.log10(d0/d) + psi_dB
    avg_channel_gain = 10**(avg_channel_gain_dB/10)

    sigma_alpha_squared = np.mean(avg_channel_gain) / 2

    # Generate channel realizations
    h = np.random.normal(0, np.sqrt(sigma_alpha_squared), (L, 2)).view(np.complex128)

    # Calculate capacity
    capacities = np.log2(1 + (Pt * np.abs(h)**2) / N0B)

    # Calculate average capacity
    return np.mean(capacities)

# Calculate for L1
L1 = int(2.406735 * 1e6)
C1 = calculate_average_capacity(L1)
print(f"Average capacity C1 (L1 = {L1}): {C1:.4f} bits/s/Hz")

# Calculate for L2
L2 = int(2.406735 * 1e7)
C2 = calculate_average_capacity(L2)
print(f"Average capacity C2 (L2 = {L2}): {C2:.4f} bits/s/Hz")

# Compare results
print(f"\nDifference between C1 and C2: {abs(C1 - C2):.6f} bits/s/Hz")
print(f"Relative difference: {abs(C1 - C2) / C1 * 100:.6f}%")
