# MyCPUPowerLinux

Python helper that sets the Linux CPU frequency governor to `performance` and turns on boost or Intel turbo. It is a port of a short `cpupower` / sysfs shell script, with Intel `intel_pstate` support and a log file next to the script.

The script re-runs itself with `sudo` when it is not already root. A real run changes CPU power settings on the machine.

## Requirements

- Linux
- Python 3 (standard library only)
- `sudo`
- `cpupower` from `kernel-tools` (Fedora/RHEL: `sudo dnf install kernel-tools`; Debian/Ubuntu: `sudo apt install linux-tools-generic` or `linux-cpupower`)

If `cpupower` is missing, the script falls back to writing `performance` to each CPU's `/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`.

## Usage

```bash
chmod +x cpu_performance.py
./cpu_performance.py
```

Or:

```bash
python3 cpu_performance.py
```

You can also start it as root:

```bash
sudo python3 cpu_performance.py
```

## Intel vs AMD

The script reads `/sys/devices/system/cpu/cpu0/cpufreq/scaling_driver` and then enables boost the way that driver expects:

| Driver | Boost / turbo |
| --- | --- |
| `intel_pstate` | Writes `0` to `/sys/devices/system/cpu/intel_pstate/no_turbo` (Intel turbo on). |
| Anything else (`acpi-cpufreq`, AMD `amd-pstate`, and similar) | Writes `1` to `/sys/devices/system/cpu/cpufreq/boost`. |

If the boost or turbo file is missing, that step is skipped and the reason is logged. The governor is still set.

## Verify boost

Use `cpupower frequency-info` to check whether your CPU supports boost and whether it is active:

```bash
cpupower frequency-info
```

Look for the `boost state support` section in the output. `Supported: yes` means the CPU and driver can boost, and `Active: yes` means boost is on. Run it before and after the script to confirm the change. The `current policy` line also shows the active governor, which should read `performance`.

## Log file

Actions, the detected driver, and errors are printed to the console and appended to `cpu_performance.log` in the same directory as the script. The log is ignored by git.
