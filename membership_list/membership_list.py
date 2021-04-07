# Membership_list by Ivano


import os
import datetime
import json
import hashlib

from flask import Flask
from flask import request
from flask import render_template
from flask import session
from flask import redirect

from google.cloud import storage


def ivano_date(option, data=""):
    local_datenow = datetime.datetime.now()
    local_datenow = local_datenow + datetime.timedelta(hours=1)
    
    local_date = str(local_datenow).split(" ")[0]
    local_time = str(local_datenow).split(" ")[1]
    local_date = local_date.split("-")[2] + "/" + local_date.split("-")[1] + "/" + local_date.split("-")[0]
    local_time = local_time.split(":")[0] + ":" + local_time.split(":")[1]

    if option == "date":
        return local_date
    if option == "time":
        return local_time

    if option == "check":
        try:
            x = datetime.datetime.strptime(data, "%d/%m/%Y")
            return "valid"
        except:
            return "invalid"
        
    
    return local_datenow

class membership_list_presets():
    filler = ""

def membership_list_init():
#Initialise your value
    membership_list_presets.bucket = "ivanomembership.appspot.com"
    membership_list_presets.folder = "c:/membership_list_data/"
    membership_list_presets.folder_file = "ivano"
    membership_list_presets.users = "users"
    membership_list_presets.error_msg1 = ""
    membership_list_presets.error_msg2 = ""
    membership_list_presets.error_msg3 = ""
    membership_list_presets.date = ivano_date("date")
    membership_list_presets.time = ivano_date("time")
    membership_list_presets.screen = ""
    membership_list_presets.option = ""
    membership_list_presets.user_type = ""
    membership_list_presets.username = ""
    membership_list_presets.my_search_data = False
    membership_list_presets.url = request.url
    membership_list_presets.items = [
                                    "name",
                                    "surname",
                                    "other_name",
                                    "membership_no",
                                    "first_line_address",
                                    "second_line_address",
                                    "town",
                                    "county",
                                    "country",
                                    "postcode",
                                    "telephone_no",
                                    "mobile_no",
                                    "email",
                                    "data",
                                    "dob"
                                    ]

    agent = request.headers.get('User-Agent')

    if 'mobile' in agent.lower():
        membership_list_presets.device = "mobile"
    else:
        membership_list_presets.device = "desktop"
   # membership_list_presets.device = agent    
    
    if "username" in session:
        if session["username"] != "":
            membership_list_presets.username = session["username"]
            membership_list_presets.user_type = session["user_type"]
            membership_list_presets.my_items =  session["items"]
            if session.get("file_name"):
                membership_list_presets.folder_file = session["file_name"]
                if "my_search_data" in session:
                    if "membership_list" in membership_list_presets.url:
                        membership_list_presets.my_search_data = True
                    elif "membership_extract" in membership_list_presets.url:
                        membership_list_presets.my_search_data = True
                    else:
                        session.pop("my_search_data", None)
            else:
                session.pop("my_search_data", None)
    else:
        session["username"] = ""
    if request.method == "POST":
        membership_list_presets.msg_type = "POST"
        membership_list_presets.option = 1
        storage_client = storage.Client()
        bucket = storage_client.bucket(membership_list_presets.bucket)
        try:
            blob = bucket.get_blob(membership_list_presets.folder_file)
            my_data = json.loads(str(blob.download_as_string()).replace('b"', '').replace('"', '').replace("'", '"'))
            session["my_data"] = my_data
        except:
            my_data = []
            session["my_data"] = my_data 
    else:
        membership_list_presets.msg_type = "GET"

    if membership_list_presets.msg_type == "GET":
        membership_list_presets.option = request.args.get("option")
        if membership_list_presets.option == None:
            storage_client = storage.Client()
            bucket = storage_client.bucket(membership_list_presets.bucket)
            try:
                blob = bucket.get_blob(membership_list_presets.folder_file)
                my_data = json.loads(str(blob.download_as_string()).replace('b"', '').replace('"', '').replace("'", '"'))
                session["my_data"] = my_data
            except:
                my_data = []
                session["my_data"] = my_data
            
            membership_list_presets.option = 0
        else:
            membership_list_presets.option = int(membership_list_presets.option)
              
