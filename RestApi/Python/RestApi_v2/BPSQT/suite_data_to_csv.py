# Title:  suite_data_to_csv
# Note:This Python script using the bps_restpy and pytz package (pip install bps_restpy pytz) 
# Actions: Exports the suite data to a csv
#   1. Login to BPSQT box
#   2. Based on the QT_SUITE_RUNID get each test result
#   3. Extract aditional data from the bps legacy  report for the specific test (REPORT_SECTIONS)
#   4. write all to csv: OUT_RESULTS_CSV
# ================

import re
from pytz import timezone
from datetime import datetime, timedelta
from bps_restpy.bps import BPS


########################################
# Demo script global variables
# bps system info
bps_system  = '10.36.83.240' # bpsqt system ip 
bpsuser     = 'admin' # system username
bpspass     = 'admin' # system password

# go to BPSQT suite result that you are interested in
# set QT_SUITE_RUNID to the number found at the end of the link
QT_SUITE_RUNID = '692' # https://<chassisip>/bpse/ui/suites/netsecOpen/runSummary/692
#sections that should be extracted from BPS legacy report
REPORT_SECTIONS = [ 'Application Response Time',
                    'Application First Byte Time',
                    'Connection First Byte Time'
                    ]
#results file output
OUT_RESULTS_CSV = 'QT_NSO_RESULT_ID' + QT_SUITE_RUNID + '.csv'
########################################
# Login to BPS box
bps = BPS(bps_system, bpsuser, bpspass)
bps.login()


def testStart2Date(datestr):
    # 'Tue Sep 24 05:27:13  2019'
    tmp = datestr.split()
    tmp[-2] = ''
    tmp = ' '.join(tmp)
    date = datetime.strptime(tmp, '%a %b %d %H:%M:%S %Y')
    date = timezone('US/Pacific').localize(date)
    date = date.astimezone(timezone('UTC'))
    return date


def suiteStart2Date(datestr):
    # "2020-03-12T22:36:26.651-07:00"
    tmp = datestr.split('.')
    needsAdjustment = re.search(r'\d\d\d[+-](\d\d\:\d\d)',tmp[-1])
    if needsAdjustment:
        adjustemntTZ = datetime.strptime(needsAdjustment.group(1), '%H:%M')
    # exclude ms and timezone adjutment and set date
    tmp = ' '.join(tmp[:-1])
    date = datetime.strptime(tmp, '%Y-%m-%dT%H:%M:%S')
    date = date + timedelta(hours=adjustemntTZ.hour, minutes=adjustemntTZ.minute, seconds=0)
    date = timezone('UTC').localize(date)
    return date


def get_reports_data(bps, run_id):
    # getReportContents 1st 'IP Summary' section
    #'exceptions'
    contents = bps.reports.getReportContents(runid=run_id)
    report_results = {}
    for section_to_get in REPORT_SECTIONS:            
        for section in contents:
            if section['Section Name'] == section_to_get:
                print("Report result: %s for runid: %s" % (section, run_id))
                report_results[section_to_get] = bps.reports.getReportTable(
                                                    runid=run_id,
                                                    sectionId=section['Section ID'])
                break
    report_results_aggregated = {}
    for section in REPORT_SECTIONS:
        report_results_aggregated[section] = get_aggregated_value(report_results[section])

    return report_results_aggregated

