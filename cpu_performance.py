#!/usr/bin/env python3
"""Set the CPU governor to performance and enable CPU boost or Intel turbo."""
import logging
import os
import subprocess
import sys
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent / "cpu_performance.log"
DRIVER_PATH = Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_driver")
BOOST_PATH = Path("/sys/devices/system/cpu/cpufreq/boost")
INTEL_NO_TURBO_PATH = Path("/sys/devices/system/cpu/intel_pstate/no_turbo")
CPU_ROOT = Path("/sys/devices/system/cpu")


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def ensure_root():
    if os.geteuid() != 0:
        logging.info("Not running as root; re-running with sudo...")
        os.execvp("sudo", ["sudo", sys.executable, *sys.argv])


def detect_driver():
    if not DRIVER_PATH.exists():
        logging.warning("Scaling driver path not found: %s", DRIVER_PATH)
        return None
    try:
        driver = DRIVER_PATH.read_text().strip()
    except OSError as e:
        logging.error("Could not read scaling driver from %s: %s", DRIVER_PATH, e)
        return None
    logging.info("Detected scaling driver: %s", driver or "(empty)")
    return driver


def set_governor(governor="performance"):
    try:
        subprocess.run(["cpupower", "frequency-set", "-g", governor], check=True)
        logging.info("CPU governor set to %s via cpupower.", governor)
        return
    except FileNotFoundError:
        logging.warning(
            "cpupower not found; falling back to sysfs scaling_governor."
        )
    except subprocess.CalledProcessError as e:
        logging.error("cpupower failed with exit code %s.", e.returncode)
        sys.exit(e.returncode)

    governors = sorted(CPU_ROOT.glob("cpu[0-9]*/cpufreq/scaling_governor"))
    if not governors:
        logging.error("No scaling_governor files found; cannot set governor.")
        sys.exit(1)
    for path in governors:
        try:
            path.write_text(governor)
            logging.info("Wrote %s to %s.", governor, path)
        except OSError as e:
            logging.error("Could not write %s to %s: %s", governor, path, e)
            sys.exit(1)


def enable_boost(driver):
    if driver == "intel_pstate":
        path = INTEL_NO_TURBO_PATH
        value = "0"
        label = "Intel turbo (no_turbo=0)"
    else:
        path = BOOST_PATH
        value = "1"
        label = "CPU boost"

    if not path.exists():
        logging.warning("%s not found; skipping %s.", path, label)
        return
    try:
        path.write_text(value)
        logging.info("Enabled %s by writing %s to %s.", label, value, path)
    except OSError as e:
        logging.error("Could not enable %s: %s", label, e)
        sys.exit(1)


def main():
    setup_logging()
    ensure_root()
    driver = detect_driver()
    set_governor()
    enable_boost(driver)
    logging.info("Done.")


if __name__ == "__main__":
    main()
