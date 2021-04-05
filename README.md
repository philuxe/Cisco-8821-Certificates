
That script will allow bulk certificates modifications on Cisco 8821 IP Phones. As you know user certificates (those used by Wifi EAP-TLS) cant be centrally managed by default. Unfortunately LSC certificates cant be used for EAP-TLS. It means when your certificates expire you need to go on each 8821 WebUI to remove and add new certs.

Features:

- Display installed certificates (user provided, not the MIC)
- Remove Server CA (the one signing your radius cert)
- Remove User certificate (used for wifi authentication - eap-tls)
- Add User Certificate (8821 IP Phone supports only one user certificate at a time)

Requirements:

- Python with required lib's (see script imports)
- Web Admin must be enabled (from CUCM)
- Phones need to be configured with same Webui credentials (from CUCM)
- Phones certificates must be generated with PFX format, all of them must be password protected with the same key
- Phones certificates files name should be PHONE_NAME.pfx (example : SEPXXXXX.pfx)
- An input CSV file must be provided with a predefined format, that will be the 8821 phone list you have exported from CUCM

Input CSV Format:

PHONE_NAME;LINE_NAME;IP_ADDRESS

SEPF8B7E24ABCDE;Philippe Blavier;10.X.X.X

Warnings:

- Your 8821 phones should have a backup Wifi profile (with WAP-PSK authentication for instance), just in case ...
- that Python script could be improved a lot, some exceptions are not handled (for instance HTTP connect issue are managed by the script and unreachable will be skipped,  but incorrect credentials resulting in login issue are NOT, script will exit)
- actions/modifications are logged in log file (8821.log)