def login():
    session["username"] = ""
    session["file_name"] = ""
    session["user_type"] = ""
    session["items"] = ""
    session["screen"] = "login"
    membership_list_init()
    storage_client = storage.Client()
    bucket = storage_client.bucket(membership_list_presets.bucket)
    try:
        blob = bucket.get_blob(membership_list_presets.users)
        my_users = json.loads(str(blob.download_as_string()).replace('b"', '').replace('"', '').replace("'", '"'))
    except:
        my_users = []

    if membership_list_presets.msg_type == "GET":
        return render_template("membership_login.html",
                               my_line = "",
                               membership_list_presets = membership_list_presets,
                               )
    if membership_list_presets.msg_type == "POST":
        local_login = False
        local_username = request.values.get("username").lower()
        local_password = request.values.get("password")
        if my_users == []:
            if local_username == "admin":
                if local_password == "password":
                    local_login = True
                    session["user_type"] = "sys_admin"
                    session["username"] = "admin"
        else:
            local_password = hashlib.sha512(local_password.encode()).hexdigest()
            for my_user in my_users:
                if my_user["username"] == local_username:
                    if my_user["password"] == local_password:
                        local_login = True
                        session["username"] = local_username
                        session["user_type"] = my_user["user_type"]
                        session["file_name"] = my_user["file_name"]
                        if "items" in my_user:
                            session["items"] = my_user["items"]
                        else:
                            session["items"] = []
                        
        if local_login == False:
            membership_list_presets.error_msg1 = "Invalid Username or Password"
            return render_template("membership_login.html",
                                   my_line = {'username':local_username},
                                   membership_list_presets = membership_list_presets,
                                   )
        if session["user_type"] == "sys_admin":
            return redirect("/membership_users")
        
        return redirect("/membership_list")
    
def users():
    membership_list_init()
    if session["username"] == "":
        return redirect("/membership_login")
    if session["user_type"] not in ["admin","sys_admin"]:
        return redirect("/membership_login")
    session["screen"] = "users"

    storage_client = storage.Client()
    bucket = storage_client.bucket(membership_list_presets.bucket)
    try:
        blob = bucket.get_blob(membership_list_presets.users)
        my_users = json.loads(str(blob.download_as_string()).replace('b"', '').replace('"', '').replace("'", '"'))
    except:
        my_users = []
    
    #edit existing users
    session["my_user"] = my_users

    if membership_list_presets.option == 2:
        local_key = request.args.get("key")
        count = 0
        number_to_edit = -1
        for my_user in my_users:
            if my_user["key"] == local_key:
                number_to_edit = count
            count+=1
        if number_to_edit != -1:
            my_user = my_users[number_to_edit]
            return render_template("membership_users.html",
                                   my_users = my_users,
                                   my_user = my_user,
                                   membership_list_presets = membership_list_presets,
                                   )
            
    #delete existing users
    if membership_list_presets.msg_type == "GET":
        if membership_list_presets.option == 3:
            local_key = request.args.get("key")
            count = 0
            number_to_delete = -1
            for my_user in my_users:
                if my_user["key"] == local_key:
                    if my_user["username"] != session["username"]:
                        number_to_delete = count
                    else:
                        membership_list_presets.error_msg1 = "You cannot delete yourself"
                count+=1           

            if number_to_delete != -1:
                del my_users[number_to_delete]
                storage_client = storage.Client()
                bucket = storage_client.bucket(membership_list_presets.bucket)
                blob = bucket.blob(membership_list_presets.users)
                blob.upload_from_string(str(my_users))

        
        #sort users section by username or by user type
        if membership_list_presets.option == 4:
            local_sort = request.args.get("sort")
            my_users = sorted(my_users, key = lambda i:(i[local_sort]))
            storage_client = storage.Client()
            bucket = storage_client.bucket(membership_list_presets.bucket)
            blob = bucket.blob(membership_list_presets.users)
            blob.upload_from_string(str(my_users))
     
        return render_template("membership_users.html",
                               my_line = "",
                               my_users = my_users,
                               membership_list_presets = membership_list_presets,
                               )
    
    if membership_list_presets.msg_type == "POST":
        local_key = request.values.get("key")
        local_username = request.values.get("username").lower()
        local_password = request.values.get("password")
        if local_key == "":
            local_password = hashlib.sha512(local_password.encode()).hexdigest()
        else:
            if local_password != "":
                local_password = hashlib.sha512(local_password.encode()).hexdigest()
        if session["user_type"] == 'admin':
            local_file_name = membership_list_presets.folder_file
        else:
            local_file_name = local_username.replace(".", "").replace("@", "")
        local_user_type = request.values.get("user_type")
        local_date = ivano_date("date")
        if local_key == "":
            for my_user in my_users:
                if my_user["username"] == local_username:
                    membership_list_presets.error_msg1 = "User already exists"
        if membership_list_presets.error_msg1 != "":
            return render_template("membership_users.html",
                                   my_line = "",
                                   my_users = my_users,
                                   membership_list_presets = membership_list_presets,
                                   )
        if local_key != "":
            count = 0
            number_to_delete = -1
            for my_user in my_users:
                if my_user["key"] == local_key:
                    if local_password == "":
                        local_password = my_user["password"]
                    number_to_delete = count
                count+=1           
            if number_to_delete != -1:
                my_user = my_users[number_to_delete]
                del my_users[number_to_delete]
            my_user["password"] = local_password
            my_user["user_type"] = local_user_type
        else:
            local_key = str(datetime.datetime.now()).replace("-" , "").replace(" " , "").replace("." , "").replace(":" , "")
            my_user = {"username" : local_username,
                       "password" : local_password,
                       "user_type" : local_user_type,
                       "file_name" : local_file_name,
                       "key" : local_key,
                       "date" : local_date
                       }
        my_users.append(my_user)

        storage_client = storage.Client()
        bucket = storage_client.bucket(membership_list_presets.bucket)
        blob = bucket.blob(membership_list_presets.users)
        blob.upload_from_string(str(my_users))

        return render_template("membership_users.html",
                               my_line = "",
                               my_users = my_users,
                               membership_list_presets = membership_list_presets,
                               )

                
