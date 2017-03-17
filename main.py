import cameraIsbn
import getProductDimensions
import bookDatabase

def main():
    #set up database
    conn = bookDatabase.initDb()
    #isbn = cameraIsbn.scanForIsbn()
    #print isbn
    isbn = ('0545010225','0545010225')
    if isbn:
        #title, width = getProductDimensions.getBookInfo(isbn)
        title, width = getProductDimensions.getBookInfo(('0545010225','0545010225'))
        isbn = isbn[0]
        if title and width is not 'NaN':
            print title, width
            print "Check if book was checked out.."
            rc, row, position = checkBook( conn, isbn )
            if rc:
                print "check book back in.."


def test():
    conn = bookDatabase.initDb()
    isbn = ('0545010225','0545010225')
    title, width = getProductDimensions.getBookInfo(isbn)
    isbn = isbn[0]
    if title and width is not 'NaN':
        print title, width
        bookDatabase.insertBook( conn, isbn, title, float(width))

    myList = bookDatabase.returnAsDict( conn, 'BOOK' )
    for dictionary in myList:
        for key in dictionary:
            print key, ' = ', dictionary[key]


if __name__ == "__main__":
    test()
