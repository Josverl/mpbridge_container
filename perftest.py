"""
Performance test comparing socket and rfc2217 connections for mpremote.
Tests simple and complex scripts on both connection types.
"""

import statistics
import subprocess
import time

# Connection configurations
CONNECTIONS = {
    "socket": "socket://localhost:2218",
    "rfc2217": "rfc2217://localhost:2217",
}

# Test scripts
SCRIPTS = {
    "simple_print": "print('Hello')",
    "simple_math": "x = sum(range(100)); print(x)",
    "loop_small": "for i in range(10): print(i)",
    "loop_large": "for i in range(100): pass; print('done')",
    "complex_list": "data = [i**2 for i in range(50)]; print(len(data))",
    "complex_dict": "d = {str(i): i**2 for i in range(50)}; print(len(d))",
    "nested_loops": "total = 0\nfor i in range(10):\n    for j in range(10):\n        total += i * j\nprint(total)",
    "string_ops": "s = 'test' * 100; print(len(s))",
}

NUM_ITERATIONS = 5


def run_mpremote(connection: str, script: str) -> tuple[float, bool]:
    """Run mpremote with the given connection and script, return (duration, success)."""
    cmd = ["mpremote", "connect", connection, "exec", script]
    start = time.perf_counter()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        end = time.perf_counter()
        success = result.returncode == 0
        return (end - start, success)
    except subprocess.TimeoutExpired:
        return (30.0, False)
    except Exception as e:
        print(f"Error: {e}")
        return (0.0, False)


def run_tests():
    """Run all performance tests."""
    results = {}

    print("=" * 70)
    print("MPREMOTE PERFORMANCE TEST")
    print("Comparing socket vs rfc2217 connections")
    print(f"Iterations per test: {NUM_ITERATIONS}")
    print("=" * 70)
    print()

    for script_name, script_code in SCRIPTS.items():
        print(f"\nTest: {script_name}")
        print(f"  Code: {script_code[:50]}{'...' if len(script_code) > 50 else ''}")
        print("-" * 50)

        results[script_name] = {}

        for conn_name, conn_url in CONNECTIONS.items():
            times = []
            failures = 0

            for i in range(NUM_ITERATIONS):
                duration, success = run_mpremote(conn_url, script_code)
                if success:
                    times.append(duration)
                else:
                    failures += 1

            if times:
                avg_time = statistics.mean(times)
                min_time = min(times)
                max_time = max(times)
                std_dev = statistics.stdev(times) if len(times) > 1 else 0

                results[script_name][conn_name] = {
                    "avg": avg_time,
                    "min": min_time,
                    "max": max_time,
                    "std": std_dev,
                    "failures": failures,
                }

                print(
                    f"  {conn_name:10}: avg={avg_time:.3f}s  min={min_time:.3f}s  max={max_time:.3f}s  std={std_dev:.3f}s  failures={failures}"
                )
            else:
                results[script_name][conn_name] = {"failures": NUM_ITERATIONS}
                print(f"  {conn_name:10}: ALL FAILED")

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    socket_total = 0
    rfc2217_total = 0
    socket_count = 0
    rfc2217_count = 0

    for script_name, conn_results in results.items():
        if "socket" in conn_results and "avg" in conn_results["socket"]:
            socket_total += conn_results["socket"]["avg"]
            socket_count += 1
        if "rfc2217" in conn_results and "avg" in conn_results["rfc2217"]:
            rfc2217_total += conn_results["rfc2217"]["avg"]
            rfc2217_count += 1

    if socket_count > 0 and rfc2217_count > 0:
        socket_avg = socket_total / socket_count
        rfc2217_avg = rfc2217_total / rfc2217_count

        print(f"\nOverall average execution time:")
        print(f"  socket:  {socket_avg:.3f}s")
        print(f"  rfc2217: {rfc2217_avg:.3f}s")

        if socket_avg < rfc2217_avg:
            pct = ((rfc2217_avg - socket_avg) / rfc2217_avg) * 100
            print(f"\n  => socket is {pct:.1f}% faster than rfc2217")
        else:
            pct = ((socket_avg - rfc2217_avg) / socket_avg) * 100
            print(f"\n  => rfc2217 is {pct:.1f}% faster than socket")

    print()


if __name__ == "__main__":
    run_tests()
