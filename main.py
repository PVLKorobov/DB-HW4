import psycopg2

# Создание таблиц
def createTables(conn):
    with conn.cursor() as cur:
            cur.execute("""
                    DROP TABLE IF EXISTS phoneNums;
                    DROP TABLE IF EXISTS clients;
                        """)
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS clients(
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(40) NOT NULL,
                    surname VARCHAR(40) NOT NULL,
                    email VARCHAR(30) UNIQUE NOT NULL
                    );
                        """)
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS phoneNums(
                    id SERIAL PRIMARY KEY,
                    userId INTEGER REFERENCES clients(id),
                    userPhone VARCHAR(15) UNIQUE
                    )
                        """)
            conn.commit()

# Добавление данных о клиенте
def addClient(conn, firstName, secondName, email, phones=None):
    with conn.cursor() as cur:
            cur.execute("""
                    INSERT INTO clients(name, surname, email)
                    VALUES(%s, %s, %s) RETURNING id;
                        """, (firstName, secondName, email))
            insertedId = cur.fetchone()
            conn.commit()

            if phones != None:
                for number in phones:
                    cur.execute("""
                            INSERT INTO phoneNums(userId, userPhone)
                            VALUES(%s, %s);
                                """, (insertedId, number))
            conn.commit()

# Добавление номера для существующего клиента
def addPhone(conn, clientId, phone):
     with conn.cursor() as cur:
        cur.execute("""
                INSERT INTO phoneNums(userId, userPhone)
                VALUES(%s, %s);
                    """, (clientId, phone))
        conn.commit()

# Изменение данных о клиенте
def changeInfo(conn, clientId, name=None, surname=None, email=None, phones=None):
    with conn.cursor() as cur:
        if name != None:
            cur.execute("""
                    UPDATE clients
                    SET name=%s
                    WHERE id=%s;
                        """, (name, clientId))
        if surname != None:
            cur.execute("""
                    UPDATE clients
                    SET surname=%s
                    WHERE id=%s;
                        """, (surname, clientId))
        if email != None:
            cur.execute("""
                    UPDATE clients
                    SET email=%s
                    WHERE id=%s;
                        """, (email, clientId))
        if phones != None:
            cur.execute("""
                    DELETE FROM phoneNums
                    WHERE userId=%s;
                        """, (clientId,))
            for phone in phones:
                cur.execute("""
                        INSERT INTO phoneNums(userId, userPhone)
                        VALUES(%s, %s);
                            """, (clientId, phone))
        conn.commit()

# Удаление телефона существующего клиента
def deletePhone(conn, clientId, phone):
    with conn.cursor() as cur:
        cur.execute("""
                DELETE FROM phoneNums
                WHERE userId=%s AND userPhone=%s;
                    """, (clientId, phone))
        conn.commit()
        
# Удаление записи о клиенте
def deleteClient(conn, clientId):
    with conn.cursor() as cur:
        cur.execute("""
                DELETE FROM phoneNums
                WHERE userId=%s;
                    """, (clientId,))
        conn.commit()
        cur.execute("""
                DELETE FROM clients
                WHERE id=%s;
                    """, (clientId,))
        conn.commit()

# Поиск клиента по данным
def findClient(conn, name='', surname='', email='', phone=''):
    print('Результат поиска по', name, surname, email, phone, '\n=============')
    with conn.cursor() as cur:
        userData = ()
        phoneData = []
        if email != '':
            cur.execute("""
                    SELECT * FROM clients
                    WHERE email=%s;
                        """, (email,))
            userData = cur.fetchone()
            cur.execute("""
                    SELECT userPhone FROM phoneNums
                    WHERE userId=%s
                        """, (userData[0],))
            phoneData = cur.fetchall()
        elif phone != '':
            cur.execute("""
                    SELECT userId FROM phoneNums
                    WHERE userPhone=%s;
                        """, (phone,))
            userId = cur.fetchone()

            cur.execute("""
                    SELECT * FROM clients
                    WHERE id=%s;
                        """, (userId[0],))
            userData = cur.fetchone()
            cur.execute("""
                    SELECT userPhone FROM phoneNums
                    WHERE userId=%s
                        """, (userId[0],))
            phoneData = cur.fetchall()
        elif name != '' and surname != '':
            cur.execute("""
                    SELECT * FROM clients
                    WHERE name=%s AND surname=%s;
                        """, (name,surname))
            userData = cur.fetchall()
        elif name != '':
            cur.execute("""
                    SELECT * FROM clients
                    WHERE name=%s;
                        """, (name,))
            userData = cur.fetchall()
        elif surname != '':
            cur.execute("""
                    SELECT * FROM clients
                    WHERE surname=%s;
                        """, (surname,))
            userData = cur.fetchall()
                
        if type(userData) == list:
            for entry in userData:
                cur.execute("""
                        SELECT userPhone FROM phoneNums
                        WHERE userId=%s
                            """, (entry[0],))
                phoneData = cur.fetchall()
                print(entry[1], entry[2], ' email:', entry[3], ' id:', entry[0])
                print('Номер(а) телефона:', end=' ')
                for tuple in phoneData:
                    print(tuple[0], end=' ')
                print('\n--')
            print()
        else:
            print(userData[1], userData[2], ' email:', userData[3], ' id:', userData[0])
            print('Номер(а) телефона:', end=' ')
            for tuple in phoneData:
                    print(tuple[0], end=' ')
            print('\n')


with psycopg2.connect(database='', user='', password='') as conn:
    # Создание таблиц
    createTables(conn)
    # Добавление данных о клиентах
    with open('userData.txt') as dataFile:
        for line in dataFile:
            lineList = line.split(' ')
            if len(lineList) == 3:
                addClient(conn, lineList[0], lineList[1], lineList[2].strip())
            else:
                phoneNumTuple = ()
                for i in range(3, len(lineList)):
                    phoneNumTuple += (lineList[i].strip(),)
                addClient(conn, lineList[0], lineList[1], lineList[2], phoneNumTuple)
    # Добавление номера для существующего клиента
    addPhone(conn, 1, '88005553535')
    # Изменение данных о клиенте
    changeInfo(conn, 2, 'Dan', 'Conwell', None, ('94929814', '25398536', '6326527'))
    # Удаление телефона существующего клиента
    deletePhone(conn, 2, '25398536')
    # Удаление записи о клиенте
    deleteClient(conn, 1)
    # Поиск клиента по данным
    findClient(conn, name='Dan')
    findClient(conn, email='jfi@gmail.net')
    findClient(conn, phone='94929814')