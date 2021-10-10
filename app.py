from typing import Tuple
from flask import Flask, render_template, redirect, request, sessions
from flask.ctx import after_this_request
from twilio.twiml.messaging_response import Body, Message, Redirect, MessagingResponse
import json
from decouple import config
from user_data import get_user
import asyncio

app = Flask(__name__)
app.secret_key = config('APP_SECRET')

@app.route('/')
def index():
    return render_template('home.html')

def write(data):
    session['Loaded'] = True
    with open("data.json", "w") as database:
        json.dump(data, database) 

def go():
    data = get_user(config('USER'), config('PASSWORD'))
    return  write(data)     

session = {'Login':False, 'State':0, 'Loaded':False}

@app.route( '/bot', methods=['POST']) 
def bot():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    responded = False

    # handling session 

    if session['Login']:
        if not session['Loaded']:
            if 'start' in incoming_msg:
                go()
                msg.body("*Loading data*\nthis may take some time. Please reply with *?* to know status of your information")
                responded = True
    
            elif '?' in incoming_msg:
                if session['Loaded']:
                    msg.body('your data sucessfully loaded. \nReply with following to get imformation\n*1.* *General*- general information \n*2* *User*- user info \n*3.* *Balance*- balance Inquiry \n*4.* *Logout*- to end your session.')
                    responded = True  
                else:
                    msg.body('still Loading!. Please wait for few seconds')
                    responded = True 
            elif 'logout' in incoming_msg:
                session['Login'] = False
                with open("data.json", "w") as database:
                    json.dump({}, database) 
                msg.body('session ended sucessfully! \n*Thank you*')
                responded = True
            else:
                msg.body('your session alredy started. \n type *?* to know more.')     
                responded = True
                
   
        if session['Loaded']:
            if 'general' in incoming_msg:
                val = ""
                with open("data.json", "r") as database:
                    json_object = json.load(database)
                    val = json_object["1"]
                msg.body(val)
                responded = True

            elif 'balance' in incoming_msg:
                val = ""
                with open("data.json", "r") as database:
                    json_object = json.load(database)
                    val = json_object["2"]
                msg.body(val)
                responded = True

            elif 'user' in incoming_msg:
                val = ""
                with open("data.json", "r") as database:
                    json_object = json.load(database)
                    val = json_object["3"]
                msg.body(val)
                responded = True
                
            elif 'logout' in incoming_msg:
                session['Login'] = False
                with open("data.json", "w") as database:
                    json.dump({}, database) 
                msg.body('session ended sucessfully! \n*Thank you*')
                responded = True


            else:
                msg.body('Type *?* to know your command \n Type *START* to get your details or to send refresh command')     
                responded = True
            if not responded:
                msg.body('an Error occured! again Type *START* to start bot')  
         
    
    else:
        if "yes" in incoming_msg:
            session['Login'] = True
            msg.body("your session began \ntype *START*- To getting your information") 
            responded = True
        else:
            msg.body('*your session is not initialised* \nfor developement purpose we stored your Auth Payloads \nIf you want to start your session reply with *YES*')
            responded = True             

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
