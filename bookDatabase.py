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
            HEIGHT REAL NOT NULL,
            CHECKED_IN INT NOT NULL,
            ROW INT NOT NULL,
            POSITION REAL NOT NULL);''')

    # Row Database
    # Contains:
    #   Row Num
    #   Start Position
    #   Width
    #   Height
    # conn.execute('''CREATE TABLE IF NOT EXISTS ROWS
                    # (ROW_NUM INT PRIMARY KEY NOT NULL,
                    # END_POSITION REAL NOT NULL);''')
    conn.execute('''CREATE TABLE IF NOT EXISTS ROWS
                    (ROW_NUM INT NOT NULL,
                    START_POS REAL NOT NULL,
                    WIDTH REAL NOT NULL,
                    HEIGHT REAL NOT NULL,
                    PRIMARY KEY (ROW_NUM, START_POS));''')
    
    print ("Table opened successfully!\n");
    return conn

# init bookshelf values, ran once
# input
#   conn
#   rowList: List of bookshelf width and height dictionary for each shelf
#       Width: 
#       Height :
def initBookshelf( conn, rowList = [] ):
    # check to see if any books are in the db, if so cannot change values
    cursor = conn.execute("SELECT * from {tn}".format(tn='BOOK'))
    if cursor.fetchall():
        print(cursor.fetchall())
        print("Cannot update values when there are books in the db!");
        return False
    # insert each row into db
    rowId = 0
    for row in rowList:
        conn.execute( "INSERT INTO ROWS (ROW_NUM,START_POS,WIDTH,HEIGHT) \
                      VALUES ("+str(rowId)+", 0, "+str(row['Width'])+","+str(row['Height'])+") ");
        print("Adding row "+str(rowId)+" of width "+str(row['Width'])+" and height "+str(row['Height']))
        rowId = rowId + 1
    conn.commit()
    return True

# insert a book given ISBN, name and width
# retval: row - which row the book is on
#         position - position the book is located in inches from the left
def insertBook( conn, isbn, name, width, height ):
    if conn:
        print ("Adding " + name + " to library...")
        print (isbn)
        width = float(width)
        # check if this book exists first
        rc, row, position,dbWidth = checkBook(conn, isbn)
        if rc:
            return row, position, width
        else:
            #find where to put the book, try each row
            # for row in range(0,max_rows):
                # position = checkRow(conn, row, width )
                # if position is not 'NaN':
                    # addBookToDatabase( conn, isbn, name, width, row, position )
                    # updateRowOnDatabase( conn, row, position+width )
            row, position = findRowPos(conn,width, height)
            print(name + " added to row " + str(row) + " at " + str(position) + " inches!")
            addBookToDatabase( conn, isbn, name, width, height, row, position)
            return row, position, width
        return 'NaN','NaN', 'NaN'

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
            if all_rows[0][4]:
                print ("Duplicate book error!")
                return 1 #can't tdo anything just return value
            else:   # check book back in
                conn.execute("UPDATE BOOK SET CHECKED_IN=1 WHERE ISBN='"+isbn+"'");
                conn.commit()
                print("Checked in " + all_rows[0][1])
                return 1, all_rows[0][5], all_rows[0][6], all_rows[0][2]
        else:
            print("Failed to find " + isbn)
        return 0,0,0,0
            
# check if book exists and check it out
def checkOutBook( conn, name ):
    if conn:
        c = conn.cursor()
        c.execute("SELECT * FROM {tn} WHERE {cn}='{book_name}'".\
                format(tn='BOOK', cn='NAME', book_name=name))
        all_rows = c.fetchall()

        # if book already exists, check if it's checked in
        if all_rows:
            if all_rows[0][4]:
                conn.execute("UPDATE BOOK SET CHECKED_IN=0 WHERE NAME='"+name+"'");
                conn.commit()
                print("Checked out " + name)
                return all_rows[0][5], all_rows[0][6], all_rows[0][2]   #return row,pos,width
            else:   # check book back in
                print("Book is not checked in!")
        else:
            print("Book does not exist!")

        return 'NaN','NaN','NaN'

