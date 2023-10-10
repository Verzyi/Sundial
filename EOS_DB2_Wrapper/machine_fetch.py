import sqlite3 as sqlite_db
import ibm_db_dbi as ibm_db
import pandas as pd
import datetime as dt
import xmltodict
import os


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 2000)
pd.set_option('max_colwidth', 100)

directory = os.path.dirname(os.path.realpath(__file__))


class MachineFetchException(Exception):
    """Base Exception"""
    pass


class MachineModelError(MachineFetchException):
    """For if a machine model isn't correct"""
    pass


class DB2ConnectionError(MachineFetchException):
    """For failures to connect to the machine's internal database"""
    pass


class MachineData:
    def __init__(self):
        # Connect to local database containing all machine platform data by machine id
        sqlite_conn = sqlite_db.connect(directory + '\dmls_machine_info.sqlite')
        _sql = 'SELECT * FROM machines LEFT OUTER JOIN platforms ON machines.platform = platforms.platform_id WHERE sell_date IS NULL'
        self.machine_info = pd.read_sql_query(_sql, sqlite_conn, index_col='machine_id')
        self.machine_info.sort_values(by=['site', 'sheets_row'], ascending=[False, True], inplace=True)
        sqlite_conn.close()
        # print(self.machine_info)

        # Clean up data
        self.machine_info = self.machine_info.drop(['platform', 'platform_id'], axis=1)

        # Set attribute for each machine so the machine's info can be called by .siXXXX
        for machine_id in self.machine_info.index:
            setattr(self, 'si%s' % machine_id, Machine(self.machine_info[self.machine_info.index == machine_id]))

    @property
    def machines(self):
        return self.machine_info.index.tolist()

    @property
    def austin_machines(self):
        return self.machine_info[self.machine_info.site == 'Austin'].index.tolist()

    @property
    def belton_machines(self):
        return self.machine_info[self.machine_info.site == 'Belton'].index.tolist()

    @property
    def upkeep_ids(self):
        return self.machine_info[['alias', 'site', 'sheets_row', 'upkeep_id']]


