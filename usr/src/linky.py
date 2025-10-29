#!/usr/bin/python3

# stdlib
import serial, MySQLdb, datetime, sys, logging, logging.handlers, time, yaml

def init_log_system():
    """ Initializes log system """
    log = logging.getLogger('linky')
    log.setLevel(logging.DEBUG) # Define minimum severity here
    handler = logging.handlers.RotatingFileHandler('./logs/linky.log', maxBytes=1000000, backupCount=5) # Log file of 1 MB, 5 previous files kept
    formatter = logging.Formatter('[%(asctime)s][%(module)s][%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S %z') # Custom line format and time format to include the module and delimit all of this well
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log

def load_config():
    """ Loads config file """
    try:
        with open('config.yml', 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        log.critical('Something went wrong while opening config file:', exc_info=True)
        print('Something went wrong while opening config file. See logs for more info.', file=sys.stderr)
        raise SystemExit(3)
    else:
        return config

def setup_serial(dev):
    """ Builds the serial connection object """
    terminal = serial.Serial()
    terminal.port = dev
    terminal.baudrate = 1200
    terminal.stopbits = serial.STOPBITS_ONE
    terminal.bytesize = serial.SEVENBITS
    return terminal

def test_db_connection(server, user, password, name):
    """ Tests DB connection, and creates the schema if missing """
    # testing connection
    db, cr = open_db(server, user, password, name)

    # create schema if first connection
    stream_exists = cr.execute(f"SELECT * FROM information_schema.tables WHERE table_schema = '{name}' AND table_name = 'stream' LIMIT 1;")
    if stream_exists == 0:
        log.info("Database schema is not there, creating it...")
        try:
            cr.execute("CREATE TABLE `stream` (`id` int(20) UNSIGNED NOT NULL,`clock` datetime NOT NULL,`HCHP` int(11),`HCHC` int(11),`PAPP` int(11),`PTEC` varchar(11),`HCHP_diff` int(11),`HCHC_diff` int(11)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
            cr.execute("ALTER TABLE `stream` ADD PRIMARY KEY (`id`), ADD KEY `clock` (`clock`);")
            cr.execute("ALTER TABLE `stream` MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;")
            db.commit()
        except MySQLdb._exceptions.OperationalError:
            log.critical('Something went wrong while trying to create database schema:', exc_info=True)
            print('Something went wrong while trying to create database schema. See logs for more info.', file=sys.stderr)
            raise SystemExit(4)
        else:
            log.info("Database schema created successfully")

def open_db(server, user, password, name):
    """ Connects to database """
    try:
        db = MySQLdb.connect(server, user, password, name)
        cr = db.cursor()
        return db, cr
    except MySQLdb._exceptions.OperationalError:
        log.critical('Something went wrong while connecting to database server:', exc_info=True)
        print('Something went wrong while connecting to database server. See logs for more info.', file=sys.stderr)
        raise SystemExit(4)

def close_db(db):
    """ Closes connection to database """
    db.close()

def insert_stream(config, db, cr, HCHP, HCHC, PAPP, PTEC, ts):
    """ Insert a record in the stream table. Args: HCHP: HP counter, HCHC: HC counter, PAPP: Curent power, PTEC: current Tarif """
    ############### generating time
    ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ############### retrieving previous HCHP and calculating BASE_diff
    cr.execute("SELECT HCHP FROM stream ORDER BY clock DESC LIMIT 1;")
    try:
        previous = cr.fetchone()[0]
    except TypeError:
        ############# no records yet
        HCHP_diff = 0
    else:
        HCHP_diff = HCHP-int(previous)

    ############### retrieving previous HCHC and calculating BASE_diff
    cr.execute("SELECT HCHC FROM stream ORDER BY clock DESC LIMIT 1;")
    try:
        previous = cr.fetchone()[0]
    except TypeError:
        ############# no records yet
        HCHC_diff = 0
    else:
        HCHC_diff = HCHC-int(previous)
    ############### inserting records
    cr.execute(f'INSERT INTO stream VALUES (NULL, %(now)s, %(HCHP)s, %(HCHC)s, %(PAPP)s, %(PTEC)s, %(HCHP_diff)s, %(HCHC_diff)s, %(ts)s);', {"now": now, "HCHP": HCHP, "HCHC": HCHC, "PAPP": PAPP, "PTEC": PTEC, "HCHP_diff": HCHP_diff, "HCHC_diff": HCHC_diff, "ts": ts})
    db.commit()

############### Initializing log system
log = init_log_system()
