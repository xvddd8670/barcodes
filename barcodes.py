import pymysql
import sqlite3
import pymssql
import datetime
import configparser
import os
import logging
import pygame
import pygame_gui
import json
import random
import secrets
import string
####################
import gui

#+++++++++++++++++++++++#
def random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(secrets.choice(
        letters_and_digits) for i in range(length))
#+++++++++++++++++++++++#

#logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='log')
logging.info('=============')
logging.info('start program')

#open json config file
try:
    with open('config.json', 'r') as cnf:
        config_json = cnf.read()
    config = json.loads(config_json)
except:
    raise Exception('error config')

#init
programm_mode = config['main_config']['programm_mode']
test_mode = config['main_config']['test_mode']
if test_mode == True:
    table_scan_all = config['for_sql']['table_scan_all_for_test_mode']
    table_workplace_data = config['for_sql']['table_workplace_data_for_test_mode']
else:
    table_scan_all = config['for_sql']['table_scan_all']
    table_workplace_data = config['for_sql']['table_workplace_data']

##
color_yellow = (255, 255, 0)
color_soft_yellow = (179, 170, 18)
color_green = (0, 255, 0)
color_red = (255, 0, 0)
color_gray = (200, 200, 200)
color_dark_gray = (65, 65, 65)
color_orange = (250, 60, 0)

#pygame init
screen_width = config['main_config']['screen_width']
screen_height = config['main_config']['screen_height']
pygame.init()
pygame.display.set_caption('scan')
screen = pygame.display.set_mode([screen_width, screen_height], pygame.FULLSCREEN)
manager = pygame_gui.UIManager([screen_width, screen_height])

#sqlite connect
try:
    local_db = sqlite3.connect(config['for_sql']['local_db_file'])#'local_database_for_stack_documents.db')
    local_db_cursor = local_db.cursor()
except:
    logging.error('error connect to sqlite')
    raise Exception('error sqlite connect')

#mysql connect
try:
    db_host = config['for_sql']['host_to_mysql']#'mx1.droma.me'
    db_user = config['for_sql']['user_to_mysql']#'c3zlicenia'
    db_password = config['for_sql']['password_to_mysql']#'222-Droma-222'
    db_database = config['for_sql']['database_name_to_mysql']#'c3dane_skanowania'
    db_connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_database)
    db_cursor = db_connection.cursor()
except:
    logging.error('error connect to mysql')

#mssql connect
try:
    viso_host = config['for_sql']['mssql_roger_host']
    viso_user = config['for_sql']['mssql_roger_user']
    viso_password = config['for_sql']['mssql_roger_password']
    viso_database = config['for_sql']['mssql_roger_database']
    viso_connection = pymssql.connect(
        host=viso_host,
        user=viso_user,
        password=viso_password,
        database=viso_database)
    viso_cursor = viso_connection.cursor()
except:
    logging.error('error connect to viso')
    viso_connection = None



#db_cursor.commit()

#++++++++++++++++++++++++++++++++++++#
#synchronize db
#synchronize documents_stack
try:
    local_db_cursor.execute("SELECT * FROM documents_stack WHERE on_server = 0")
    rows_to_documents_stack = local_db_cursor.fetchall()
    i_in_while = 0
    if rows_to_documents_stack:
        while i_in_while < len(rows_to_documents_stack):
            db_cursor.execute("""INSERT INTO """+table_scan_all+"""
                              (numer, date, time, open_close)
                              VALUES
                              ("""+str(rows_to_documents_stack[i_in_while][0])+""",
                              '"""+rows_to_documents_stack[i_in_while][1]+"""',
                              '"""+rows_to_documents_stack[i_in_while][2]+"""',
                              """+str(rows_to_documents_stack[i_in_while][3])+""")""")
            db_connection.commit()
            local_db_cursor.execute("""UPDATE documents_stack SET on_server=1 WHERE
                                    numer='"""+str(rows_to_documents_stack[i_in_while][0])+"""' and
                                    time='"""+rows_to_documents_stack[i_in_while][2]+"""'""")
            local_db.commit()
            i_in_while += 1
