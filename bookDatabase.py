import sqlite3

shelf_width = 24.75
max_rows = 3

## _______________________PUBLIC FUNCTIONS ____________________________
#returns connection
def initDb():
    conn = sqlite3.connect('bookDatabase.db',check_same_thread=False)
    
    print ("Opened database!\n");
    
    conn.execute('''CREATE TABLE IF NOT EXISTS BOOK
            (ISBN TEXT PRIMARY KEY NOT NULL,
            NAME TEXT NOT NULL,
            WIDTH REAL NOT NULL,
            CHECKED_IN INT NOT NULL,
            ROW INT NOT NULL,
            POSITION REAL NOT NULL);''')

    conn.execute('''CREATE TABLE IF NOT EXISTS ROWS
                    (ROW_NUM INT PRIMARY KEY NOT NULL,
                    END_POSITION REAL NOT NULL);''')
    
    print ("Table opened successfully!\n");
    return conn

# insert a book given ISBN, name and width
# retval: row - which row the book is on
#         position - position the book is located in inches from the left
def insertBook( conn, isbn, name, width ):
    if conn:
        print "Adding " + name + " to library..."
        print isbn
        width = float(width)
        # check if this book exists first
        rc, row, position = checkBook(conn, isbn)
        if rc:
            return row, position
        else:
            #find where to put the book, try each row
            for row in range(0,max_rows):
                position = checkRow(conn, row, width )
                if position is not 'NaN':
                    addBookToDatabase( conn, isbn, name, width, row, position )
                    updateRowOnDatabase( conn, row, position+width )
                    print(name + " added to row " + str(row) + " at " + str(position) + " inches!")
                    return row, position
        #if no room for book, don't print
        return 'NaN','NaN'

# check if book already exists, if it already exists, we can put the book back in
# returns if run or not
def checkBook( conn, isbn ):
    if conn:
        c = conn.cursor()
        c.execute("SELECT * FROM {tn} WHERE {cn}='{isbn_num}'".\
                format(tn='BOOK', cn='ISBN', isbn_num=isbn))
        all_rows = c.fetchall()

        # if book already exists, check if it's checked in
        if all_rows:
            if all_rows[0][3]:
                print ("Duplicate book error!")
            else:   # check book back in
                conn.execute("UPDATE BOOK SET CHECKED_IN=1 WHERE ISBN='"+isbn+"'");
                conn.commit()
                print("Checked in " + all_rows[0][1])
                return 1, all_rows[0][4], all_rows[0][5]
        else:
            print("Failed to find " + isbn)
        return 0,0,0
            
# check if book exists and check it out
def checkOutBook( conn, name ):
    if conn:
        c = conn.cursor()
        c.execute("SELECT * FROM {tn} WHERE {cn}='{book_name}'".\
                format(tn='BOOK', cn='NAME', book_name=name))
        all_rows = c.fetchall()

        # if book already exists, check if it's checked in
        if all_rows:
            if all_rows[0][3]:
                conn.execute("UPDATE BOOK SET CHECKED_IN=0 WHERE NAME='"+name+"'");
                conn.commit()
                print("Checked out " + name)
                return all_rows[0][4], all_rows[0][5]
            else:   # check book back in
                print("Book is not checked in!")
        else:
            print("Book does not exist!")

        return 'NaN','NaN'

# check if book exists and check it out
def checkOutBook( conn, isbn ):
    if conn:
        c = conn.cursor()
        c.execute("SELECT * FROM {tn} WHERE {cn}='{book_name}'".\
                format(tn='BOOK', cn='ISBN', book_name=isbn))
        all_rows = c.fetchall()

        # if book already exists, check if it's checked in
        if all_rows:
            if all_rows[0][3]:
                conn.execute("UPDATE BOOK SET CHECKED_IN=0 WHERE ISBN='"+isbn+"'");
                conn.commit()
                print("Checked out " + isbn)
                return all_rows[0][4], all_rows[0][5]
            else:   # check book back in
                print("Book is not checked in!")
        else:
            print("Book does not exist!")

        return 'NaN','NaN';

