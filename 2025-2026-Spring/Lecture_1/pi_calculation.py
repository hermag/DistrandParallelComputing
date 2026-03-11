import random, time

def estimate_pi_sequential(n_points):
    inside = 0
    for _ in range(n_points):
        x, y = random.random(), random.random()
        if x*x + y*y <= 1.0:
            inside += 1
    return 4.0 * inside / n_points

N = 10_000_000
start = time.perf_counter()
pi = estimate_pi_sequential(N)
elapsed = time.perf_counter() - start
print(f"π ≈ {pi:.6f}  |  time: {elapsed:.3f}s")

