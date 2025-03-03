Gap Theorem Calibration Tool
Overview
This tool implements the Gap Theorem for network traffic calibration, allowing precise control over Average Packet Size (APS) in network testing. It uses a mathematical approach to calculate the optimal traffic mix between two components with different packet sizes to achieve a desired target APS.
Gap Theorem Explained
The Gap Theorem provides a mathematical model for achieving a specific Average Packet Size (APS) by mixing traffic from two components with different packet sizes:
Principle: By combining traffic from a "low APS" component and a "high APS" component in the right proportions, any target APS between them can be achieved.
Formula:
Tput_high = (APS_high * (APS_desired - APS_low)) / (APS_desired * (APS_high - APS_low)) * Tput_total
Tput_low = (APS_low * (APS_high - APS_desired)) / (APS_desired * (APS_high - APS_low)) * Tput_total
Variables:
APS_low: Average packet size of the low component
APS_high: Average packet size of the high component
APS_desired: Target average packet size
Tput_total: Total throughput (sum of both components)
Tput_low: Calculated throughput for low component
Tput_high: Calculated throughput for high component
Features
Automated Calibration: Automatically calibrates low and high components
Validation Testing: Validates the calibration with a combined test
Detailed Reporting: Generates comprehensive reports with all test metrics
Log File Generation: Saves all test results to reports/calibration_validation.log
Error Handling: Robust error handling for test failures
Usage
Prerequisites
Python 3.6+
BreakingPoint API access
Network test components with different packet sizes
Basic Usage
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
Advanced Usage

# Initialize with custom components and settings
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

Input Parameters
| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| bps_system | IP address of the BreakingPoint system | None | Yes |
| username | Username for BreakingPoint authentication | None | Yes |
| password | Password for BreakingPoint authentication | None | Yes |
| port | Port for BreakingPoint API | 443 | No |
| test_name | Name of the test to load | None | Yes |
| aps_desired | Target Average Packet Size in bytes | None | Yes |
| total_throughput | Total throughput in Mbps | None | Yes |
| low_component | Name of the low APS component | Auto-detected | No |
| high_component | Name of the high APS component | Auto-detected | No |
| samples_required | Number of samples required for calibration | 50 | No |
| steady_state_threshold | Threshold for steady state detection | 0.95 | No |
Output
Calibration Results
The tool produces a comprehensive report with the following sections:
Calibration Results
Average Packet Size
Throughput
Data Points Collected
Frame Data Rate Range
Frame Size Range
Test ID
Validation Results
Target APS
Measured APS
Tolerance (±5%)
Samples Collected
Test Duration
Gap Theorem Calculation
Formulas used
Values used in calculation
Test Results
Test IDs for low, high, and validation tests
Throughput values (calculated and measured)
Average Packet Size for each test
Status of each test
Validation Summary
APS Deviation (absolute and percentage)
Log File
All test results are saved to reports/calibration_validation.log with timestamps for easy reference.
Troubleshooting
Common Issues
Component Detection Failure
Ensure component names contain "low"/"small" or "high"/"large"
Manually specify component names if auto-detection fails
Zero Throughput Values
Check network connectivity
Verify test configuration
Ensure minimum throughput values are at least 1.0 Mbps
Missing Data in Report
Run calibration for both components before validation
Check for errors in the console output
Verify that steady state was reached during tests
Debug Tips
Set debug=True when initializing the calibrator for verbose logging
Check the raw test results in calibration_results attribute
Examine the log file for detailed test information
Best Practices
Test Selection
Use tests with clearly different packet sizes for low and high components
Ensure both components can generate stable traffic
Throughput Settings
Set total throughput within the capabilities of your test environment
Allow sufficient headroom for traffic generation
Validation
Always run validation after calibration
Check the APS deviation percentage (should be under 5%)
Verify RX/TX values match expected throughput
Example Report
License
This tool is provided under the MIT License. See LICENSE file for details.

=== CALIBRATION RESULTS ===
📏 **Average Packet Size**: 512.00 B
📨 **Throughput**: 30,000.00 Mbps
💾 **Data Points Collected**:
  💾 Frame Data Rate Samples: 92
  📏 Frame Size Samples: 92
  💾 Frame Data Rate Range: 29,400.00 Mbps - 30,600.00 Mbps
  📏 Frame Size Range: 506.88 B - 517.12 B
🔧 **Validation Calibration Stored** (ID: TEST-210)

=== VALIDATION RESULTS ===
╒══════════════════╤════════════╕
│ 🔖 Target APS    │ 512.00 B   │
├──────────────────┼────────────┤
│ 📏 Measured APS  │ 512.00 B   │
├──────────────────┼────────────┤
│ ⚖️ Tolerance (±5%) │ 25.60 B    │
├──────────────────┼────────────┤
│ 🧪 Samples Collected │ 92         │
├──────────────────┼────────────┤
│ ⏱️ Test Duration  │ 120.00 s   │
╘══════════════════╧════════════╛

=== GAP THEOREM CALCULATION ===
╒═══════════════════════╤═══════════════════════════════════════════════╤═══════════════════════════════════════════════╕
│ Gap Theorem Formulas  │ Tput_high = (APS_high*(APS_desired - APS_low))│ Tput_low = (APS_low*(APS_high - APS_desired)) │
│                       │ / (APS_desired*(APS_high - APS_low)) * Tput_total│ / (APS_desired*(APS_high - APS_low)) * Tput_total│
├───────────────────────┼───────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ Values Used           │ APS_low: 64.00 B                              │ APS_target: 512.00 B                          │
│                       │ APS_high: 1,500.00 B                          │ Tput_total: 30,000.00 Mbps                    │
╘═══════════════════════╧═══════════════════════════════════════════════╧═══════════════════════════════════════════════╛

=== TEST RESULTS ===
╒═══════════════════╤═══════════════════╤════════════════════╤═══════════════════╕
│ Test ID           │ LOW-123           │ HIGH-456           │ TEST-210          │
├───────────────────┼───────────────────┼────────────────────┼───────────────────┤
│ Throughput (Mbps) │ 1,117.00 (calculated) │ 11,709.00 (calculated) │ RX: 29,445.15    │
│                   │ 12,826.26 (measured) │ 29,445.15 (measured) │ TX: 29,445.15    │
├───────────────────┼───────────────────┼────────────────────┼───────────────────┤
│ Avg Packet Size   │ 64.00 B           │ 1,500.00 B         │ 512.00 B          │
│                   │                   │                    │ (Target: 512.00 B) │
├───────────────────┼───────────────────┼────────────────────┼───────────────────┤
│ Status            │ ✅ Complete       │ ✅ Complete        │ ✅ Passed         │
╘═══════════════════╧═══════════════════╧════════════════════╧═══════════════════╛

=== VALIDATION SUMMARY ===
APS Deviation: 0.00B (0.0%)