except:
    logging.error('error synchronize documents_stack')

#synchronize documents_workplace
try:
    local_db_cursor.execute("SELECT * FROM documents_workplace WHERE on_server = 0")
    rows_to_documents_workplace = local_db_cursor.fetchall()

    if rows_to_documents_workplace:
        i_in_while = 0
        while i_in_while < len(rows_to_documents_workplace):
            db_cursor.execute("""INSERT INTO """+table_workplace_data+"""
                              (numer, open_close, date, time, position, count, type, worker_id, time_summary)
                              VALUES
                              ("""+str(rows_to_documents_workplace[i_in_while][0])+""",
                              """+str(rows_to_documents_workplace[i_in_while][1])+""",
                              '"""+rows_to_documents_workplace[i_in_while][2]+"""',
                              '"""+rows_to_documents_workplace[i_in_while][3]+"""',
                              """+str(rows_to_documents_workplace[i_in_while][4])+""",
                              """+str(rows_to_documents_workplace[i_in_while][5])+""",
                              '"""+rows_to_documents_workplace[i_in_while][7]+"""',
                              '"""+rows_to_documents_workplace[i_in_while][8]+"""',
                              """+str(rows_to_documents_workplace[i_in_while][9])+""")""")
            db_connection.commit()
            local_db_cursor.execute("""UPDATE documents_workplace SET on_server=1 WHERE
                                    numer='"""+str(rows_to_documents_workplace[i_in_while][0])+"""' and
                                    time='"""+rows_to_documents_workplace[i_in_while][3]+"""'""")
            local_db.commit()
            i_in_while += 1
except:
    logging.error('error synchronize documents_workplace')


#++++++++++++++++++++++++++++++++++++#
#its mode for scanning documents stack
if programm_mode == 1:
    stack_status = '0'

    #create gui elements
    #console
    console_width = screen_width/2
    console_height = screen_height - 100
    console = pygame_gui.windows.UIConsoleWindow(
        rect = pygame.Rect((screen_width/2, 50), (console_width, console_height)),
        manager = manager)

    #buttons
    exit_button = gui.Button(0, 0, 100, 40, 'X', manager)
    btn_1 = gui.Button(0, 400, 200, 80, 'in', manager)
    btn_2 = gui.Button(0, 480, 200, 80, 'out', manager)
    btn_1.button.disable()

    #set focus to console
    manager.set_focus_set(console.command_entry)

    #enter_key in console
    def enter_key_for_programm_mode_1(numer):
        on_server = '1'
        date_now = datetime.date.today().strftime('%Y-%m-%d')
        time_now = datetime.datetime.now().time().strftime('%H:%M:%S')

        #save to mysql
        try:
            db_cursor.execute("""INSERT INTO """+table_scan_all+"""
                              (numer, date, time, open_close)
                              VALUES
                              ("""+numer+""", '"""+date_now+"""', '"""+time_now+"""', """+stack_status+""")""")
            db_connection.commit()
            on_server = '1'
        except:
            logging.warning('error save to mysql')
            on_server = '0'

        #save to sqlite
        try:
            local_db_cursor.execute("""INSERT INTO documents_stack
                              (numer, date, time, open_close, on_server)
                              VALUES
                              ("""+numer+""", '"""+date_now+"""', '"""+time_now+"""', """+stack_status+""", """+on_server+""")""")
            local_db.commit()
        except:
            logging.error('error sqlite save')
            raise Exception('error save to sqlite')
        console.add_output_line_to_log(time_now)
        console.add_output_line_to_log('====================')
    ####

    clock = pygame.time.Clock()
    running = True
    while running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            ##
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            ##
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == btn_1.button:
                    btn_1.button.disable()
                    btn_2.button.enable()
                    stack_status = '0'
                elif event.ui_element == btn_2.button:
                    btn_2.button.disable()
                    btn_1.button.enable()
                    stack_status = '1'
                elif event.ui_element == exit_button.button:
                    running = False
                manager.set_focus_set(console.command_entry)
            ##
            if (event.type == pygame_gui.UI_CONSOLE_COMMAND_ENTERED and
                    event.ui_element == console):
                command = event.command
                if command != '':
                    enter_key_for_programm_mode_1(command)
            ##
            manager.process_events(event)
        manager.update(time_delta)
        pygame.display.update()
        manager.draw_ui(screen)

    pygame.quit()




