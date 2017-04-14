from flask import Flask, jsonify, request
import bookDatabase

app = Flask(__name__)

@app.route('/')
def getDatabase():
    conn = bookDatabase.initDb()
    myList = bookDatabase.returnAsDict( conn, 'BOOK' )
    return jsonify(myList)

@app.route('/delete',methods = ['POST','GET'])
def delete():
    content = request.get_json
    print "Received delete request.."
    print content
    return jsonify(result=str(1))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    
