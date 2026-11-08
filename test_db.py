
from database import get_db_connection

db = get_db_connection()

if db and db.is_connected():

    print("\n================================")
    print("       YOGABITE DATABASE")
    print("================================")

    print("Connection: Successful")
    print("Database:", db.database)

    cursor = db.cursor()
    cursor.execute("SHOW TABLES")

    print("\nAvailable Tables:")

    tables = cursor.fetchall()

    for table in tables:
        print("-", table[0])

    cursor.close()
    db.close()

    print("\nDatabase test completed!")

else:
    print("Database connection failed!")
