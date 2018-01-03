#!/usr/bin/python
import cameraIsbn
import getProductDimensions
import bookDatabase
from led_control import BookShelfLight

# the main bookshelf class
# Consider this the glue that holds the lights and database together
#
# Member Data:
#   BookShelfLight - class to control bookshelf leds, contains information about bookshelf
#   database connection - connection to bookshelf database
class BookShelf:
    def __init__(self,staticfile):
        self.mBLight = BookShelfLight.BookShelfLight(staticfile)
        self.mDb = bookDatabase.initDb()

    # init bookshelf
    # set values that we need to know such as ledWidth
    def init(self,ledWidth,offset,rows,numLeds, rowList = []):
        self.mBLight.initValues(ledWidth,offset,rows,numLeds)
        return bookDatabase.initBookshelf(self.mDb, rowList )

    # returns a dictionary of the books to pass onto flask
    def getShelfDict(self):
        return bookDatabase.returnAsDict( self.mDb, 'BOOK')

    # add a new book to the shelf
    # - Invokes camera to get the ISBN
    # - Searches on Amazon for product dimensions
    # - adds it to database
    # - Illuminates where to put it on the shelf
    def addBook(self):
        isbn = cameraIsbn.scanForIsbn()
        # if we get an isbn
        if isbn:
            title, width, height, author, picture_url = getProductDimensions.getBookInfo(isbn)
            if title is not 'NaN' and width is not 'NaN' and height is not 'NaN':
                isbn = isbn[0] #isbn comes in a list from camera stream
                print ("Checking in " + title + "!\n" )
                row, pos, width= bookDatabase.insertBook(self.mDb,isbn,title,width,height,
                        author, picture_url)
                if row is not 'NaN' and pos is not 'NaN' and width is not 'NaN':
                    return self.mBLight.lightShelf(row,pos,width)
                else:
                    print ("Unable to fit " + title + " on the bookshelf!\n")
                    return False

            else:
                print("Unable to get product dimensions for " + isbn[0] + "!\n")
                return False
        else:
            # maybe loop again and try again
            return False

    # checkout book, updating DB and illuminating bookshelf
    # inputs 
    #       isbn number
    def checkOut(self, isbn):
        row, pos, width = bookDatabase.checkOutBook(self.mDb, isbn)
        # check if valid TODO: maybe flash lights if invalid
        if row is not 'NaN':
            return self.mBLight.lightShelf(row,pos,width)
        else:
            return False

    # checkin book
    # - call checkBook to checkin book
    # - illuminate where to place the book
    def checkIn(self, isbn):
        print("Starting checkin process\n");
        rc, row, pos,width = bookDatabase.checkBook(self.mDb, isbn)
        if rc is 1: #if success
            return self.mBLight.lightShelf(row,pos,width)
        else:
            return False

    # testing function, no camera, no lights
    def testAddBook( self,isbn ):
        title, width, height, author, picture_url = getProductDimensions.getBookInfo(isbn)
        if title is not 'NaN' and width is not 'NaN' and height is not 'NaN':
            isbn = isbn[0] #isbn comes in a list from camera stream
            print ("Checking in " + title + "!\n" )
            row, pos, width= bookDatabase.insertBook(self.mDb,isbn,title,width,height,
                    author, picture_url)
            if row is not 'NaN' and pos is not 'NaN' and width is not 'NaN':
                return True
            else:
                print ("Unable to fit " + title + " on the bookshelf!\n")
                return False

        else:
            print("Unable to get product dimensions for " + isbn[0] + "!\n")
            return False

if __name__ == "__main__":
    bShelf = BookShelf("bookshelf_config.txt")
    rowList = []
    rowList.append(
            {
                "Width":14.5,
                "Height":12.0,
                })
    rowList.append(
            {
                "Width":14.5,
                "Height":12.0,
                })
    rowList.append(
            {
                "Width":14.5,
                "Height":15.0,
                })
    #bShelf.init(1.25,0,3,18,rowList)
    #bShelf.testAddBook( ('1416915281',) )
    bShelf.checkOut('1416915281')
    bShelf.checkIn('1416915281')
    myList = bShelf.getShelfDict()
    for dictionary in myList:
        for key in dictionary:
            print (key, ' = ', dictionary[key])
