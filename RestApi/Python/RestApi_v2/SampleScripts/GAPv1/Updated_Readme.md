# 📏 Gap Theorem Calibration Tool

## 🚀 Overview
The **Gap Theorem Calibration Tool** is a network traffic calibration utility designed to achieve precise control over **Average Packet Size (APS)** in network testing. By leveraging a mathematical approach, this tool determines the optimal traffic mix between two components with different packet sizes to achieve a desired target APS.

## 📖 The Gap Theorem
The **Gap Theorem** provides a systematic method for achieving a target **Average Packet Size (APS)** by combining traffic from two distinct packet-size components. It ensures:
- A predictable and **controlled APS** for network testing.
- A systematic method for **calibrating** network traffic.
- A precise balance between **small and large packets** to reach the desired APS.

## ✨ Features
✔️ **Automated Calibration** – Dynamically adjusts low and high components.  
✔️ **Validation Testing** – Ensures the calibration accuracy through verification tests.  
✔️ **Comprehensive Reporting** – Generates detailed test reports.  
✔️ **Logging** – Saves all test results in `reports/calibration_validation.log`.  
✔️ **Error Handling** – Detects and manages test failures seamlessly.  

## 🛠️ Usage

### 📌 Prerequisites
- Python **3.6+**
- **BreakingPoint API** access
- Network test components with **different packet sizes**

### 🔧 Basic Usage
```python
from gap_theorem_oop import GapTheoremCalibrator

# Initialize the calibrator
calibrator = GapTheoremCalibrator(
    bps_system="10.36.66.31",
    username="admin",
    password="admin",
    port=443,
    test_name="GapTheoremTest",
    aps_desired=512.0,
    total_throughput=30000.0
)

# Run the full calibration process
calibrator.run_calibration()

# Generate and print the report
report = calibrator.generate_full_report()
print(report)
```

### ⚙️ Advanced Usage
```python
# Custom settings with component specification
calibrator = GapTheoremCalibrator(
    bps_system="10.36.66.31",
    username="admin",
    password="admin",
    port=443,
    test_name="CustomTest",
    aps_desired=1024.0,
    total_throughput=20000.0,
    low_component="SmallPackets",
    high_component="LargePackets",
    samples_required=100,
    steady_state_threshold=0.95
)

# Run individual steps
calibrator.calibrate_low_component()
calibrator.calibrate_high_component()
calibrator.run_validation_test("final")

# Generate report
report = calibrator.generate_full_report()
```

## 📥 Input Parameters
| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `bps_system` | IP address of the BreakingPoint system | None | ✅ |
| `username` | Username for BreakingPoint authentication | None | ✅ |
| `password` | Password for BreakingPoint authentication | None | ✅ |
| `port` | Port for BreakingPoint API | 443 | ❌ |
| `test_name` | Name of the test to load | None | ✅ |
| `aps_desired` | Target Average Packet Size (bytes) | None | ✅ |
| `total_throughput` | Total throughput (Mbps) | None | ✅ |
| `low_component` | Name of the low APS component | Auto-detected | ❌ |
| `high_component` | Name of the high APS component | Auto-detected | ❌ |
| `samples_required` | Number of samples required for calibration | 50 | ❌ |
| `steady_state_threshold` | Threshold for steady-state detection | 0.95 | ❌ |

## 📤 Output
### 📝 Calibration Results
✅ **Average Packet Size**  
✅ **Throughput Measurements**  
✅ **Collected Data Points**  
✅ **Frame Size Range**  
✅ **Test ID & Validation**  

### 🛠️ Validation Results
| Metric | Value |
|--------|-------|
| 🎯 **Target APS** | 512.00 B |
| 📏 **Measured APS** | 512.00 B |
| ⚖ **Tolerance** | ±5% |
| 📊 **Samples Collected** | 92 |
| ⏳ **Test Duration** | 120 sec |

### 📈 Test Results
| Test ID | Low Component | High Component | Validation |
|---------|--------------|---------------|------------|
| **Throughput (Mbps)** | 1,117.00 (calculated) | 11,709.00 (calculated) | RX: 29,445.15 |
| **Measured Values** | 12,826.26 Mbps | 29,445.15 Mbps | TX: 29,445.15 |
| **APS** | 64.00 B | 1,500.00 B | 512.00 B |
| **Status** | ✅ Complete | ✅ Complete | ✅ Passed |

### 📊 Validation Summary
✔ **APS Deviation**: **0.00 B (0.0%)**  
📜 **Log File**: All results stored in `reports/calibration_validation.log`  

## 🛠️ Troubleshooting
### 🔍 Common Issues & Fixes
🔸 **Component Detection Failure**  
✔ Ensure component names contain `"low"/"small"` or `"high"/"large"`.  
✔ Manually specify component names if auto-detection fails.  

🔸 **Zero Throughput Values**  
✔ Check network connectivity.  
✔ Verify test configuration.  
✔ Ensure minimum throughput is at least **1.0 Mbps**.  

🔸 **Missing Data in Report**  
✔ Run calibration for both components before validation.  
✔ Verify steady state was reached.  

### 🐞 Debugging Tips
✔ Set `debug=True` in the calibrator for **verbose logging**.  
✔ Check raw test results in `calibration_results`.  
✔ Examine the log file for detailed errors.  

## 🏆 Best Practices
- Use tests with **clearly different** packet sizes for low/high components.  
- Ensure both components generate **stable traffic**.  
- Set throughput within **realistic network capabilities**.  
- Always **run validation** after calibration.  
- Ensure **APS deviation** is under **5%** for accuracy.  

## 📜 License
This tool is provided under the **MIT License**. See `LICENSE` for details.  
