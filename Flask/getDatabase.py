from flask import Flask, jsonify
import bookDatabase

app = Flask(__name__)

app.route('/')
def getDatabase():
    conn = initDb()
    myList = returnAsDict( conn, 'BOOK' )
    return jsonify(myList)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    