class Machine:
    def __init__(self, pd_data):
        self._fetch_completed = False
        self.pd_data = pd_data
        self.serial_number = self.pd_data.index.values[0]

        # Set all future variables to None
        self._current_height = None
        self.status = None
        self._total_build_time = None
        self._remaining_build_time = None
        self._finish_datetime = None
        self._layer_count = None
        self._file_name = None
        self._parameter_material = None
        self._actual_layer_thickness = None
        self._material = None
        self._build_id = None
        self._start_height = None
        self._final_height = None
        self._status_id = None
        self._status = None
        self._job_id = None

        # Add "; connecttimeout=20" to implement connection timeout
        self.ibm_sql = 'DATABASE=LOGDB; HOSTNAME={0}; PORT=49999; PROTOCOL=TCPIP; UID=LogDBAdmin; PWD=%admin4L0gDB.#'
        for column in self.pd_data:
            setattr(self, column, self.pd_data[column].values[0])
            

    def fetch_status(self):
        self._fetch_completed = True
        try:
            ibm_conn = ibm_db.connect(self.ibm_sql.format(self.ip_address), '', '')
        except ibm_db.OperationalError:
            error_text = "Unable to connection to machine {0}. Is the machine on? Is the IP Address correct?"
            self._status = 'Connection Error'
            raise DB2ConnectionError(error_text.format(self.serial_number))
        status = pd.read_sql_query('SELECT * FROM EOSLOG.STATUS_TBL', ibm_conn)
        status = status[status.MA_ID.str.startswith('SI' + self.serial_number)]
        status = status.drop(['SE_BINDATA', 'MA_ID', 'APP_ID', 'SE_CRY', 'SE_NVAL'], axis=1)
        status = status.set_index('ST_ID')
        status = status.sort_index()
        status_indices = status.index.tolist()

        # This gets the current build height out of the data pulled from the machine
        # For layer thickness, EOS does not give a correct value for M290s & M400s!!!
        if 0 in status_indices:
            self._current_height = float(status.loc[0]['SE_FVAL'])

        # If building, this gets the total and remaining build time
        if 1 in status_indices:
            row_data = xmltodict.parse(status.loc[1]['SE_TEXTDATA'])['TimeInfo']

            # The same method of all models can be used for _total_build_time
            self._total_build_time = [float(x) for x in row_data['Building'].split(':')]
            self._total_build_time = self._total_build_time[0] + (self._total_build_time[1] / 60)

            # The same method of all models can be used for _remaining_build_time
            self._remaining_build_time = [float(x) for x in row_data['Remaining'].split(':')]
            self._remaining_build_time = self._remaining_build_time[0] + (self._remaining_build_time[1] / 60)

            # _finish_datetime will need different methods depending on machine frame
            if self.model in ['M270', 'M280']:
                self._finish_datetime = dt.datetime.strptime(row_data['Ready'], '%A, %B %d, %Y %I:%M:%S %p')
            elif self.model in ['M290', 'M400']:
                self._finish_datetime = dt.datetime.strptime(row_data['Ready'], '%A %d. %B %Y %H:%M:%S')
            else:
                error_text = "{0}'s model ({1}) is outside of scope. Please update local database"
                raise MachineModelError(error_text.format(self.serial_number, self.model))

            if self._finish_datetime <= dt.datetime.now():
                self._finish_datetime = None

            self._layer_count = int(row_data['LayerCount'])

        # For layer thickness, EOS does not give a correct value for M290s & M400s!!!
        if 2 in status_indices:
            row_data = status.loc[2]['SE_TEXTDATA'].replace('&', '&amp;')
            row_data = xmltodict.parse(row_data)['JobInfo']

            self._file_name = row_data['FileName'].split('/')[-1].split('.')[0].split('_')
            self._file_name = self._file_name[1:] if self._file_name[0] == 'DEV' else self._file_name

            if self.model in ['M270', 'M280']:
                self._material = self._file_name[0]
                self._build_id = self._file_name[-1]
                self._parameter_material = row_data['Material']
            elif self.model in ['M290', 'M400']:
                self._material = self._file_name[0]
                self._build_id = self._file_name[2]
                self._parameter_material = row_data['Material']
                

            if self.model in ['M270', 'M280']:
                self._actual_layer_thickness = row_data['LayerThickness']

        if 4 in status_indices:
            row_data = xmltodict.parse(status.loc[4]['SE_TEXTDATA'])['Heights']
            self._start_height = float(row_data['StartProcessHeight'])
            self._final_height = float(row_data['EndProcessHeight'])
            if self.model in ['M290', 'M400']:
                try:
                    self._actual_layer_thickness = (self._final_height - self._start_height) / (self._layer_count - 1)
                except TypeError:
                    self._actual_layer_thickness = None

        if 6 in status_indices:
            row_data = xmltodict.parse(status.loc[6]['SE_TEXTDATA'])['MachineStatus']
            self._status_id = row_data['StatusID']
            self._status = row_data['LastStatus']

        if 8 in status_indices:
            self._job_id = status.loc[8]['SE_TEXTDATA']

        # Conditional events
        self._remaining_build_time = 0.00 if self._status == "Job end" else self._remaining_build_time

    @property
    def current_height(self):
        if self._fetch_completed is False:
            self.fetch_status()
        return self._current_height

    @property
    def total_build_time(self):
        if self._fetch_completed is False:
            self.fetch_status()
        return self._total_build_time

    @property
    def remaining_build_time(self):
        if self._fetch_completed is False:
            self.fetch_status()
        return self._remaining_build_time

    @property
    def finish_datetime(self):
        if self._fetch_completed is False:
            self.fetch_status()
        return self._finish_datetime

    @property
    def layer_count(self):
        if self._fetch_completed is False:
            self.fetch_status()
        return self._layer_count

    @property
    def file_name(self):
        if self._fetch_completed is False:
            self.fetch_status()
        return self._file_name

    @property
    def actual_layer_thickness(self):
        if self._fetch_completed is False:
            self.fetch_status()
        return self._actual_layer_thickness

    @property
    def material(self):
        if self._fetch_completed is False:
            self.fetch_status()
        return self._material

    @property
    def build_id(self):
        if self._fetch_completed is False:
            self.fetch_status()
        return self._build_id

    @property
    def parameter_material(self):
        if self._fetch_completed is False:
            self.fetch_status()
        return self._parameter_material

    @property
    def start_height(self):
        if self._fetch_completed is False:
            self.fetch_status()
        return self._start_height

    @property
    def final_height(self):
        if self._fetch_completed is False:
            self.fetch_status()
        return self._final_height

    @property
    def status_id(self):
        if self._fetch_completed is False:
            self.fetch_status()
        return self._status_id

    @property
    def current_status(self):
        if self._fetch_completed is False:
            self.fetch_status()
        return self._status

    @property
    def job_id(self):
        if self._fetch_completed is False:
            self.fetch_status()
        return self._job_id


if __name__ == '__main__':
    test = MachineData()
    machine = test.si2642
    # print(test.upkeep_ids)





