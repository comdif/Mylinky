#!/usr/bin/python3
# stdlib
import datetime, time, logging
# Self libraries
import linky

# ----------------------------- #
# Setup                         #
# ----------------------------- #
log = logging.getLogger('linky')
log.debug('Loading config...')
config = linky.load_config()
log.debug(f'Config loaded! Values: {config}')
terminal = linky.setup_serial(config['device'])

# Try to connect the db server and creating schema if not exists Check scenarion for test_db_connection in linky.py
linky.test_db_connection(config['database']['server'], config['database']['user'], config['database']['password'], config['database']['name'])

# ----------------------------- #
# Main loop                     #
# ----------------------------- #
while True:
    log.debug("Cycle begins")
    data_HCHP = None
    data_HCHC = None
    data_PAPP = None
    data_PTEC = None
    # Beginning to read data from Linky
    log.debug("Opening terminal...")
    terminal.open()
    # reading continously output until we have data that interests us
    while True:
        line = terminal.readline().decode('utf8')
        log.debug(f"Current line: {line}")
        ########################################
        if line.startswith('HCHP'):
            myhchp = line[5:14]
            if myhchp.isnumeric():
                data_HCHP = int(line[5:14])
            else:
                data_HCHP = ""
        ########################################
        if line.startswith('HCHC'):
            myhchc = line[5:14]
            if myhchc.isnumeric():
                data_HCHC = int(line[5:14])
            else:
                data_HCHC = ""
         ########################################
        if line.startswith('PAPP'):
            myapp = line[5:10]
            if myapp.isnumeric():
                data_PAPP = int(line[5:10])
            else:
                data_PAPP = ""
        ########################################
        if line.startswith('PTEC'):
           data_PTEC = str(line[5:7])

        # We have HCHP, HCHC, PTEC and PAPP, we can now close the connection
        if data_HCHP and data_HCHC and data_PAPP and data_PTEC:
            log.debug(f"Output parsed: HCHP={data_HCHP}, HCHC={data_HCHC}, PAPP={data_PAPP}, PTEC={data_PTEC}. Closing terminal.")
            terminal.close()
            break
    
    # Connecting to database
    log.debug("Connecting to database")
    db, cr = linky.open_db(config['database']['server'], config['database']['user'], config['database']['password'], config['database']['name'])
    ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    # inserting values
    log.debug("Inserting stream record")
    linky.insert_stream(config, db, cr, data_HCHP, data_HCHC, data_PAPP, data_PTEC, ts)
    log.debug("Cycle ends, sleeping for 60 seconds")
    time.sleep(60)
