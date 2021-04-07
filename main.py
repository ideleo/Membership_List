from flask import Flask

from membership_list import membership_list

app = Flask(__name__)
app.secret_key = "keyboard"

@app.route("/membership_login" , methods = ['GET', 'POST'])
def membership_list_login():
    return membership_list.login()

@app.route("/membership_users" , methods = ['GET', 'POST'])
def membership_users():
    return membership_list.users()

@app.route("/" , methods = ['GET', 'POST'])
def membership_list_home():
    return membership_list.home()
    
@app.route("/membership_list" , methods = ['GET', 'POST'])
def membership_list_list():
    return membership_list.home()
        
@app.route("/membership_input" , methods = ['GET', 'POST'])
def membership_input():
    return membership_list.register()

@app.route("/membership_search" , methods = ['GET', 'POST'])
def membership_search():
    return membership_list.search()

@app.route("/membership_extract" , methods = ['GET', 'POST'])
def membership_extract():
    return membership_list.extract()

@app.route("/membership_my_user" , methods = ['GET', 'POST'])
def membership_my_user():
    return membership_list.my_user()

#if __name__ == "__main__":
 #   app.run()

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]

