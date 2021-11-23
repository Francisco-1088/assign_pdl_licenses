import meraki
import credentials

dashboard = meraki.DashboardAPI(api_key=credentials.api_key)

org_id = credentials.org_id

# Collect all licenses and devices in organization
licenses = dashboard.organizations.getOrganizationLicenses(organizationId=org_id,total_pages='all')
devices = dashboard.organizations.getOrganizationDevices(organizationId=org_id,total_pages='all')

# Sort them in buckets
available_licenses = {}
licensed_devices = {}
unlicensed_devices = {}
device_types = []
license_types = []
for lic in licenses:
    if lic['licenseType'] not in license_types:
        license_types.append(lic['licenseType'])

for device in devices:
    if 'MR' in device['model']:
        if 'MR' not in device_types:
            device_types.append('MR')
    elif 'MT' in device['model']:
        if 'MT' not in device_types:
            device_types.append('MT')
    elif 'MV' in device['model']:
        if 'MV' not in device_types:
            device_types.append('MV')
    elif device['model'] not in device_types:
        device_types.append(device['model'])

for license_type in license_types:
    available_licenses[f'{license_type}']=[]

for device_type in device_types:
    licensed_devices[f'{device_type}']=[]
    unlicensed_devices[f'{device_type}'] = []

# Find licensed devices
# Find available licenses and sort them
for lic in licenses:
    if lic['deviceSerial']!=None:
        if lic['licenseType']=='ENT':
            licensed_devices['MR'].append(lic)
        elif lic['licenseType']=='MV':
            licensed_devices['MV'].append(lic)
        elif lic['licenseType']=='MT':
            licensed_devices['MT'].append(lic)
        else:
            for product in licensed_devices.keys():
                if product in lic['licenseType']:
                    licensed_devices[product].append(lic)

    elif lic['deviceSerial']==None:
        if lic['licenseType']=='ENT':
            available_licenses['ENT'].append(lic)
        elif lic['licenseType']=='MV':
            available_licenses['MV'].append(lic)
        elif lic['licenseType']=='MT':
            available_licenses['MT'].append(lic)
        else:
            for product in licensed_devices.keys():
                if product in lic['licenseType']:
                    available_licenses[product].append(lic)
for key in licensed_devices.keys():
    print(f"Licensed {key}s: {len(licensed_devices[key])}")

for key in available_licenses.keys():
    print(f"Free {key} Licenses: {len(available_licenses[key])}")

print(f"Total number of devices: {len(devices)}")

# Remove licensed devices from list
for i in reversed(range(len(devices))):
    match = 0
    for key in licensed_devices.keys():
        for licensed_device in licensed_devices[key]:
            if devices[i]['serial'] == licensed_device['deviceSerial']:
                #print(f'This is a licensed {key}, with serial {devices[i]["serial"]}')
                devices.pop(i)
                match = 1
                break
        if match == 1:
            break


print(f"Total number of unlicensed devices: {len(devices)}")

print(unlicensed_devices)

# Sort unlicensed devices
for device in devices:
    for key in unlicensed_devices.keys():
        if device['model'] in key:
            unlicensed_devices[key].append(device)

for key in unlicensed_devices.keys():
    print(f'Unlicensed {key}s: {len(unlicensed_devices[key])}')

for key in available_licenses.keys():
    print(f'Available {key} licenses: {len(available_licenses[key])}')

# Select which device type you want to assign licenses to
for i in range(len(unlicensed_devices.keys())):
    print(f'{i+1} - {list(unlicensed_devices.keys())[i]} (Total {len(unlicensed_devices[list(unlicensed_devices.keys())[i]])})')
option = input("To which of your unlicensed device types do you which to attach licenses?")

if list(unlicensed_devices.keys())[int(option)-1] == 'MR':
    product = 'ENT'
    print(f"You have {len(available_licenses['ENT'])} {list(unlicensed_devices.keys())[int(option)-1]} licenses available.")
else:
    product = list(unlicensed_devices.keys())[int(option)-1]
    print(f"You have {len(available_licenses[list(unlicensed_devices.keys())[int(option)-1]])} {list(unlicensed_devices.keys())[int(option)-1]} licenses available.")

print("A single available license from your pool of available licenses for this device type will be assigned to each unlicensed device, regardless of license duration.")
proceed = input("Do you wish to proceed? (Y/N)")

if proceed == 'Y':
    print(f'Attaching licenses to {list(unlicensed_devices.keys())[int(option) - 1]}')

    # Create as many asynchronous action batches as needed to assign all licenses
    actions = []

    for lic in available_licenses[product]:
        action = {
            "resource": f"/organizations/{org_id}/licenses/{lic['id']}",
            "operation": "update",
            "body": {
                "deviceSerial": f"{unlicensed_devices[product][-1]['serial']}"
            }
        }
        print(lic['id'], unlicensed_devices[product][-1])
        actions.append(action)
        unlicensed_devices[product].pop()

    for i in range(0, len(actions), 100):
        subactions = actions[i:i + 100]
        dashboard.organizations.createOrganizationActionBatch(
            organizationId=org_id,
            actions=subactions,
            confirmed=True,
            synchronous=False
        )
elif proceed == 'N':
    print('Operation aborted.')
