from sqlalchemy import create_engine
from pandas import read_sql as psql
from time import sleep

def _getConnection(dbname='tm351',
                     host='localhost', port=5432,
                     user='tm351admin', password='tm351admin'):
    engine = create_engine("postgresql://{user}:{password}@{host}:{port}/{dbname}".format(dbname=dbname, host=host, port=port, user=user, password=password))
    conn = engine.connect()
    conn.execution_options(isolation_level="AUTOCOMMIT")
    return conn
    
    
    
def showDatabases(dbname='tm351',
                host='localhost', port=5432,
                user='tm351', password='tm351', allusers=False):
    ''' Return list of databases. '''
    conn = _getConnection(dbname, host, port, user, password)
    allusers = '' if allusers else "WHERE pg_catalog.pg_get_userbyid(datdba) !='postgres'"
    q="SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database {};".format(allusers)
    dbs = psql(q,conn)
    conn.close()
    return dbs
    
def checkDatabase(dbname='tm351',
                host='localhost', port=5432,
                user='tm351', password='tm351'):
    ''' Check whether specified database exists. '''
    
    conn = _getConnection(dbname, host, port, user, password)
    q="SELECT datname FROM pg_database WHERE datname='{db}';".format(db=dbname)
    dbs = psql(q,conn)
    conn.close()
    return dbs
    

    
    
def forceDropdb(dbname='tm351',
                host='localhost', port=5432,
                user='tm351', password='tm351'):
    ''' Clear all connections associated with a particular database and then delete that database. '''
    
    if dbname=='tm351':
        print("Not doing that...")
        return
    #Clear any connections to the database
    clearConnections(dbname=dbname,host=host,port=port,user=user,password=password)
    #Delete the database
    q="DROP DATABASE IF EXISTS {db};".format(db=dbname)
    conn = _getConnection('', host, port, user, password)
    conn.execute(q)
    conn.close()


def forceCleandb(dbname,user='tm351'):
    ''' Clear all connections associated with a database, drop it, 
        then create a new, empty database with the same name. '''
    forceDropdb(dbname)
    
    
    conn = _getConnection()
    
    q="CREATE DATABASE {db}".format(db=dbname, user=user)
    conn.execute(q)
    
    if user is not None:
        q = "GRANT ALL PRIVILEGES ON DATABASE {db} TO {user}".format(db=dbname,user=user)
        conn.execute(q)
        
    conn.close()
    
def showConnections(dbname,
                     host='localhost', port=5432,
                     user='tm351', password='tm351',
                     dbconn='tm351'):
    #Look for a database of the required name
    dbs=checkDatabase(dbname,host,port,user,password)
    #Return silently if it doesn't exist
    if len(dbs)==0: return
    
    conn = _getConnection(dbconn, host, port, user, password)
    #Check for connections to that database
    q="SELECT datname, usename, pid, query FROM pg_stat_activity WHERE pid <> pg_backend_pid() AND datname='{db}';".format(db=dbname)
    openconns=psql(q,conn)
    conn.close()
    return openconns

def clearConnections(dbname,
                     host='localhost', port=5432,
                     user='tm351', password='tm351',
                     dbconn='tm351'):
    ''' Clear all connections associated with a particular database. '''
                     
    #Delete any outstanding connections to that database
    
    openconns = showConnections(dbname,host, port,user, password,dbconn)
                     
    if len(openconns):
        print("Closing connections on {}....".format(dbname))
        conn = _getConnection(dbconn, host, port, user, password)
        for openconn in openconns['pid'].tolist():
            conn.execute("SELECT pg_terminate_backend({oc});".format(oc=openconn))
        #Superstitiously, give everything time to clear down
        #It also makes users think something is happening
        sleep(1.5)
        print('...connections closed.\n\nYou will need to reconnect %sql magics in other notebooks.\n\n')
        conn.close()
    else: print("No connections found on {}.\n".format(dbname))


