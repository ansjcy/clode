from app import app

@app.route('/query', method='POST')
def query():
    return 'Hello world ~~~~~~'