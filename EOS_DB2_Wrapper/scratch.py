import ibm_db_dbi as ibm_db
import pandas as pd
import xmltodict
import EOS_DB2_Wrapper.machine_fetch as fetch


ibm_sql = 'DATABASE=LOGDB; HOSTNAME={0}; PORT=49999; PROTOCOL=TCPIP; UID=LogDBAdmin; PWD=%admin4L0gDB.#'
ip_address = 'SI1991'
ibm_conn = ibm_db.connect(ibm_sql.format(ip_address), '', '')
status = pd.read_sql_query('SELECT * FROM EOSLOG.STATUS_TBL', ibm_conn)
status = pd.read
print(status)


"""10.101.114.11"""