def showTables(dbname='tm351',
                host='localhost', port=5432,
                user='tm351', password='tm351'):
    ''' Return public tables in specified database. '''
    
    conn = _getConnection(dbname, host, port, user, password)
    q="SELECT tablename, tableowner FROM pg_catalog.pg_tables WHERE schemaname='public';"
    tables = psql(q,conn)
    conn.close()
    return tables
    
def showColumns(dbname='tm351',table=None,
                host='localhost', port=5432,
                user='tm351', password='tm351'):
    ''' Return columns in specified table(s). '''

    table = table if table else showTables(dbname, host, port, user, password)['tablename'].tolist()
    
    if not table: return
    table= table if isinstance(table, list) else [table]
    table= ','.join(["'{}'".format(t) for t in table])
    
    conn = _getConnection(dbname, host, port, user, password)
    q="SELECT column_name, table_name FROM INFORMATION_SCHEMA.COLUMNS 'WHERE table_name IN ({t})' ORDER BY table_name, column_name;".format(t=table)
    cols = psql(q,conn)
    conn.close()
    return cols
    
def showUsers(dbname='tm351',table=None,
                host='localhost', port=5432,
                user='tm351', password='tm351'):
    ''' Return a table of PostgreSQL database users and roles. '''
    
    q='''SELECT u.usename AS "Role name",
  CASE WHEN u.usesuper AND u.usecreatedb THEN CAST('superuser, create
database' AS pg_catalog.text)
       WHEN u.usesuper THEN CAST('superuser' AS pg_catalog.text)
       WHEN u.usecreatedb THEN CAST('create database' AS
pg_catalog.text)
       ELSE CAST('' AS pg_catalog.text)
  END AS "Attributes"
FROM pg_catalog.pg_user u
ORDER BY 1;'''
    conn = _getConnection(dbname, host, port, user, password)
    users = psql(q,conn)
    conn.close()
    return users

    
def showConstraints(dbname='tm351',table=None,
                host='localhost', port=5432,
                user='tm351', password='tm351', typ=None, cols=[], asdict=False):
    ''' Show constraints asscoiated with a database. '''
    
    table= '' if not table else table if isinstance(table, list) else [table]
    table= '' if not table else ','.join(["'{}'".format(t) for t in table])
    
    where = 'WHERE'
    where = '' if not typ or not any(x for x in ['fk','foreign'] if x in typ.lower()) else "{} constraint_type = 'FOREIGN KEY'".format(where)
    where = '{w} tc.table_name IN ({t})'.format(w='{} AND'.format(where) if where!='WHERE' else where,
                                  t=table) if table else where
    
    q='''
    -- via https://stackoverflow.com/questions/1152260/postgres-sql-to-list-table-foreign-keys#comment8649732_1152321
-- https://dba.stackexchange.com/a/37068/152044
SELECT tc.constraint_name, tc.table_name, kcu.column_name,
    constraint_type, pg_get_constraintdef(c.oid) AS constraintDef,
    CASE constraint_type WHEN 'FOREIGN KEY' THEN ccu.table_name ELSE '' END AS foreign_table_name,
    CASE constraint_type WHEN 'FOREIGN KEY' THEN ccu.column_name ELSE '' END AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu USING (constraint_schema, constraint_name) 
    JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
    JOIN pg_constraint AS c ON c.conname = tc.constraint_name AND tc.constraint_schema=tc.table_schema
    JOIN pg_namespace n ON n.oid = c.connamespace AND n.nspname = tc.table_schema
{where} ;
    '''.format(where=where)
    conn = _getConnection(dbname, host, port, user, password)
    constraints = psql(q,conn)
    conn.close()
    
    if cols:
        cols = cols if isinstance(cols, list) else [cols]
        constraints=constraints[cols]
    constraints = constraints.to_dict(orient='record') if asdict else constraints
    return constraints
