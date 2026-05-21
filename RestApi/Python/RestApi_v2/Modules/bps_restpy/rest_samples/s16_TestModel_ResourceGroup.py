"""Create and run a simple BPS Test Model using Resource Groups.

Workflow:
1. Log in to BPS and print current user session info.
2. Create a new test model and add one `appsim` component.
3. Create resource groups and clone components.
4. Assign resource groups to components and save the model.
5. Reserve ports and L47 resources.
6. Run the test and poll real-time summary stats.
7. Unreserve ports and log out.
"""

import os
import sys
import time

from bps_restpy.bps import BPS, pp


########################################
# Demo script global variables
APPSIM_COMPONENT_NAME = "tempAppsim"
TEST_NAME = "Test_Model_with_ResourceGroup"

#bps system info
BPS_SYSTEM = '<system ip>'
BPS_USER = '<username>'
BPS_PASS = '<password>'

########################################
#session inactivity -  session will close after this time of inactivity, in seconds.
INACTIVITY_TIMEOUT = 180

SLOT_NUMBER = 1
PORT_LIST = ["1.0", "2.0"]
TEST_GROUP = 1
L47_RESOURCE = [0, 1]
INIT_TIMEOUT_SECONDS = 300
RETRYABLE_STATUS_CODES = {500, 503}
STATS_RETRY_LIMIT = 3

########################################


########################################

def create_and_configure_test_model(bps_client):
    print("Create a new test:")
    bps_client.testmodel.new()

    print("Add components to the test.")
    bps_client.testmodel.add(name=APPSIM_COMPONENT_NAME, type="appsim", active=True, component="appsim")

    component_name = bps_client.testmodel.component["appsim_1"].label.get()
    print("Component Name is: %s" % component_name)

    bps_client.testmodel.save(name=TEST_NAME, force=True)
    test = bps_client.testmodel.search(searchString=TEST_NAME, limit=2, sort="name", sortorder="ascending")
    print("Search result after save:")
    print(test)

    bps_client.testmodel.resourceGroup.add(name="Test_Group1", count=1, affinity=".*")
    bps_client.testmodel.resourceGroup.add(name="Test_Group2", count=1, affinity=".*")
    resource_group_map = {
        group["name"]: str(group["id"]) for group in bps_client.testmodel.resourceGroup.get()
    }
    test_group1_id = resource_group_map.get("Test_Group1")
    test_group2_id = resource_group_map.get("Test_Group2")
    if not test_group1_id or not test_group2_id:
        raise RuntimeError(
            f"Failed to resolve resource group IDs. Current groups: {bps_client.testmodel.resourceGroup.get()}"
        )

    print("Clone the components:")
    bps_client.testmodel.clone("appsim_1", 'appsim', True)
    bps_client.testmodel.clone("appsim_2", 'appsim', True)
    bps_client.testmodel.clone("appsim_3", 'appsim', True)

    print("Change resource groups for appsim components:")
    bps_client.testmodel.component["appsim_1"].resources.set({"resourceGroup": test_group1_id})
    bps_client.testmodel.component["appsim_2"].resources.resourceGroup.set(test_group2_id)
    bps_client.testmodel.component["appsim_3"].resources.resourceGroup.set(test_group2_id)

    print("Save test:")
    bps_client.testmodel.save()


def reserve_test_resources(bps_client):
    print("Reserve ports")
    for port in PORT_LIST:
        bps_client.topology.reserve([{'slot': SLOT_NUMBER, 'port': port, 'group': TEST_GROUP}])

    print("Reserve L47 resources")
    for resource_id in L47_RESOURCE:
        bps_client.topology.reserveResource(group=TEST_GROUP, resourceId=resource_id, resourceType="l47")


def run_test_and_collect_stats(bps_client):
    print("Run test and get stats:")
    test_id_json = bps_client.testmodel.run(modelname=TEST_NAME, group=TEST_GROUP)
    run_id = test_id_json["runid"]
    print("Test Run Id: %s" % run_id)

    running_test_key = 'TEST-%s' % run_id
    print("Wait for test to begin initialization.")
    running_tests = bps_client.topology.runningTest[running_test_key].get()
    init_wait_start = time.time()

    while running_tests["initProgress"] is None:
        if time.time() - init_wait_start > INIT_TIMEOUT_SECONDS:
            raise TimeoutError("Timed out waiting for initProgress.")
        running_tests = bps_client.topology.runningTest[running_test_key].get()
        print("...")
        time.sleep(1)

    print("Wait for initialization process.")
    init_progress = bps_client.topology.runningTest[running_test_key].initProgress.get()
    while int(init_progress) <= 100 and running_tests["progress"] is None:
        if time.time() - init_wait_start > INIT_TIMEOUT_SECONDS:
            raise TimeoutError("Timed out waiting for test progress.")
        init_progress = bps_client.topology.runningTest[running_test_key].initProgress.get()
        running_tests = bps_client.topology.runningTest[running_test_key].get()
        print("Initialization progress:   %s%%" % init_progress)
        time.sleep(1)

    print("Test is running. Get stats every 2 seconds.")
    progress = bps_client.topology.runningTest[running_test_key].progress.get()
    retry_count = 0
    while isinstance(progress, int) and progress <= 100 and retry_count <= STATS_RETRY_LIMIT:
        try:
            pp(bps_client.testmodel.realTimeStats(int(run_id), "summary", -1))
            progress = bps_client.topology.runningTest[running_test_key].progress.get()
            time.sleep(2)
        except Exception as err:
            if retry_count == STATS_RETRY_LIMIT:
                raise Exception("Exceeded the retry limitation!")
            if isinstance(err, dict) and err.get("status_code") in RETRYABLE_STATUS_CODES:
                print("Retry stats retrieval in 5 seconds...")
                time.sleep(5)
                retry_count += 1
                continue
            raise


def cleanup(bps_client):
    print("Unreserve ports")
    for port in PORT_LIST:
        try:
            bps_client.topology.unreserve([{'slot': SLOT_NUMBER, 'port': port}])
        except Exception as err:
            print(f"Failed to unreserve port {port}: {err}")

    print("Session logout")
    bps_client.logout()


def main():
    bps_client = BPS(BPS_SYSTEM, BPS_USER, BPS_PASS)
    bps_client.login(inactivityTimeout=INACTIVITY_TIMEOUT)

    try:
        create_and_configure_test_model(bps_client)
        reserve_test_resources(bps_client)
        run_test_and_collect_stats(bps_client)
    finally:
        cleanup(bps_client)


if __name__ == "__main__":
    main()


