import psycopg2
from psycopg2 import sql

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
    	    client_id integer not null references client(client_id) ON DELETE CASCADE ON UPDATE CASCADE)
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
def update_client(conn, client_id, first_name=None, last_name=None, email=None):
    if not first_name and not last_name and not email:
        return
    first_name_param = sql.SQL('')
    last_name_param = sql.SQL('')
    email_param = sql.SQL('')
    if first_name:
        first_name_param = sql.SQL('first_name = {}').format(sql.Literal(first_name))
    if last_name:
        last_name_param = sql.SQL('last_name = {}').format(sql.Literal(last_name))
    if email:
        email_param = sql.SQL('email = {}').format(sql.Literal(email))
    filtered_items = filter(lambda param: param != sql.SQL(''), [first_name_param, last_name_param, email_param])
    all_params = sql.SQL(',').join(filtered_items)
    print(all_params.as_string(conn))
    with conn.cursor() as cur:
        cur.execute(sql.Composed([
            sql.SQL("UPDATE client SET "),
            all_params,
            sql.SQL("WHERE client_id = %s;")]),
            (client_id, ))

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
        DELETE FROM client CASCADE 
        WHERE client_id=%s  
        """, (client_id,))
        conn.commit()

#Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону.
def find_client(conn,phone_number=None, first_name=None, last_name=None, email=None):
    output = []
    if not phone_number and not first_name and not last_name and not email:
        return []
    phone_number_param = sql.SQL('')
    first_name_param = sql.SQL('')
    last_name_param = sql.SQL('')
    email_param = sql.SQL('')
    if phone_number:
        phone_number_param = sql.SQL('p.phone_number ilike {}').format(sql.Literal(phone_number))
    if first_name:
        first_name_param = sql.SQL('c.first_name ilike {}').format(sql.Literal(first_name))
    if last_name:
        last_name_param = sql.SQL('c.last_name ilike {}').format(sql.Literal(last_name))
    if email:
        email_param = sql.SQL('c.email ilike {}').format(sql.Literal(email))
    filtered_items = filter(lambda param: param != sql.SQL(''), [phone_number_param, first_name_param, last_name_param, email_param])
    all_params = sql.SQL(' and ').join(filtered_items)

    with conn.cursor() as cur:
        cur.execute(
            sql.Composed([
                sql.SQL("""SELECT c.client_id, c.first_name, c.last_name, c.email
                    from client c 
                    left join phone p on c.client_id = p.client_id 
                    WHERE """),
                all_params,
                sql.SQL("order by client_id;")]))
        output = cur.fetchall()
        #if output is not None:
            #result = output
    return output


if __name__ == "__main__":
    conn = psycopg2.connect(database='clients_management',
                            user='postgres',
                            password='1234')
    test = create_tables(conn)
    first_client = add_new_client(conn, 'Alex', 'Jones', 'alexjones@gmail.com')
    print(first_client)
    add_phone_number(conn, first_client, str(first_client) + '-410-459-5056')
    first_find_client = find_client(conn, str(first_client) + '-410-459-5056')
    print(first_find_client)
    update_client(conn, client_id=first_client, first_name='Alex', last_name='Jackson', email='alexjones@gmail.com')
    print(find_client(conn, str(first_client) + '-410-459-5056'))
    phone_data = print_phone_number(conn, first_client)
    print(phone_data)
    delete_phone(conn, phone_data[0][0])
    print(print_phone_number(conn, first_client))
    print(delete_client(conn, first_client))
else:
    print("Module Homework will be imported in a different module")