def home():
    membership_list_init()
    if session["username"] == "":
        return redirect("/membership_login")
    if "membership_list" in membership_list_presets.url:
        if "sort" not in membership_list_presets.url:
            session["screen"] = "list"
    my_data = session["my_data"]
    if membership_list_presets.option == 4:
        if membership_list_presets.my_search_data == True:
            my_data = session["my_search_data"]
            local_sort = request.args.get("sort")
            my_data = sorted(my_data, key = lambda i:(i[local_sort]))
        else:
            local_sort = request.args.get("sort")
            my_data = sorted(my_data, key = lambda i:(i[local_sort]))
            storage_client = storage.Client()
            bucket = storage_client.bucket(membership_list_presets.bucket)
            blob = bucket.blob(membership_list_presets.folder_file)
            blob.upload_from_string(str(my_data))

    if session["screen"] == "extract":
        local_template = "membership_extract.html"
    else:
        local_template = "membership_list.html"
    return render_template(local_template,
                           my_data = my_data,
                           membership_list_presets = membership_list_presets,
                           )

def register():
    membership_list_init()
    if session["username"] == "":
        return redirect("/membership_login")
    session["screen"] = "register"
    my_data = session["my_data"]

    if membership_list_presets.option == 0:
        return render_template("membership_input.html",
                               my_data = my_data,
                               membership_list_presets = membership_list_presets,
                               )

    if membership_list_presets.option == 1:
        local_edit = request.values.get("key")
        local_name = request.values.get("name")
        local_name1 = local_name.title().replace("'","").replace('.',"").replace(" ","")
        local_surname = request.values.get("surname")
        local_surname1 = local_surname.title().replace("'","").replace('.',"").replace(" ","")
        local_other_name = request.values.get("other_name")
        local_membership_no = request.values.get("membership_no")
        local_first_line_address = request.values.get("first_line_address")
        local_second_line_address = request.values.get("second_line_address")
        local_town = request.values.get("town")
        local_town1 = local_town.title().replace("'","").replace(" ","")
        local_county = request.values.get("county")
        local_county1 = local_county.title().replace("'","").replace(" ","")
        local_country = request.values.get("country")
        local_country1 = local_country.title().replace("'","").replace(" ","")
        local_postcode = request.values.get("postcode").title().replace(" ","")
        local_telephone_no= request.values.get("telephone_no")
        local_mobile_no = request.values.get("mobile_no")
        local_email = str(request.values.get("email")).lower()
        local_data = ivano_date("date")
        local_dob = request.values.get("dob")
        local_key = request.values.get("key")

        my_input_data = {"name":local_name,
                        "surname":local_surname,
                        "other_name":local_other_name,
                        "membership_no":local_membership_no,
                        "first_line_address":local_first_line_address,
                        "second_line_address":local_second_line_address,
                        "town":local_town,
                        "county":local_county,
                        "country":local_country,
                        "postcode":local_postcode,
                        "telephone_no":local_telephone_no,
                        "mobile_no":local_mobile_no,
                        "email":local_email,
                        "data":local_data,
                        "dob":local_dob,
                        "key":local_key,
                        }

        if local_name1.isalpha() != True:
            membership_list_presets.error_msg1 += " Invalid Name : all the characters must be alphabetic characters only (a-z). , "

        if local_surname1.isalpha() != True:
            membership_list_presets.error_msg1 += " Invalid Surname : all the characters must be alphabetic characters only (a-z). , "

        if local_town1.isalpha() != True:
            membership_list_presets.error_msg1 += " Invalid Town : all the characters must be alphabetic characters only (a-z). , "

        if local_county1.isalpha() != True:
            membership_list_presets.error_msg1 += " Invalid County : all the characters must be alphabetic characters only (a-z). , "

        if local_country1.isalpha() != True:
            membership_list_presets.error_msg1 += " Invalid Country : all the characters must be alphabetic characters only (a-z). , "

        if local_telephone_no != "":
            if local_telephone_no.replace(" " , "").replace("+" , "").replace("-" , "").isdigit() == False:
                membership_list_presets.error_msg1 += " Invalid Telephone No. : must be numeric , "

        if local_mobile_no != "":
            if local_mobile_no.replace(" " , "").replace("+" , "").replace("-" , "").isdigit() == False:
                membership_list_presets.error_msg1 += " Invalid Mobile No. : must be numeric , "

        if local_dob != "":
            if local_dob.replace(" " , "").replace("/" , "").replace("-" , "").replace("." , "").isdigit() == False:
                membership_list_presets.error_msg1 += " Invalid Date of birth : must be numeric , "
            else:
                if ivano_date("check", local_dob) == "invalid":
                    membership_list_presets.error_msg1 += " Invalid Date of birth : must be dd/mm/yyyy , "

                    
        if local_edit == "":
            for my_line in my_data:
                if local_membership_no == my_line["membership_no"]:
                    membership_list_presets.error_msg1 += " Invalid Membership No. : already in use , "
                if local_email == my_line["email"]:
                    membership_list_presets.error_msg1 += " Invalid E-mail : already in use , "

        if local_edit !=  "":
            count = 0
            number_to_delete = -1

            for my_line in my_data:
                if my_line["key"] == local_edit:
                    number_to_delete = count
                count+=1 

            if number_to_delete != -1:
                if my_data[number_to_delete]["membership_no"] != local_membership_no:
                    local_membership_no = my_data[number_to_delete]["membership_no"]
                    my_input_data["membership_no"] = local_membership_no
                    membership_list_presets.error_msg1 += " Invalid Membership No. : cannot be changed , "
                    


        if membership_list_presets.error_msg1 != "":
            return render_template("membership_input.html",    
                                   my_data = my_data,
                                   my_line = my_input_data,
                                   membership_list_presets = membership_list_presets,
                                   )
        if local_edit != "":
            if number_to_delete != -1:
                del my_data[number_to_delete]

        local_key = str(datetime.datetime.now()).replace("-" , "").replace(" " , "").replace("." , "").replace(":" , "")
        my_data.append({"name":local_name ,
                        "surname":local_surname ,
                        "other_name":local_other_name,
                        "membership_no":local_membership_no,
                        "first_line_address":local_first_line_address,
                        "second_line_address":local_second_line_address,
                        "town":local_town,
                        "county":local_county,
                        "country":local_country,
                        "postcode":local_postcode,
                        "telephone_no":local_telephone_no,
                        "mobile_no":local_mobile_no,
                        "email":local_email,
                        "data":local_data,
                        "dob":local_dob,
                        "key":local_key
                        })
        session["my_data"] = my_data

    if membership_list_presets.option == 2:
        local_key = request.args.get("key")
        count = 0
        number_to_edit = -1
        for my_line in my_data:
            if my_line["key"] == local_key:
                number_to_edit = count
            count+=1
        if number_to_edit != -1:
            my_line = my_data[number_to_edit]
            return render_template("membership_input.html",
                                   my_data = my_data,
                                   my_line = my_line,
                                   membership_list_presets = membership_list_presets,
                                   )       

    if membership_list_presets.option == 3:
        local_key = request.args.get("key")
        count = 0
        number_to_delete = -1
        for my_line in my_data:
            if my_line["key"] == local_key:
                number_to_delete = count
            count+=1 
        if number_to_delete != -1:
            del my_data[number_to_delete]
            session["my_data"] = my_data

    if membership_list_presets.option == 5:
        local_key = request.args.get("key")
        count = 0
        number_to_edit = -1
        for my_line in my_data:
            if my_line["key"] == local_key:
                number_to_edit = count
            count+=1
        if number_to_edit != -1:
            my_line = my_data[number_to_edit]
            my_line["key"] = ""
            return render_template("membership_input.html",
                                   my_data = my_data,
                                   my_line = my_line,
                                   membership_list_presets = membership_list_presets,
                                   )    
    storage_client = storage.Client()
    bucket = storage_client.bucket(membership_list_presets.bucket)
    blob = bucket.blob(membership_list_presets.folder_file)
    blob.upload_from_string(str(my_data))
    return redirect("/membership_list?option=0")
    
