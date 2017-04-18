from flask import Flask, jsonify, request
import bookDatabase
import json

app = Flask(__name__)

@app.route('/')
def getDatabase():
    conn = bookDatabase.initDb()
    myList = bookDatabase.returnAsDict( conn, 'BOOK' )
    return jsonify(myList)

@app.route('/delete',methods = ['POST','GET'])
def delete():
    content = request.form['ISBN']
    print "Received delete request.."
    print "Deleting book: " + content
#    return jsonify(result=str(1))
    conn = bookDatabase.initDb()
    rc = bookDatabase.deleteBook(conn, content)
    return jsonify(result=str(rc))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    