#compute min/max and avg for given report table() and last sustain in minutes
def get_aggregated_value(report_stat_data, sustain_duration=9, rampdown_duration=5):
    # ex : report_results['Application Response Time'] is:
    #  [{u'Timestamp': [...]}, {u'Average Response Time': [...]}, {u'Instantaneous Response Time': [...]}]
    #get sustain index
    time_samples = report_stat_data[0]['Timestamp']
    sustain_start_time = float(time_samples[-1]) - (60 * sustain_duration) - (60 * rampdown_duration)
    sustain_last_time = float(time_samples[-1]) - (60 * rampdown_duration)
    for sustain__start_index, val in enumerate(time_samples):
        if float(val) > sustain_start_time:
            break
    for sustain_end_index, val in enumerate(time_samples):
        if float(val) > sustain_last_time:
            break
    table_collumn_name = list(report_stat_data[2].keys())[0]
    measurements = report_stat_data[2][table_collumn_name][sustain__start_index:sustain_end_index]
    measurements = [float(y.strip('~')) for y in measurements]
    try:
        return_val = [min(measurements), average(measurements), max(measurements)]
    except ValueError as e:
        print('Problems when calculating average : %s' % str(e))
        return_val = ['Err', 'Err', 'Err']
    return return_val


def average(lst): 
    return sum(y for y in lst)/len(lst)


def get_app_times(testname, suiteStartTime, suiteDuration):
    suite_start_date = suiteStart2Date(suiteStartTime)
    suite_duration_date = datetime.strptime(suiteDuration, '%H:%M:%S')
    suite_end_date = suite_start_date + \
        timedelta(hours=suite_duration_date.hour, minutes=suite_duration_date.minute)
    # query the last 200 bps results matching the test name
    results = bps.reports.search(
        searchString=testname, limit=200, sort='startTime', sortorder='descending')
    for result in results:
        if not result['startTime']:
            continue
        test_start_date = testStart2Date(result['startTime'])
        print ("Test Date : %s Suite : %s <-> %s" % (test_start_date.strftime('%Y-%m-%dT%H:%M:%S'),
                                                     suite_start_date.strftime('%Y-%m-%dT%H:%M:%S'),
                                                     suite_end_date.strftime('%Y-%m-%dT%H:%M:%S')
                                                    ) 
              )
        if test_start_date >= suite_start_date and test_start_date <= suite_end_date:
            avg_timings = get_reports_data(bps, result['runid'])
            break
    return avg_timings
#################################



#Using a GET request to obtain the status of the suite

params = {'responseDepth': '4'}
url = 'https://' + bps_system +'/bpse/api/v2/results/' + QT_SUITE_RUNID
r = bps.session.get(url, params=params)
if not r.status_code == 200:
    raise Exception('Failed to get  results for suite id: %s returned %s' % (QT_SUITE_RUNID, r.contents))
suite = r.json()
csv_handle = open(OUT_RESULTS_CSV, 'w+')
head_line_csv = ",".join([suite['suite'],
                          'startDate:' + suite['startDate'] +' duration:' + suite['duration'],
                           suite['state'],
                           suite['id'] 
                        ])
head_line_csv = head_line_csv + ',' + ' min,avg,max,'.join(REPORT_SECTIONS)
print(head_line_csv)
csv_handle.write(head_line_csv + '\n')
suiteStartTime = suite['startDate']
suiteDuration = suite['duration']
for category in suite['categories']:
    print(category['category'])
    csv_handle.write(category['category'] + '\n')
    for test in category['tests']:
        if test['state'] == 'Skipped':
            continue
        match = re.search(r'achieved\s(\d*)', test['goals'][0]['result'])
        val = 'x'
        if match:
            val = match.group(1)   
        durations = get_app_times(test['name'], suiteStartTime, suiteDuration)
        test_csv_line = ", ".join([test['test'], test['grading']['description'], val, test['goals'][0]['units']])
        for section in REPORT_SECTIONS:
            if section in REPORT_SECTIONS:
                try:
                    durations_to_strings = ['%.2f' % d for d in durations[section]]
                except TypeError:
                    durations_to_strings = durations[section]
                test_csv_line = test_csv_line + ',' + ','.join(durations_to_strings)
            else:
                test_csv_line = test_csv_line + ',' + ','.join(['0', '0', '0'])
        print(test_csv_line)
        csv_handle.write(test_csv_line + '\n')
csv_handle.close()

# logout bps session
print("Session logout")
bps.logout()
