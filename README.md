
That script will allow bulk certificates modifications on Cisco 8821 IP Phones. As you know user certificates (those used by Wifi EAP-TLS) cant be centrally managed. It means when your certificates expire you need to go on each 8821 WebUI to remove and add new certs.

Features:

- Display installed certificates (user provided, not the MIC)
- Remove Server CA
- Remove User certificate
- Add User Certificate (8821 IP Phone supports only one user certificate)

Requirements:

- Python with required lib's
- Webui must be enabled (from CUCM)
- Phones need to be configured with same Webui credentials (from CUCM)
- Phones certificates must be generated with PFX format, all of them must be password protected with the same key
- Phones certificates files name should be PHONE_NAME.pfx (example : SEPXXXXX.pfx)
- an input CSV file must be provided with a predefined format

