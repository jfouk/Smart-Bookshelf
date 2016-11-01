import cameraIsbn
import getProductDimensions
import bookDatabase

def main():
    #set up database
    conn = bookDatabase.initDb()
    #isbn = cameraIsbn.scanForIsbn()
    #print isbn
    isbn = 1
    if isbn:
        #title, width = getProductDimensions.getBookInfo(isbn)
        title, width = getProductDimensions.getBookInfo(('0545010225','0545010225'))
        if title and width is not 'NaN':
            print title, width
            print "Check if book was checked out.."
            if (




if __name__ == "__main__":
    main()
