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




if __name__ == "__main__":
    main()