def search():
    membership_list_init()
    if session["username"] == "":
        return redirect("/membership_login")
    my_data = session["my_data"]

    local_search = str(request.values.get("search")).lower()

    my_search_data = []
    for my_line in my_data:
        local_include = 0
        if local_search in my_line["name"].lower():
            local_include = 1
        if local_search in my_line["surname"].lower():
            local_include = 1
        if local_search in my_line["other_name"].lower():
            local_include = 1
        if local_search in my_line["membership_no"].lower():
            local_include = 1
        if local_search in my_line["first_line_address"].lower():
            local_include = 1
        if local_search in my_line["second_line_address"].lower():
            local_include = 1
        if local_search in my_line["town"].lower():
            local_include = 1
        if local_search in my_line["county"].lower():
            local_include = 1
        if local_search in my_line["country"].lower():
            local_include = 1
        if local_search in my_line["postcode"].lower():
            local_include = 1
        if local_search in my_line["telephone_no"].lower():
            local_include = 1
        if local_search in my_line["mobile_no"].lower():
            local_include = 1
        if local_search in my_line["email"].lower():
            local_include = 1
        if local_search in my_line["dob"].lower():
            local_include = 1
        if local_include == 1:
            my_search_data.append(my_line)

    
    local_template = "membership_list.html"
    if session["screen"] == "extract":
        local_template = "membership_extract.html"

    session["my_search_data"] = my_search_data
    return render_template(local_template,
                           my_data = my_search_data,
                           membership_list_presets = membership_list_presets,
                           )


