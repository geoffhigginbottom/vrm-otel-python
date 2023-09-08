import requests
import json
import os

def lambda_handler(event, context):
    # Global Variables
    vrm_username = os.environ.get('VRM_USERNAME')
    vrm_password = os.environ.get('VRM_PASSWORD')
    access_token = os.environ.get('ACCESS_TOKEN')
    realm = os.environ.get('REALM')
    site_id = os.environ.get('SITE_ID')
    site_name = os.environ.get('SITE_NAME')
    fwd_mppt_id = int(os.environ.get('FWD_MPPT_ID'))
    aft_mppt_id = int(os.environ.get('AFT_MPPT_ID'))

    def VRM():
        login_url = 'https://vrmapi.victronenergy.com/v2/auth/login'
        diags_url = "https://vrmapi.victronenergy.com/v2/installations/139346/diagnostics?count=1000"
        login_string = f'{{"username":"{vrm_username}","password":"{vrm_password}"}}'
    
        response = requests.post(login_url , login_string)
        token = json.loads(response.text)["token"]
        headers = {'X-Authorization': "Bearer " + token }
    
        response = requests.get(diags_url, headers=headers)
        data = response.json()["records"]
        return data


    def SYSOVERVIEW(data):
        batterySoC=[element['rawValue'] for element in data if element['code']=="SOC"][0]
        batteryCurrent=[element['rawValue'] for element in data if element['code']=="I"][0]
        solarPower=[element['rawValue'] for element in data if element['code']=="Pdc"][0]
        consumedAmpHours=[element['rawValue'] for element in data if element['code']=="CE"][0]
        
        return batterySoC, batteryCurrent, solarPower, consumedAmpHours

    def FWDMPPT(data):
        fwd_values = []  # List to store the values
        mppt_ids = [fwd_mppt_id]
        codes = ["ScV", "ScI", "SLI", "PVV", "PVP", "MCPT", "MCPY"]
        mppt_names = {
            fwd_mppt_id: {
                "ScV": "fwdSolarChargerBatteryVoltage",
                "ScI": "fwdSolarChargerBatteryCurrent",
                "SLI": "fwdSolarChargerLoadCurrent",
                "PVV": "fwdSolarChargerPvVoltage",
                "PVP": "fwdSolarChargerPvPower",
                "MCPT": "fwdSolarChargerMaxChargePowerToday",
                "MCPY": "fwdSolarChargerMaxChargePowerYesterday"
            }
        }
        for code in codes:
            for mppt_id in mppt_ids:
                matching_code_block = next(
                    (block for block in data if block["code"] == code and block["instance"] == mppt_id),
                    None
                )
                raw_value = matching_code_block["rawValue"]
                fwd_values.append(raw_value)
        return fwd_values
        
    
    
    def AFTMPPT(data):
        aft_values = []  # List to store the values
        mppt_ids = [aft_mppt_id]
        codes = ["ScV", "ScI", "SLI", "PVV", "PVP", "MCPT", "MCPY"]
        mppt_names = {
            aft_mppt_id: {
                "ScV": "aftSolarChargerBateryVoltage",
                "ScI": "aftSolarChargerBateryCurrent",
                "SLI": "aftSolarChargerLoadCurrent",
                "PVV": "aftSolarChargerPvVoltage",
                "PVP": "aftSolarChargerPvPower",
                "MCPT": "aftSolarChargerMaxChargePowerToday",
                "MCPY": "aftSolarChargerMaxChargePowerYesterday"
            }
        }
        for code in codes:
            for mppt_id in mppt_ids:
                matching_code_block = next(
                    (block for block in data if block["code"] == code and block["instance"] == mppt_id),
                    None
                )
                raw_value = matching_code_block["rawValue"]
                aft_values.append(raw_value)
        return aft_values
    
    
    def O11YSYSOVERVIEW(batterySoC, batteryCurrent, solarPower, consumedAmpHours):
        endpoint = 'https://ingest.' + realm + '.signalfx.com/v2/datapoint'
        headers = {
            'Content-Type': 'application/json',
            'X-SF-Token': access_token
        }
        metrics = [
        {'metric': 'BatterySoC', 'value': batterySoC},
        {'metric': 'BatteryCurrent', 'value': batteryCurrent},
        {'metric': 'SolarPower', 'value': solarPower},
        {'metric': 'ConsumedAmpHours', 'value': consumedAmpHours},
        ]
    
        for metric in metrics:
            json_data = {
                'gauge': [
                    {
                        'metric': metric['metric'],
                        'value': metric['value'],
                        'dimensions': {
                            'site_id': site_id,
                            'site_name': site_name,
                        },
                    },
                ],
            }
            response = requests.post(endpoint, headers=headers, json=json_data)
    
    
    def O11YFWDMPPT(fwdSolarChargerBatteryVoltage, fwdSolarChargerBatteryCurrent, fwdSolarChargerLoadCurrent, fwdSolarChargerPvVoltage, fwdSolarChargerPvPower, fwdSolarChargerMaxChargePowerToday, fwdSolarChargerMaxChargePowerYesterday):
        endpoint = 'https://ingest.' + realm + '.signalfx.com/v2/datapoint'
        headers = {
            'Content-Type': 'application/json',
            'X-SF-Token': access_token
        }
        metrics = [
        {'metric': 'fwdSolarChargerBatteryVoltage', 'value': fwdSolarChargerBatteryVoltage},
        {'metric': 'fwdSolarChargerBatteryCurrent', 'value': fwdSolarChargerBatteryCurrent},
        {'metric': 'fwdSolarChargerLoadCurrent', 'value': fwdSolarChargerLoadCurrent},
        {'metric': 'fwdSolarChargerPvVoltage', 'value': fwdSolarChargerPvVoltage},
        {'metric': 'fwdSolarChargerPvPower', 'value': fwdSolarChargerPvPower},
        {'metric': 'fwdSolarChargerMaxChargePowerToday', 'value': fwdSolarChargerMaxChargePowerToday},
        {'metric': 'fwdSolarChargerMaxChargePowerYesterday', 'value': fwdSolarChargerMaxChargePowerYesterday}
        ]
    
        for metric in metrics:
            json_data = {
                'gauge': [
                    {
                        'metric': metric['metric'],
                        'value': metric['value'],
                        'dimensions': {
                            'site_id': site_id,
                            'site_name': site_name,
                        },
                    },
                ],
            }
            response = requests.post(endpoint, headers=headers, json=json_data)
    
    def O11YAFTMPPT(aftSolarChargerBatteryVoltage, aftSolarChargerBatteryCurrent, aftSolarChargerLoadCurrent, aftSolarChargerPvVoltage, aftSolarChargerPvPower, aftSolarChargerMaxChargePowerToday, aftSolarChargerMaxChargePowerYesterday):
        endpoint = 'https://ingest.' + realm + '.signalfx.com/v2/datapoint'
        headers = {
            'Content-Type': 'application/json',
            'X-SF-Token': access_token
        }
        metrics = [
        {'metric': 'aftSolarChargerBatteryVoltage', 'value': aftSolarChargerBatteryVoltage},
        {'metric': 'aftSolarChargerBatteryCurrent', 'value': aftSolarChargerBatteryCurrent},
        {'metric': 'aftSolarChargerLoadCurrent', 'value': aftSolarChargerLoadCurrent},
        {'metric': 'aftSolarChargerPvVoltage', 'value': aftSolarChargerPvVoltage},
        {'metric': 'aftSolarChargerPvPower', 'value': aftSolarChargerPvPower},
        {'metric': 'aftSolarChargerMaxChargePowerToday', 'value': aftSolarChargerMaxChargePowerToday},
        {'metric': 'aftSolarChargerMaxChargePowerYesterday', 'value': aftSolarChargerMaxChargePowerYesterday}
        ]
    
        for metric in metrics:
            json_data = {
                'gauge': [
                    {
                        'metric': metric['metric'],
                        'value': metric['value'],
                        'dimensions': {
                            'site_id': site_id,
                            'site_name': site_name,
                        },
                    },
                ],
            }
            response = requests.post(endpoint, headers=headers, json=json_data)
    
    data = VRM()
    batterySoC, batteryCurrent, solarPower, consumedAmpHours = SYSOVERVIEW(data)
    fwdSolarChargerBatteryVoltage, fwdSolarChargerBatteryCurrent, fwdSolarChargerLoadCurrent, fwdSolarChargerPvVoltage, fwdSolarChargerPvPower, fwdSolarChargerMaxChargePowerToday, fwdSolarChargerMaxChargePowerYesterday = FWDMPPT(data)
    aftSolarChargerBatteryVoltage, aftSolarChargerBatteryCurrent, aftSolarChargerLoadCurrent, aftSolarChargerPvVoltage, aftSolarChargerPvPower, aftSolarChargerMaxChargePowerToday, aftSolarChargerMaxChargePowerYesterday = AFTMPPT(data)
        
    O11YSYSOVERVIEW(batterySoC, batteryCurrent, solarPower, consumedAmpHours)
    O11YFWDMPPT(fwdSolarChargerBatteryVoltage, fwdSolarChargerBatteryCurrent, fwdSolarChargerLoadCurrent, fwdSolarChargerPvVoltage, fwdSolarChargerPvPower, fwdSolarChargerMaxChargePowerToday, fwdSolarChargerMaxChargePowerYesterday)
    O11YAFTMPPT(aftSolarChargerBatteryVoltage, aftSolarChargerBatteryCurrent, aftSolarChargerLoadCurrent, aftSolarChargerPvVoltage, aftSolarChargerPvPower, aftSolarChargerMaxChargePowerToday, aftSolarChargerMaxChargePowerYesterday)
