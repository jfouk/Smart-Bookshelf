from flask import Flask, jsonify, request
import bookDatabase
import json
import BookShelf

app = Flask(__name__)

bShelf = BookShelf.BookShelf('bookshelf_config.txt')

@app.route('/init',methods = ['POST','GET'])
def init():
    ledWidth = request.form['ledWidth']
    offset = request.form['offset']
    rows = request.form['rows']
    numLeds = request.form['numLeds']
    rowList = []
    for i in range(0,int(rows)):
        rowList.append(
                {
                    "Width":request.form['width'+i],
                    "Height":request.form['height'+i]
                    })
    print "Received init request.."
    msg = '''Initializing bookshelf...
             ledWidth={lw}, offset={of}, rows={r}, numLeds={nl}
        '''.format(lw=ledWidth,of=offset,r=rows,nl=numLeds)
    print ( msg )
    for rows in rowList:
        for key in rows:
            print(key,' = ',rows[key])

    rc = 0
    if bShelf.init(ledWidth,offset,rows,numLeds,rowList):
        rc = 1  #Android app takes 1 as true
    else:
        rc = 0  #Android app takes 0 as False
    return jsonify(result=str(rc))

@app.route('/')
def getDatabase():
    myList = bShelf.getShelfDict()
    return jsonify(myList)

# add a new book to the bookshelf
@app.route('/add')
def addBook():
    rc = bShelf.addBook()
    if rc:
        myList = bShelf.getShelfDict()
        responseCode = 200
    else:   #return -1 value if failed
        myList = {
                "ISBN": -1,
                }
        responseCode = 201
    return jsonify(myList), responseCode

@app.route('/delete',methods = ['POST','GET'])
def delete():
    content = request.form['ISBN']
    print "Received delete request.."
    print "Deleting book: " + content
#    return jsonify(result=str(1))
    conn = bookDatabase.initDb()
    rc = bookDatabase.deleteBook(conn, content)
    return jsonify(result=str(rc))

@app.route('/checkout',methods = ['POST','GET'])
def checkout():
    content = request.form['ISBN']
    print "Received checkout request.."
    print "Checking out book: " + content
#    return jsonify(result=str(1))
    # conn = bookDatabase.initDb()
    # rc = bookDatabase.checkOutBook(conn, content)
    rc = bShelf.checkOut(content)
    if rc:
        rc = 1  #Android app takes 1 as true
    else:
        rc = 0  #Android app takes 0 as False
    return jsonify(result=str(rc))

@app.route('/checkin',methods = ['POST','GET'])
def checkin():
    content = request.form['ISBN']
    print "Received checkin request.."
    print "Checking in book: " + content
#    return jsonify(result=str(1))
    # conn = bookDatabase.initDb()
    # rc = bookDatabase.checkOutBook(conn, content)
    rc = bShelf.checkIn(content)
    if rc:
        rc = 1  #Android app takes 1 as true
    else:
        rc = 0  #Android app takes 0 as False
    return jsonify(result=str(rc))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    
