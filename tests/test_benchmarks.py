import pytest

from multiaddr import Multiaddr

BENCH_ADDR = "/ip4/127.0.0.1/tcp/4001/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC"


@pytest.mark.benchmark
def test_bench_from_string(benchmark):
    benchmark(Multiaddr, BENCH_ADDR)


@pytest.mark.benchmark
def test_bench_to_string(benchmark):
    ma = Multiaddr(BENCH_ADDR)
    benchmark(str, ma)


@pytest.mark.benchmark
def test_bench_to_bytes(benchmark):
    ma = Multiaddr(BENCH_ADDR)
    benchmark(ma.to_bytes)


@pytest.mark.benchmark
def test_bench_protocols(benchmark):
    ma = Multiaddr(BENCH_ADDR)
    benchmark(lambda: list(ma.protocols()))


@pytest.mark.benchmark
def test_bench_encapsulate(benchmark):
    ma1 = Multiaddr("/ip4/1.2.3.4")
    ma2 = Multiaddr("/tcp/80")
    benchmark(ma1.encapsulate, ma2)


@pytest.mark.benchmark
def test_bench_decapsulate(benchmark):
    ma = Multiaddr("/ip4/1.2.3.4/tcp/80")
    benchmark(ma.decapsulate, "/tcp/80")
