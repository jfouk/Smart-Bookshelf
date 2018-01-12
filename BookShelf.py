#!/usr/bin/python
import cameraIsbn
import getProductDimensions
import bookDatabase
from led_control import BookShelfLight

# the main bookshelf class
# Consider this the glue that holds the lights and database together
#   @TODO need a state mgr, in flask, return back what next step is
# Member Data:
#   BookShelfLight - class to control bookshelf leds, contains information about bookshelf
#   database connection - connection to bookshelf database
class BookShelf:
    #STATES
    READY="READY"
    CAMERA_SCANNED="CAMERA_SCANNED"
    PRODUCT_INFO="PRODUCT_INFO"
    WAIT_FOR_CONFIRM="WAIT_FOR_CONFIRM"

    def __init__(self,staticfile):
        self.mBLight = BookShelfLight.BookShelfLight(staticfile)
        self.mDb = bookDatabase.initDb()
        self.mState = self.READY
        self.mISBN = 0
    
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
            if title != 'NaN' and width != 'NaN' and height != 'NaN':
                isbn = isbn[0] #isbn comes in a list from camera stream
                print ("Checking in " + title + "!\n" )
                row, pos, width= bookDatabase.insertBook(self.mDb,isbn,title,width,height,
                        author, picture_url)
                if row != 'NaN' and pos != 'NaN' and width != 'NaN':
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

    # scan camera to find isbn
    def scanCamera(self):
        self.mState = self.CAMERA_SCANNED
        isbn = cameraIsbn.scanForIsbn()
        if isbn:
            self.mISBN = isbn;
        else:
            self.mState = self.READY
            return False
        # return and wait for confirmation
        return True

    def getProductInfo(self):
        if self.mISBN:
            title, width, height, author, picture_url = getProductDimensions.getBookInfo(self.mISBN)
            if title != 'NaN' and width != 'NaN' and height != 'NaN':
                self.mISBN = self.mISBN[0] #isbn comes in a list from camera stream
                print ("Checking in " + title + "!\n" )
                row, pos, width= bookDatabase.insertBook(self.mDb,self.mISBN,title,width,height,
                        author, picture_url)
                if row != 'NaN' and pos != 'NaN' and width != 'NaN':
                    self.mState = self.WAIT_FOR_CONFIRM
                    return self.mBLight.lightShelf(row,pos,width)
                else:
                    print ("Unable to fit " + title + " on the bookshelf!\n")
                    self.mState = self.READY
                    return False

            else:
                print("Unable to get product dimensions for " + self.mISBN[0] + "!\n")
                self.mState = self.READY
                return False

    # book is placed, so we don't need the leds anymore
    def confirmBookPlaced(self):
        self.mBLight.turnOffLeds()
        self.mState = self.READY
        return True


    # action confirmed by app, move on to next state
    def confirm(self):
        if self.mState == self.CAMERA_SCANNED:
            rc = self.getProductInfo()
        elif self.mState == self.WAIT_FOR_CONFIRM:
            rc = self.confirmBookPlaced()
        return rc

    # checkout book, updating DB and illuminating bookshelf
    # inputs 
    #       isbn number
    def checkOut(self, isbn):
        row, pos, width = bookDatabase.checkOutBook(self.mDb, isbn)
        # check if valid TODO: maybe flash lights if invalid
        if row != 'NaN':
            self.mState = self.WAIT_FOR_CONFIRM
            return self.mBLight.lightShelf(row,pos,width)
        else:
            self.mState = self.READY
            return False

    # checkin book
    # - call checkBook to checkin book
    # - illuminate where to place the book
    def checkIn(self, isbn):
        print("Starting checkin process\n");
        rc, row, pos,width = bookDatabase.checkBook(self.mDb, isbn)
        if rc is 1: #if success
            self.mState = self.WAIT_FOR_CONFIRM
            return self.mBLight.lightShelf(row,pos,width)
        else:
            self.mState = self.READY
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
    #bShelf.checkOut('1416915281')
    #bShelf.checkIn('1416915281')
    bShelf.testAddBook( ('1423124545',) )
    myList = bShelf.getShelfDict()
    for dictionary in myList:
        for key in dictionary:
            print (key, ' = ', dictionary[key])