# check if book exists and check it out
def checkOutBook( conn, isbn ):
    if conn:
        c = conn.cursor()
        c.execute("SELECT * FROM {tn} WHERE {cn}='{book_name}'".\
                format(tn='BOOK', cn='ISBN', book_name=isbn))
        all_rows = c.fetchall()

        # if book already exists, check if it's checked in
        if all_rows:
            if all_rows[0][4]:
                conn.execute("UPDATE BOOK SET CHECKED_IN=0 WHERE ISBN='"+isbn+"'");
                conn.commit()
                print("Checked out " + isbn)
                return all_rows[0][5], all_rows[0][6], all_rows[0][2]   #return row,pos,width
            else:   # check book back in
                print("Book is not checked in!")
        else:
            print("Book does not exist!")

        return 'NaN','NaN','NaN';

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
def addBookToDatabase( conn, isbn, name, width, height, row, position ):
    if conn:
        print ("Insert book!");
        conn.execute( "INSERT INTO BOOK (ISBN,NAME,WIDTH,HEIGHT,CHECKED_IN,ROW,POSITION) \
                      VALUES ('"+isbn+"', '"+name+"', "+str(width)+", "+str(height)+", 1, "+str(row)+", "+str(position)+" )" );
        conn.commit()

# print current library
def printLibrary(conn, table):
    print ("Print library!\n");
    cursor = conn.execute("SELECT * from {tn}".format(tn=table))
    for row in cursor:
        if table is 'BOOK':
            print ("ISBN = ", row[0])
            print ("NAME = ", row[1])
            print ("WIDTH = ", row[2])
            print ("CHECKED_IN = ", row[3])
            print ("HEIGHT = ", row[4])
            print ("ROW = ", row[5])
            print ("POSITION = ", row[6], "\n")
        elif table is 'ROWS':
            print ("ROW_NUM = ", row[0])
            print ("END_POSITION = ", row[1], "\n")


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
                    "HEIGHT": row[3],
                    "CHECKED_IN" : row[4],
                    "ROW" : row[5],
                    "POSITION": row[6],
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
        else:
            for column in row:
                print(column)
    return myList
        
# shelf helper functions
# find a free row and pos on the bookshelf for the new book
def findRowPos( conn, width, height ):
    if conn:
        c = conn.cursor()
        #select all values that will fit our required height and width
        c.execute('SELECT * FROM {tn} WHERE {cn}>{height_num} AND {cn2}>={width_num} '\
                'ORDER BY {cn} ASC, {cn2} ASC'.\
                format(tn='ROWS', cn='HEIGHT', height_num=height, cn2='WIDTH', width_num=width))
        results=c.fetchall()
        # fit in first slot since that will be the smallest slot
        if results:
            row = results[0][0]
            pos = results[0][1]
            newWidth = round(results[0][2] - width,2)    # new width of item (round to 2 places)
            newPos = pos + width                # new pos of item
            if newWidth==0:
                deleteRowPos(conn,row,pos)
            else:

                # update table with new value
                updateQuery = ''' UPDATE {tn}
                              SET WIDTH = {new_width},
                                  START_POS = {new_pos}
                              WHERE ROW_NUM={row_num} AND START_POS={old_pos}
                          '''.format(tn='ROWS',new_width=newWidth,new_pos=newPos,row_num=row,
                                  old_pos=pos)
                c.execute(updateQuery)
                conn.commit()
            return row,pos
        else:
            return 'NaN','NaN'

