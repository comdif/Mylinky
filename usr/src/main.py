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

last_data_PTEC = None  # To keep the last valid PTEC value
# ----------------------------- #
# Main loop                     #
# ----------------------------- #
while True:
    log.debug("Cycle begins")
    data_HCHP = None
    data_HCHC = None
    data_PAPP = None
    data_PTEC = None
    log.debug("Opening terminal...")
    terminal.open()
    restart_cycle = False
    while True:
        line = terminal.readline().decode('utf8')
        log.debug(f"Current line: {line}")
        ########################################
        if line.startswith('HCHP'):
            myhchp = line[5:14]
            if myhchp.isnumeric():
                data_HCHP = int(line[5:14])
            else:
                log.error("HCHP is not numeric, closing terminal and restarting main loop.")
                terminal.close()
                restart_cycle = True
                break
        ########################################
        if line.startswith('HCHC'):
            myhchc = line[5:14]
            if myhchc.isnumeric():
                data_HCHC = int(line[5:14])
            else:
                log.error("HCHC is not numeric, closing terminal and restarting main loop.")
                terminal.close()
                restart_cycle = True
                break
        ########################################
        if line.startswith('PAPP'):
            myapp = line[5:10]
            if myapp.isnumeric():
                data_PAPP = int(line[5:10])
            else:
                log.error("PAPP is not numeric, closing terminal and restarting main loop.")
                terminal.close()
                restart_cycle = True
                break
        ########################################
        if line.startswith('PTEC'):
            temp_PTEC = str(line[5:7])
            if temp_PTEC in ('HC', 'HP'):
                data_PTEC = temp_PTEC
            else:
                data_PTEC = last_data_PTEC  # Use previous if not HC or HP

        # We have HCHP, HCHC, PTEC and PAPP, we can now close the connection
        if data_HCHP and data_HCHC and data_PAPP and data_PTEC:
            log.debug(f"Output parsed: HCHP={data_HCHP}, HCHC={data_HCHC}, PAPP={data_PAPP}, PTEC={data_PTEC}. Closing terminal.")
            terminal.close()
            break

    if restart_cycle:
        continue
        
    # Temperature feature
    resptemp = urllib2.urlopen('http://192.168.20.116/t')
    tempout = resptemp.read()
    resptempin = urllib2.urlopen('http://192.168.20.136/z*Z9/t')
    tempin = resptempin.read()

    
    # Connecting to database
    log.debug("Connecting to database")
    db, cr = linky.open_db(config['database']['server'], config['database']['user'], config['database']['password'], config['database']['name'])
    ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    # inserting values
    log.debug("Inserting stream record")
    linky.insert_stream(config, db, cr, data_HCHP, data_HCHC, data_PAPP, data_PTEC, ts)
    log.debug("Cycle ends, sleeping for 60 seconds")
    time.sleep(60)