#++++++++++++++++++++++++++++++++++++#
#its mode for workplace 
elif programm_mode == 2:
    #create gui elements 
    #vars
    open_close = '0'
    identification_status = False
    identification_string = ''
    open_close_text_block_coord_x = 150
    open_close_text_block_coord_y = 150
    force_end_document = False
    operation_id_uni = random_string(12)
    operation_id_nouni = ''


    #vars for gui
    gui_block_width = 200
    gui_block_height = 250

    #console
    console_width = 400
    console_height = screen_height
    console_x = screen_width-console_width
    console_y = 0
    console = pygame_gui.windows.UIConsoleWindow(
        rect = pygame.Rect((console_x, console_y), (console_width, console_height)),
        manager = manager)
    manager.set_focus_set(console.command_entry)

    #buttons
    exit_button = gui.Button(0, 0, 100, 50, 'X', manager)
    #button_start = gui.Button(screen_width-console_width-(gui_block_width*4),
                              #screen_height-gui_block_height-30,
                              #gui_block_width, gui_block_height/2,
                              #'start',
                              #manager)
    #button_start.button.disable()
    #button_stop = gui.Button(screen_width-console_width-(gui_block_width*4),
                             #screen_height-(gui_block_height/2)-30,
                             #gui_block_width,
                             #gui_block_height/2,
                             #'stop',
                             #manager)
    button_logout = gui.Button(0, 150, 200, 100, 'koniec prace', manager)
    button_forced_end = gui.Button(0, 150+100, 200, 100, 'zamkni zlecenie', manager)

    #counters
    #create font to counters
    text_to_counters_size = 40
    text_to_counters_font = pygame.font.Font(None, text_to_counters_size)

    #create counters
    text_to_counter_for_position = text_to_counters_font.render('pozycja', True, (255, 0, 0))
    counter_for_position = gui.Counter(screen_width-console_width-(gui_block_width*2),
                                       screen_height-gui_block_height-30,
                                       gui_block_width, gui_block_height, True, manager)

    text_to_counter_for_count = text_to_counters_font.render('ilosc', True, (255, 0, 0))
    counter_for_count = gui.Counter(screen_width-console_width-gui_block_width,
                                    screen_height-gui_block_height-30,
                                    gui_block_width, gui_block_height, True, manager)
    litehral_list_for_produkt_counter = config['programm_mode_2']['litheral_list']
    litehral_dict_for_produkt_counter = {}
    i_in_while = 0
    while i_in_while < len(litehral_list_for_produkt_counter):
        litehral_dict_for_produkt_counter[i_in_while] = litehral_list_for_produkt_counter[i_in_while]
        i_in_while += 1
    text_to_counter_for_produkt = text_to_counters_font.render('typ', True, (255, 0, 0))
    counter_for_produkt = gui.Counter(screen_width-console_width-(gui_block_width*3),
                                      screen_height-gui_block_height-30,
                                      gui_block_width, gui_block_height, False,  manager)

    #enter key function
    def enter_key_for_programm_mode_2(numer, status, produkt, position, count, worker_id, uni_operation_id, nouni_operation_id):
        on_server = '1'
        date_now = datetime.date.today().strftime('%Y-%m-%d')
        time_now = datetime.datetime.now().time().strftime('%H:%M:%S')
        #save to mysql
        try:
            str_for_mysql_request = ("""
                INSERT INTO """+table_workplace_data+"""
                (numer, open_close, date, time, position, count, type, worker_id, uni_operation_id, nouni_operation_id)
                VALUES ("""
                +numer+""", '"""
                +status+"""', '"""
                +date_now+"""', '"""
                +time_now+"""', """
                +str(position)+""", """
                +str(count)+""", '"""
                +produkt+"""', '"""
                +worker_id+"""', '"""
                +uni_operation_id+"""', '"""
                +nouni_operation_id+"""')""")
            db_cursor.execute(str_for_mysql_request)
            db_connection.commit()
            on_server = '1'
        except:
            logging.warning('error save to mysql')
            on_server = '0'

        #save to sqlite
        try:
            str_for_sqlite_request = ("""
                INSERT INTO documents_workplace
                (numer, open_close, date, time, position, count, on_server, type, worker_id, uni_operation_id, nouni_operation_id)
                VALUES ("""
                +numer+""", '"""
                +status+"""', '"""
                +date_now+"""', '"""
                +time_now+"""', """
                +str(position)+""", """
                +str(count)+""", '"""
                +on_server+"""', '"""
                +produkt+"""', '"""
                +worker_id+"""', '"""
                +uni_operation_id+"""', '"""
                +nouni_operation_id+"""')""")
            local_db_cursor.execute(str_for_sqlite_request)
            local_db.commit()
        except:
            logging.error('error save to sqlite')
            raise Exception('error save to sqlite')

        #calculate and write time
        if open_close == '1':
            i=0
            local_db_cursor.execute("""SELECT * FROM documents_workplace WHERE
                                    numer="""+numer+""" and
                                    position="""+str(position)+""" and
                                    type='"""+produkt+"""' and
                                    worker_id='"""+worker_id+"""'""")
            rows = local_db_cursor.fetchall()
            if (len(rows) > 2) or (force_end_document == True):
                local_db_cursor.execute("""UPDATE documents_workplace
                                        SET time_summary=-1 WHERE
                                        numer="""+numer+""" and
                                        position="""+str(position)+""" and
                                        type='"""+produkt+"""' and
                                        worker_id="""+worker_id)
                local_db.commit()
                db_cursor.execute("""UPDATE """+table_workplace_data+"""
                                        SET time_summary=-1 WHERE
                                        numer="""+numer+""" and
                                        position="""+str(position)+""" and
                                        type='"""+produkt+"""' and
                                        worker_id="""+worker_id)
                db_connection.commit()
            else:
                time_open = int(rows[0][3][0:2])*60+int(rows[0][3][3:5])
                time_close = int(rows[1][3][0:2])*60+int(rows[1][3][3:5])
                time_summary = time_close-time_open
                local_db_cursor.execute("""UPDATE documents_workplace
                                        SET time_summary="""+str(time_summary)+""" WHERE
                                        numer="""+numer+""" and
                                        position="""+str(position)+""" and
                                        type='"""+produkt+"""' and
                                        worker_id="""+worker_id)
                local_db.commit()
                db_cursor.execute("""UPDATE """+table_workplace_data+"""
                                        SET time_summary="""+str(time_summary)+""" WHERE
                                        numer="""+numer+""" and
                                        position="""+str(position)+""" and
                                        type='"""+produkt+"""' and
                                        worker_id="""+worker_id)
                db_connection.commit()
        console.add_output_line_to_log(time_now)
        console.add_output_line_to_log('====================')

    #disable elements if no identification
    if identification_status == False:
        #counter_for_count.counter_off()
        #counter_for_position.counter_off()
        #counter_for_produkt.counter_off()
        #button_logout.button.disable()
        button_forced_end.button.disable()
        ####
        button_forced_end.hide_button()
        button_logout.hide_button()
        counter_for_count.counter_hide()
        counter_for_position.counter_hide()
        counter_for_produkt.counter_hide()

    #render text
    text_start_stop_text_size = 60
    text_start_stop_font = pygame.font.Font(None, text_start_stop_text_size)
    #text_start_text = text_start_stop_font.render('start', True, (255, 50, 50))
    #text_stop_text = text_start_stop_font.render('stop', True, (255, 50, 50))

    #while to programm mode 2
    clock = pygame.time.Clock()
    running = True
    ####
    while running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                #buttons
                if event.ui_element == exit_button.button:
                    running = False
                elif event.ui_element == button_logout.button:
                    identification_status = False
                    #counter_for_count.counter_off()
                    #counter_for_position.counter_off()
                    #counter_for_produkt.counter_off()
                    #button_logout.button.disable()
                    #button_forced_end.button.disable()
                    button_forced_end.hide_button()
                    button_logout.hide_button()
                    counter_for_count.counter_hide()
                    counter_for_position.counter_hide()
                    counter_for_produkt.counter_hide()

                    ##########
                    ##########
                elif event.ui_element == button_forced_end.button:
                    force_end_document = True
                    enter_key_for_programm_mode_2(command,
                                                  open_close,
                                                  litehral_dict_for_produkt_counter[counter_for_produkt.counter],
                                                  counter_for_position.counter,
                                                  counter_for_count.counter,
                                                  identification_string,
                                                  operation_id_uni,
                                                  operation_id_nouni)
                    force_end_document = False
                    open_close = '0'
                    button_forced_end.button.disable()

                #counter_for_position buttons
                elif event.ui_element == counter_for_position.button_plus:
                    counter_for_position.counter += 1
                elif event.ui_element == counter_for_position.button_minus:
                    counter_for_position.counter -= 1
                    if counter_for_position.counter < 0:
                        counter_for_position.counter = 0

                #counter_for_count buttons
                elif event.ui_element == counter_for_count.button_plus:
                    counter_for_count.counter += 1
                elif event.ui_element == counter_for_count.button_minus:
                    counter_for_count.counter -= 1
                    if counter_for_count.counter < 0:
                        counter_for_count.counter = 0

                #counter_for_produkt buttons
                elif event.ui_element == counter_for_produkt.button_plus:
                    counter_for_produkt.counter += 1
                    if counter_for_produkt.counter >= len(litehral_list_for_produkt_counter):
                        counter_for_produkt.counter -= 1
                elif event.ui_element == counter_for_produkt.button_minus:
                    counter_for_produkt.counter -= 1
                    if counter_for_produkt.counter < 0:
                        counter_for_produkt.counter = 0
                manager.set_focus_set(console.command_entry)
            if (event.type == pygame_gui.UI_CONSOLE_COMMAND_ENTERED and
                    event.ui_element == console):
                command = event.command
                if command != '':
                    if identification_status == False:
                        identification_string = command
                        ##
                        try:
                            viso_cursor.execute("SELECT Name, UserExternalIdentifier FROM "
                                                +config['for_sql']['mssql_roger_workers_table']+" WHERE UserExternalIdentifier='"
                                                +identification_string+"'")
                            rows_from_viso = viso_cursor.fetchall()
                            if rows_from_viso:
                                console.add_output_line_to_log(rows_from_viso[0][0])
                        except:
                            logging.error("error read worker name")
                        ##
                        identification_status = True
                        button_forced_end.show_button()
                        button_logout.show_button()
                        counter_for_count.counter_show()
                        counter_for_position.counter_show()
                        counter_for_produkt.counter_show()
                    elif identification_status == True:
                        #nouni_id create
                        operation_id_nouni = (command +
                                            litehral_dict_for_produkt_counter[counter_for_produkt.counter] +
                                            str(counter_for_position.counter) +
                                            str(counter_for_count.counter) +
                                            str(identification_string))
                        enter_key_for_programm_mode_2(command,
                                                      open_close,
                                                      litehral_dict_for_produkt_counter[counter_for_produkt.counter],
                                                      counter_for_position.counter,
                                                      counter_for_count.counter,
                                                      identification_string,
                                                      operation_id_uni,
                                                      operation_id_nouni)
                        if open_close == '0':
                            open_close = '1'
                            button_forced_end.button.enable()
                        else:
                            open_close = '0'
                            button_forced_end.button.disable()
                            operation_id_uni = random_string(12)
                            #uni_id create
            #else:
                #manager.set_focus_set(console.command_entry)
            if event.type == pygame.BUTTON_LEFT:
                manager.set_focus_set(console.command_entry)
            manager.process_events(event)
        manager.update(time_delta)

        #render
        if identification_status == True:
            #counters render
            #counter_for_position
            counter_for_position.render(screen)
            screen.blit(text_to_counter_for_position,
                        (screen_width-console_width-(gui_block_width*2)+(gui_block_width/4),
                         screen_height-gui_block_height-60))
            #counter_for_count
            counter_for_count.render(screen)
            screen.blit(text_to_counter_for_count,
                        (screen_width-console_width-gui_block_width+(gui_block_width/4),
                         screen_height-gui_block_height-60))
            #counter_for_product
            counter_for_produkt.render(screen)
            screen.blit(text_to_counter_for_produkt,
                        (screen_width-console_width-(gui_block_width*3)+(gui_block_width/4),
                         screen_height-gui_block_height-60))
            #
            litehral_counter_for_produkt = counter_for_produkt.counter_text_font.render(litehral_dict_for_produkt_counter
                                                                                        [counter_for_produkt.counter],
                                                                                        True,
                                                                                        (255, 50, 50))
            screen.blit(litehral_counter_for_produkt,
                        (counter_for_produkt.coord_x+(counter_for_produkt.counter_width/3),
                         counter_for_produkt.counter_block_coord_y+(counter_for_produkt.block_height/4)))
            ##
            pygame.display.update()
            screen.fill((0, 0, 0))
            manager.draw_ui(screen)
            #draw objects
            #if identification_status == True:
                #pygame.draw.ellipse(screen, color_green, pygame.Rect(console_x-100, console_y+18, 100, 100))
            #else:
                #pygame.draw.ellipse(screen, color_yellow, pygame.Rect(console_x-150, console_y+18, 150, 150))
            #draw open_close status
            if open_close == '0':
                #counter_text = counter_text_font.render('', True, (255, 50, 50))
                #screen.blit(counter_text,
                            #(coord_x+(counter_width/3),
                            #counter_block_coord_y+(block_height/4)))
                pygame.draw.rect(screen, color_soft_yellow, pygame.Rect(
                                    screen_width-console_width-(gui_block_width*4),
                                    screen_height-gui_block_height-30,
                                    gui_block_width,
                                    gui_block_height/2))
                pygame.draw.rect(screen, color_dark_gray, pygame.Rect(
                                    screen_width-console_width-(gui_block_width*4),
                                    screen_height-(gui_block_height/2)-30,
                                    gui_block_width,
                                    gui_block_height/2))
                text_start_text = text_start_stop_font.render('start', True, (255, 0, 0))
                text_stop_text = text_start_stop_font.render('stop', True, (120, 50, 50))
            else:
                pygame.draw.rect(screen, color_dark_gray, pygame.Rect(
                                    screen_width-console_width-(gui_block_width*4),
                                    screen_height-gui_block_height-30,
                                    gui_block_width,
                                    gui_block_height/2))
                pygame.draw.rect(screen, color_soft_yellow, pygame.Rect(
                                    screen_width-console_width-(gui_block_width*4),
                                    screen_height-(gui_block_height/2)-30,
                                    gui_block_width,
                                    gui_block_height/2))
                text_start_text = text_start_stop_font.render('start', True, (120, 50, 50))
                text_stop_text = text_start_stop_font.render('stop', True, (255, 0, 0))
            ##
            pygame.draw.rect(screen, color_green, pygame.Rect(
                                screen_width-console_width-(gui_block_width*4),
                                screen_height-(gui_block_height/2)-40,
                                gui_block_width,
                                10))
            ####
            screen.blit(text_start_text, (screen_width-console_width-(gui_block_width*4)+(gui_block_width/4),
                                          screen_height-gui_block_height+10))
            screen.blit(text_stop_text, (screen_width-console_width-(gui_block_width*4)+(gui_block_width/4),
                                         screen_height-(gui_block_height/2)+10))
        else:
            pygame.display.update()
            screen.fill((0, 0, 0))
            manager.draw_ui(screen)
            id_text_pl = text_start_stop_font.render('odskanowac kod', True, (255, 50, 50))
            id_text_ua = text_start_stop_font.render('відсканувати код', True, (255, 50, 50))
            screen.blit(id_text_pl, (100, 100))
            screen.blit(id_text_ua, (100, 200))


    pygame.quit()

#++++++++++++++++++++++++++++++++++++#

db_connection.close()
logging.info('end programm')
logging.info('============')
























