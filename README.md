# assign_pdl_licenses
Simple script to assign large quantities of equal Meraki licenses to large quantities of equal Meraki devices. Script allows selection of device type you wish to assign licenses from your available pool. As of today, the script does not differentiate between different duration licenses, nor different license tiers within a type of license (i.e. MX65-ENT is treated the same as MX65-SEC). Needless to say, this only works and is useful for PDL orgs.

Modify the credentials.py file to include your API Key and your target organization's org_id.