def extract():
    membership_list_init()
    if session["username"] == "":
        return redirect("/membership_login")
    session["screen"] = "extract"
    my_data = session["my_data"]

    return render_template("membership_extract.html",
                           my_data = my_data,
                           membership_list_presets = membership_list_presets,
                           )


def my_user():
    membership_list_init()
    if session["username"] == "":
        return redirect("/membership_login")
    session["screen"] = "my_user"
    storage_client = storage.Client()
    bucket = storage_client.bucket(membership_list_presets.bucket)
    blob = bucket.get_blob(membership_list_presets.users)
    my_user = json.loads(str(blob.download_as_string()).replace('b"', '').replace('"', '').replace("'", '"'))
    
    for my_user_search in my_user:
        if my_user_search["username"] == session["username"]:
            my_user = my_user_search
            
    if membership_list_presets.msg_type == "POST":
        local_key = request.values.get("key")
        local_current_password = request.values.get("current_password")
        local_new_password = request.values.get("new_password")
        local_confirm_password = request.values.get("confirm_password")
        if local_current_password != "":
            local_current_password = hashlib.sha512(local_current_password.encode()).hexdigest()
            if local_current_password != my_user["password"]:
                membership_list_presets.error_msg1 = "- Invalid Cureent Password "
        if local_new_password != "":
            if local_current_password == "":
                membership_list_presets.error_msg1 = membership_list_presets.error_msg1 + "- To change Password, Current Password is required "
        if local_new_password != local_confirm_password:
            membership_list_presets.error_msg1 = membership_list_presets.error_msg1 + "- The New Password and Confirm Password are not the same " 
        local_date = ivano_date("date")

        my_items = []
        for item in membership_list_presets.items:
            if request.values.get(item) == "on":
                my_items.append(item)
        my_user["items"] = my_items
        session["items"] = my_user["items"]
        
        if membership_list_presets.error_msg1 == "":
            if local_new_password != "":
                local_new_password = hashlib.sha512(local_new_password.encode()).hexdigest()
                my_user["password"] = local_new_password
            storage_client = storage.Client()
            bucket = storage_client.bucket(membership_list_presets.bucket)
            blob = bucket.get_blob(membership_list_presets.users)
            my_users = json.loads(str(blob.download_as_string()).replace('b"', '').replace('"', '').replace("'", '"'))
        
            count = 0
            for my_user_search in my_users:
                if my_user_search["username"] == session["username"]:
                    number_to_delete = count
                count += 1

            del my_users[number_to_delete]
            my_users.append(my_user)
            storage_client = storage.Client()
            bucket = storage_client.bucket(membership_list_presets.bucket)
            blob = bucket.blob(membership_list_presets.users)
            blob.upload_from_string(str(my_users))

            
    local_my_items = []
    if "items" in my_user:
        local_my_items = my_user["items"]
    return render_template("membership_my_user.html",
                           my_user = my_user,
                           my_items = local_my_items,
                           membership_list_presets = membership_list_presets
                           )

