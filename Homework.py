import psycopg2

# Функция, создающая структуру БД (таблицы).
def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS client(
            client_id serial primary key,
            first_name varchar(50) not null,
            last_name varchar(50) not null, 
            email varchar(50));  
            """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS phone (
    	    phone_id serial primary key,
    	    phone_number varchar(20) unique,
    	    client_id integer not null references client(client_id));
            """)
        conn.commit()

# Функция, позволяющая добавить нового клиента.
def add_new_client(conn, first_name, last_name, email):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO client(first_name, last_name, email)
         VALUES (%s, %s, %s) RETURNING client_id;
         """, (first_name, last_name, email))
        client_id = cur.fetchone()[0]
        conn.commit()
    return client_id

# Функция, позволяющая добавить телефон для существующего клиента.
def add_phone_number(conn, client_id, phone_number):
    if len(find_client(conn, phone_number)) == 0: # list is empty
        with conn.cursor() as cur:
            cur.execute("""
               INSERT INTO phone(phone_number, client_id)
               VALUES (%s, %s);
                """, (phone_number, client_id))
            conn.commit()

#Функция, позволяющая изменить данные о клиенте.
def update_client(conn, client_id, first_name, last_name, email):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE client 
            SET first_name = %s,
            last_name = %s,
            email = %s
            WHERE client_id = %s;
             """, (first_name, last_name, email, client_id))
        conn.commit()
#Функция, которая возвращает всe телефоны привязанные к клиенту.
def print_phone_number(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
        SELECT phone_id, phone_number 	
        FROM phone
        WHERE client_id = %s
        """, (client_id,))
        return cur.fetchall()

#Функция, позволяющая удалить телефон для существующего клиента.
def delete_phone(conn, phone_id):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM phone 
        WHERE phone_id=%s
        """, (phone_id,))
        conn.commit()
#Функция, позволяющая удалить существующего клиента.
def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM client 
        WHERE client_id=%s
        """, (client_id,))
        conn.commit()

#Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону.
def find_client(conn, data):
    with conn.cursor() as cur:
        cur.execute("""
        SELECT c.client_id, c.first_name, c.last_name, c.email
        from client c 
        left join phone p on c.client_id = p.client_id 
        where p.phone_number ilike %(data)s 
        or c.first_name ilike %(data)s 
        or c.last_name ilike %(data)s 
        or c.email ilike %(data)s
        order by client_id
        """, {'data': '%'+data+'%'})
        return cur.fetchall()
        #if output is not None:
            #result = output
    #return output

conn = psycopg2.connect(database='clients_management',
                        user='postgres',
                        password='1234')
test = create_tables(conn)
first_client = add_new_client(conn,'Alex', 'Jones', 'alexjones@gmail.com')
print(first_client)
add_phone_number(conn, first_client, str(first_client)+'-410-459-5056')
first_find_client = find_client(conn, str(first_client)+'-410-459-5056')
print(first_find_client)
update_client(conn, client_id=first_client, first_name='Alex', last_name='Jackson', email='alexjones@gmail.com')
print(find_client(conn, data=str(first_client)+'-410-459-5056'))
phone_data = print_phone_number(conn, first_client)
print(phone_data)
delete_phone(conn, phone_data[0][0])
print(print_phone_number(conn, first_client))
print(delete_client(conn, first_client))