# delete book
def deleteBook( conn, isbn ):
    rc = 0 #0 -failure 1 -success
    if conn:
        conn.execute("DELETE FROM BOOK WHERE ISBN=?",(isbn,))
        conn.commit()

        # check if book is deleted
        c = conn.cursor()
        c.execute("SELECT * FROM {tn} WHERE {cn}='{isbn_number}'".\
                format(tn='BOOK', cn='ISBN', isbn_number=isbn))
        all_rows = c.fetchall()
        if all_rows:
            print( "Book is not deleted " + ISBN )
        else:
            print("Deleted book " + isbn)
            rc = 1
    return rc

## _________________________ PRIVATE FUNCTIONS ______________________
# add a book to the database
def addBookToDatabase( conn, isbn, name, width, row, position ):
    if conn:
        print ("Insert book!");
        conn.execute( "INSERT INTO BOOK (ISBN,NAME,WIDTH,CHECKED_IN,ROW,POSITION) \
                      VALUES ('"+isbn+"', '"+name+"', "+str(width)+", 1, "+str(row)+", "+str(position)+" )" );
        conn.commit()

# print current library
def printLibrary(conn, table):
    print ("Print library!\n");
    cursor = conn.execute("SELECT * from {tn}".format(tn=table))
    for row in cursor:
        if table is 'BOOK':
            print "ISBN = ", row[0]
            print "NAME = ", row[1]
            print "WIDTH = ", row[2]
            print "CHECKED_IN = ", row[3]
            print "ROW = ", row[4]
            print "POSITION = ", row[5], "\n"
        elif table is 'ROWS':
            print "ROW_NUM = ", row[0]
            print "END_POSITION = ", row[1], "\n"


# return library as list of  dictionary object
def returnAsDict( conn, table):
    cursor = conn.execute("SELECT * from {tn}".format(tn=table))
    myList = []
    dictionary = {}
    for row in cursor:
        if table is 'BOOK':
            d = {
                    "ISBN": row[0],
                    "NAME": row[1],
                    "WIDTH": row[2],
                    "CHECKED_IN": row[3],
                    "ROW" : row[4],
                    "POSITION": row[5],
            }

            # dictionary["ISBN "] = row[0]
            # dictionary[ "NAME" ] = row[1]
            # # dictionary[ "WIDTH" ] = row[2]
            # dictionary[ "CHECKED_IN "] = row[3]
            # dictionary[ "ROW = "] =  row[4]
            # dictionary[ "POSITION"] =  row[5]
        # elif table is 'ROWS':
            # print "ROW_NUM = ", row[0]
            # print "END_POSITION = ", row[1], "\n"
            myList.append(d)
    return myList
        

# check row to see where to place the book
# input:
#   conn - connection to the database
#   row  - row we are querying
#   width - width of book we are trying to enter
# retval: position to the right of the start of the row in inches
#         if row is full, return NaN
def checkRow( conn, row, width ):
    if conn:
        c = conn.cursor()
        c.execute('SELECT {pn} FROM {tn} WHERE {cn}={row_num}'.\
                format(pn = 'END_POSITION', tn='ROWS', cn='ROW_NUM', row_num=row))
        all_rows = c.fetchall()
        print all_rows
        if all_rows:
            position = all_rows[0][0]
        else:
            position = 0
    
        #check if we have exceeded the limit
        #TODO make this more robust, factor in offset
        if (position + float(width)) > shelf_width:
            return 'NaN'
        else:
            return position

# add a row to the database
def updateRowOnDatabase( conn, row, position ):
    if conn:
        print ("Update row!")
        conn.execute( "DELETE from ROWS where ROW_NUM=" + str(row) )
        conn.execute( "INSERT INTO ROWS (ROW_NUM,END_POSITION) \
                      VALUES ("+str(row)+", "+str(position)+") ");
        conn.commit()


if __name__ == "__main__":
    conn = initDb()
    # checkOutBook(conn, 'Test Book')
    # checkBook(conn,92598990)
    # insertBook(conn,'0545010225','Test Book',0.6)
    # insertBook(conn,93472340,'Test Book 2',1.6)
    # insertBook(conn,91249870,'Test Book 3',0.2)
    # insertBook(conn,95999870,'Test Book 4',24.2)
    # insertBook(conn,91234890,'Test Book 5',10.3)
    # printLibrary(conn,'BOOK')
    # printLibrary(conn,'ROWS')
    myList = returnAsDict( conn, 'BOOK' )
    for dictionary in myList:
        for key in dictionary:
            print key, ' = ', dictionary[key]
