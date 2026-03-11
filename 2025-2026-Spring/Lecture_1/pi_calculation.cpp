// C++ — Sequential Pi: compiled baseline
// ~10-20x faster than Python: compiled, typed, no interpreter overhead
#include <cstdlib>
#include <chrono>
#include <cstdio>
#include <random>

double estimate_pi(long n) {
    std::mt19937_64 rng(std::random_device{}());
    std::uniform_real_distribution<double> dist(0.0, 1.0);

    long inside = 0;
    for (long i = 0; i < n; i++) {
        double x = dist(rng);
        double y = dist(rng);
        if (x*x + y*y <= 1.0) inside++;
    }
    return 4.0 * inside / n;
}

int main() {
    const long N = 10'000'000;

    auto start = std::chrono::high_resolution_clock::now();
    double pi = estimate_pi(N);
    auto end   = std::chrono::high_resolution_clock::now();

    double elapsed = std::chrono::duration<double>(end - start).count();
    std::printf("Pi ≈ %.6f  |  n = %ld  |  time = %.3fs\n", pi, N, elapsed);
    return 0;
}
