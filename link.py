import cx_Oracle
import oracledb

# 使用 oracledb 就不用Oracle Instant Client了
# cx_Oracle.init_oracle_client(lib_dir="C:\Oracle\Client\instantclient-basic-windows.x64-19.18.0.0.0dbru\instantclient_19_18") # init Oracle instant client 位置
# connection = cx_Oracle.connect('GROUP8', 'OfVkxNNOD5', cx_Oracle.makedsn('140.117.69.60', 1521, service_name='ORCLPDB1'))

# 參數
user = 'GROUP8'
password = 'OfVkxNNOD5'
dsn = cx_Oracle.makedsn('140.117.69.60', 1521, service_name='ORCLPDB1')

# pool
pool = oracledb.SessionPool(user=user, password=password, dsn=dsn, min=2, max=1000, increment=2, encoding='UTF-8', nencoding='UTF-8', threaded=True, timeout=60)

# 連線 Oracle
# connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
# connection = oracledb.connect(user=user, password=password, dsn=dsn)
connection = pool.acquire()

cursor = connection.cursor()
