import sqlite3
# import ibm_db_dbi as db
import pandas as pd
import datetime as dt
import xmltodict
import json


def machine_info(machine_data):
    pd.set_option('display.width', 2000)
    pd.set_option('display.max_rows', 1000)
    (machine_id, ip_address, manufacturer, model, site, cell) = machine_data
    print(machine_id)
    sqlite_sql = 'INSERT INTO status (machine_id, now, current_height, total_time, remaining_time, ' \
                 'completed_datetime, layer_count, file_name, material, layer_thickness, material_thickness, ' \
                 'event_id, module_id, level, state, start_height, end_height, bottom_offset, top_offset, ' \
                 'currents_tatus, status_id, job_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ' \
                 '?, ?, ?, ?)'
    sqlite_conn = sqlite3.connect('machine_data.sqlite')
    sqlite_cur = sqlite_conn.cursor()
    ibm_sql = 'DATABASE=LOGDB; HOSTNAME={0}; PORT=49999; PROTOCOL=TCPIP; UID=LogDBAdmin; PWD=%admin4L0gDB.#;'
    now = int(dt.datetime.now().strftime('%y%m%d%H%M%S'))
    # status = None
    for x in range(3):
        try:
            ibm_conn = db.connect(ibm_sql.format(ip_address), '', '')
            status = pd.read_sql_query('SELECT * FROM EOSLOG.STATUS_TBL', ibm_conn)
            # ibm_cur = ibm_conn.cursor()
            # ibm_cur.execute("SELECT * FROM EOSLOG.STATUS_TBL")
            break
        except db.OperationalError:
            print('OperationalError')

            if x is 2:
                data_values = (machine_id, now) + (None,) * 17 + ('Connection Error', 25) + (None,)
                # sqlite_cur.execute(sqlite_sql, data_values)
                # sqlite_conn.commit()
                sqlite_conn.close()
                return None
    status.drop(['SE_CRY', 'APP_ID', 'SE_BINDATA', 'SE_NVAL', 'SE_TIMESTAMP'], axis=1, inplace=True)
    status = status.sort_values(by='ST_ID').set_index('ST_ID')
    status['MA_ID'] = status['MA_ID'].map(lambda x: x.strip())
    print(status)
    #print(ibm_conn)
    status_indices = status.index.tolist()

    if 0 in status_indices:
        current_height = float(status.loc[0]['SE_FVAL'])
    else:
        current_height = None

    total_time, remaining_time, layer_count = None, None, None

    if 1 in status_indices:
        text = xmltodict.parse(status.loc[1]['SE_TEXTDATA'])['TimeInfo']

        total_time = [float(x) for x in text['Building'].split(':')]
        total_time = total_time[0] + total_time[1]/60 + total_time[2]/3600

        remaining_time = [float(x) for x in text['Remaining'].split(':')]
        remaining_time = remaining_time[0] + remaining_time[1] / 60 + remaining_time[2] / 3600

        layer_count = int(text['LayerCount'])

    build_id, material = None, None

    if 2 in status_indices:
        text = xmltodict.parse(status.loc[2]['SE_TEXTDATA'])['JobInfo']
        # print(json.dumps(text, indent=2))

        #  Return the actual layer thickness. This value is correct for 270, 280 and INCORRECT for 290, 400
        layer_thickness = float(text['LayerThickness'])

        #  File name - parse for material and job #
        file_name = str(text['FileName']).split('/')
        if model in ['M270', 'M280']:
            build_id = file_name[2] if file_name[2].isnumeric() else None
            build_name = file_name[-1]
            material = build_name.split('_')[0]

        elif model in ['M290', 'M400']:
            build_name = file_name[-1].split('_')
            build_name = build_name[1:] if build_name[0] == 'DEV' else build_name
            build_id = build_name[2] if build_name[2].isnumeric() else None
            material = build_name[0]

    event_id, module_id, level, state = None, None, None, None

    if 3 in status_indices:  # and status.loc[3]['MA_ID'] == machine_id.upper():
        test = status.loc[3]
        # test = test[test['MA_ID'] == 'SI{0}'.format(machine_id)]
        print(test)
        test = xmltodict.parse(str(test['SE_TEXTDATA']))
        print(test['SE_TEXTDATA'])
        text = xmltodict.parse(status.loc[3]['SE_TEXTDATA'])['Events']['LastEvent']
        event_id = text['EventId']
        module_id = text['ModuleId']
        level = text['Level']
        state = 'State'

    start_height, end_height, bottom_offset, top_offset = None, None, None, None

    if 4 in status_indices:
        text = xmltodict.parse(status.loc[4]['SE_TEXTDATA'])['Heights']
        start_height = text['StartProcessHeight']
        end_height = text['EndProcessHeight']
        bottom_offset = text['BottomOffset']
        top_offset = text['TopOffset']

    if 6 in status_indices:
        text = xmltodict.parse(status.loc[6]['SE_TEXTDATA'])['MachineStatus']
        # print(json.dumps(text, indent=2))
        status_id = text['StatusID']
        current_status = text['LastStatus']

conn = sqlite3.connect('machine_data.sqlite')
cur = conn.cursor()
data = cur.execute('SELECT * FROM machines WHERE machine_id=2006')
for i in data:
    machine_info(i)
