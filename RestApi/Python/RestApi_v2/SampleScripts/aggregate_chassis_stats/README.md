# Aggregate Chassis Stats

Run the script and get the synced output from the report

- The result is in CSV file. Each result will be store individually
- Provide the system info: IP / Domain name , credentials
- Provide the path of interest from report in a list, separated by "\\".
  - E.g, "Detailed Summarized Statistics \ IP \ TCP Sessions"
- Provide the report internal id. Open the report page, it will be the value of the last parameter from the URL.
  - Section ID will be generated automatically
- Dependency lib path in the script is a , the path to the wrapper library is: RestApi/Python/RestApi_v2/Modules/bps_restpy

  - [restPyWrapper](https://github.com/OpenIxia/BreakingPoint/blob/master/RestApi/Python/RestApi_v2/Modules/bps_restpy/restPyWrapper.py)
  - [restPyWrapper3](https://github.com/OpenIxia/BreakingPoint/blob/master/RestApi/Python/RestApi_v2/Modules/bps_restpy/restPyWrapper3.py)

- The naming convention of the file is based on the section id of the report.
