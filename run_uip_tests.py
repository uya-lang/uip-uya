#!/usr/bin/env python3.12
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TEST_DIR = os.path.join(ROOT, "ports/uip/tests")

BASE = ["ports/uip/uip_base.uya"]
TEST_DEPS = {
    "core_primitives_test.uya": ["ports/uip/uip_core.uya"],
    "lc_test.uya": ["ports/uip/uip_proto.uya"],
    "psock_bridge_edge_test.uya": ["ports/uip/uip_proto.uya"],
    "psock_test.uya": ["ports/uip/uip_proto.uya"],
    "pt_migration_demo_test.uya": ["ports/uip/uip_proto.uya"],
    "pt_test.uya": ["ports/uip/uip_proto.uya"],
    "state_and_timer_test.uya": ["ports/uip/uip_core.uya", "ports/uip/uip_proto.uya"],
    "udp_test.uya": ["ports/uip/uip_core.uya", "ports/uip/uip_proto.uya", "ports/uip/uip_arp.uya"],
    "uip_arp_test.uya": ["ports/uip/uip_arp.uya"],
    "uip_core_base_test.uya": ["ports/uip/uip_core.uya", "ports/uip/uip_proto.uya"],
    "uip_fw_test.uya": ["ports/uip/uip_base.uya", "ports/uip/uip_core.uya", "ports/uip/uip_fw_core.uya"],
    "uip_ipv6_basic_test.uya": ["ports/uip/uip_core.uya"],
    "uip_ipv6_neighbor_bridge_test.uya": ["ports/uip/uip_core.uya"],
    "uip_ipv6_neighbor_glue_test.uya": ["ports/uip/uip_neighbor_lib.uya", "ports/uip/uip_ipv6_neighbor_glue.uya", "ports/uip/uip_core.uya"],
    "uip_neighbor_test.uya": ["ports/uip/uip_neighbor_lib.uya", "ports/uip/uip_ipv6_neighbor_glue.uya", "ports/uip/uip_core.uya"],
    "uip_reass_output_test.uya": ["ports/uip/uip_core.uya"],
    "uip_reass_test.uya": ["ports/uip/uip_core.uya"],
    "uip_runtime_features_test.uya": ["ports/uip/uip_core.uya"],
    "uip_split_test.uya": ["ports/uip/uip_base.uya", "ports/uip/uip_core.uya", "ports/uip/uip_fw_core.uya"],
    "uip_stats_logging_test.uya": ["ports/uip/uip_core.uya"],
    "uip_tcp_core_ack_edge_test.uya": ["ports/uip/uip_core.uya", "ports/uip/uip_proto.uya", "ports/uip/uip_arp.uya"],
    "uip_tcp_core_edge_test.uya": ["ports/uip/uip_core.uya", "ports/uip/uip_proto.uya", "ports/uip/uip_arp.uya"],
    "uip_tcp_core_test.uya": ["ports/uip/uip_core.uya", "ports/uip/uip_proto.uya", "ports/uip/uip_arp.uya"],
    "uip_tcp_handshake_test.uya": ["ports/uip/uip_core.uya", "ports/uip/uip_proto.uya", "ports/uip/uip_arp.uya"],
    "uip_tcp_psock_bridge_test.uya": ["ports/uip/uip_core.uya", "ports/uip/uip_proto.uya", "ports/uip/uip_arp.uya"],
    "uip_timer_runtime_test.uya": ["ports/uip/uip_core.uya"],
    "uip_timer_timewait_test.uya": ["ports/uip/uip_core.uya"],
    "uip_urg_runtime_test.uya": ["ports/uip/uip_core.uya"],
    "uiplib_ipaddrconv_test.uya": ["ports/uip/uip_core.uya"],
}


def unique(seq):
    out = []
    for item in seq:
        if item not in out:
            out.append(item)
    return out


def run_one(test_name: str) -> int:
    args = ["./uya/bin/uya", "test", f"ports/uip/tests/{test_name}"]
    deps = TEST_DEPS.get(test_name, ["ports/uip/uip_core.uya"])
    args.extend(unique(BASE + deps))
    print("RUN", test_name)
    proc = subprocess.run(args, cwd=ROOT)
    return proc.returncode


def main() -> int:
    if len(sys.argv) > 1:
        tests = [arg for arg in sys.argv[1:]]
    else:
        tests = sorted(name for name in os.listdir(TEST_DIR) if name.endswith(".uya"))

    failed = []
    for test_name in tests:
        code = run_one(test_name)
        if code != 0:
            failed.append(test_name)

    print()
    print(f"TOTAL: {len(tests)}")
    print(f"FAILED: {len(failed)}")
    for test_name in failed:
        print("FAIL", test_name)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
