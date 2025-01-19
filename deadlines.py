from flask import render_template, request, redirect, url_for
from flask_mail import Message
from twilio.rest import Client
from my_app import app, mail, Client  


client = Client("your_account_sid", "your_auth_token")


account_sid = 'ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'  # ??????????????
auth_token = 'your_auth_token'                      # ??????????????


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']        # მომხმარებლის იმეილი
    phone = request.form['phone']        # მომხმარებლის ტელეფონის ნომერი
    deadline = request.form['deadline']  # პროექტის დედლაინი

    # იმეილზე შეტყობინების გაგზავნა
    msg = Message('პროექტის დედლაინი', sender='your-email@gmail.com', recipients=[email])
    msg.body = f'თქვენ მიერ შერჩეული პროექტის დედლაინი მოახლოვდა. გთხოვთ გაითვალისწინოთ, რომ პროექტზე რეგისტრაცია სრულდება: {deadline}.'
    mail.send(msg)

    # SMS შეტყობინების გაგზავნა
    message = client.messages.create(
        body=f"თქვენ მიერ შერჩეული პროექტის დედლაინი მოახლოვდა. გთხოვთ გაითვალისწინოთ, რომ პროექტზე რეგისტრაცია სრულდება: {deadline}.", 
        from_=app.config['TWILIO_PHONE_NUMBER'],  
        to=phone
    )

    return redirect(url_for('success'))  

@app.route('/success')
def success():
    return "შეტყობინება წარმატებით გაიგზავნა!"  



    
