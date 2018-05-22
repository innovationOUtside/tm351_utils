from sqlalchemy import create_engine
from pandas import read_sql as psql

def clearConnections(dbname='tm351',
                     host='localhost', port=5432,
                     user='tm351', password='tm351'):
    ''' Clear all connections associated with a particular database. '''

    engine = create_engine("postgresql://{user}:{password}@{host}:{port}/{dbname}".format(dbname=dbname,
                                                                                          host=host, port=port,
                                                                                          user=user, password=password))
    conn = engine.connect()
    
    #Look for a database of the required name
    q="SELECT datname FROM pg_database WHERE datname='{db}'".format(db=dbname)
    dbs=psql(q,conn)
    #Return silently if it doesn't exist
    if len(dbs)==0: return
    
    #Check for connections to that database
    q="SELECT pid FROM pg_stat_activity WHERE pid <> pg_backend_pid() AND datname='{db}';".format(db=dbname)
    openconns=psql(q,conn)
    #Delete any outstanding connections to that database
    if len(openconns):
        for openconn in openconns['pid'].tolist():
            conn.execute("SELECT pg_terminate_backend({oc});".format(oc=openconn))
    conn.close()


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
    !dropdb $dbname
    
def forceCleandb(dbname,user='tm351'):
    ''' Clear all connections associated with a database, drop it, 
        then create a new, empty datababase with the same name. '''
    forceDropdb(dbname)
    if user is not None and user!='':
        !createdb $dbname --owner=$user
    else:
        !createdb $dbname