# free up the row and pos taken up by a book
# 1) check for mergable values before the shelf
# 2) check for mergable values after the shelf
# 3) merge any values
# 4) otherwise just add it in 
def freeUpRowPos(conn, row, pos, width, height):
    #init starting values to save later
    save_pos = pos
    save_width = width
    end_location = pos + width
    # check if this space is free already
    search = ''' SELECT *
                 FROM {tn}
                 WHERE ROW_NUM = {rowid}
                    AND ((START_POS >= {pos} AND START_POS < {end_pos}) 
                    OR (START_POS < {pos} AND (START_POS+WIDTH) > {pos} ))
             '''.format(tn='ROWS',rowid=str(row),pos=str(pos),end_pos=str(end_location))
    c = conn.cursor()
    c.execute(search)
    results = c.fetchall()
    for item in results:
        print("Trying to free up row: {row}, pos: {pos}, width: {width} which is already free!"\
                .format(row=str(row),pos=str(pos),width=str(width)))
        for each in item:
            print (each)
        return

    # check for mergable values before the shelf
    # this means START_POS + WIDTH = pos ( or within a really close measurement)
    # account for ~.5 inches, will merge anything less than that
    presearch = ''' SELECT *
                    FROM {tn}
                    WHERE 
                    ROW_NUM = {rowid} AND {start_pos}-(START_POS+WIDTH)<{diff}
                    AND {start_pos} > START_POS
                '''.format(tn='ROWS',rowid=str(row),start_pos=str(pos),diff='0.5')
    c.execute(presearch)
    presults = c.fetchall()
    print("presults:")
    for item in presults:
        for each in item:
            print (each)
    if presults:    #merge with this
        save_pos = presults[0][1]  #take on preceding starting position
        save_width = round(end_location-save_pos,2)
        # delete this node
        deleteRowPos(conn, presults[0][0], presults[0][1] )

    # check for mergable values after the shelf
    # this means START_POS = pos+width ( or within a really close measurement)
    # account for ~.5 inches, will merge anything less than that
    postsearch = ''' SELECT *
                     FROM {tn}
                     WHERE ROW_NUM = {rowid}
                         AND (START_POS-{end})<{diff}
                         AND START_POS >= {end}
                '''.format(tn='ROWS',rowid=str(row),end=str(end_location),diff='0.5')
    c.execute(postsearch)
    postsults = c.fetchall()
    print("postsult:")
    for item in postsults:
        for each in item:
            print (each)
    if postsults: #merge with this
        save_width = postsults[0][1] + postsults[0][2] - save_pos   #add on extra fragment
        # delete this node
        deleteRowPos(conn, postsults[0][0], postsults[0][1] )

    # add this new node ( either merged or unmerged )
    add = ''' INSERT INTO {tn} (ROW_NUM,START_POS,WIDTH,HEIGHT)
              VALUES({row_id},{pos},{width},{height})
          '''.format(tn='ROWS',row_id=str(row),pos=str(save_pos),
                  width=str(save_width),height=str(height))
    conn.execute(add)
    conn.commit()
    print(add)

# delete 
def deleteRowPos(conn, row, start_pos):
    if conn:
        conn.execute(''' DELETE
                         FROM {tn}
                         WHERE ROW_NUM = {rowid}
                            AND START_POS = {pos}
                    '''.format(tn='ROWS',rowid=str(row),pos=str(start_pos)))
        conn.commit()

# BELOW FUNCTIONS ARE DEPRECATED
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
        print (all_rows)
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
    rowList = []
    rowList.append(
            {
                "Width":10.0,
                "Height":12.0,
                })
    rowList.append(
            {
                "Width":10.0,
                "Height":12.0,
                })
    rowList.append(
            {
                "Width":10.0,
                "Height":15.0,
                })
    initBookshelf(conn,rowList)
    width = 1
    height = 6.5
    # insertBook( conn, "12345678", "TestBook1", 1.25,12)
    # insertBook( conn, "87654321", "TestBook2", 2.6,14)
    insertBook( conn, "876543212", "TestBook3", 2.5,10)
    myList = returnAsDict( conn, 'ROWS' )
    for dictionary in myList:
        for key in dictionary:
            print (key, ' = ', dictionary[key])
    myList = returnAsDict( conn, 'BOOK' )
    for dictionary in myList:
        for key in dictionary:
            print (key, ' = ', dictionary[key])
