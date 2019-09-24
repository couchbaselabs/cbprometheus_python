from application import application

if (__name__=='__main__') or (__name__=='__run__') or (__name__=='run'):
    application.run(host='0.0.0.0', port=5000, debug=True)
