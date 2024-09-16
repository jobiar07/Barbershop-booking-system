import sqlite3, smtplib, ssl, random,datetime
from datetime import date

#SQL library to communicate with database
#Email library required to send emails
#Random library for authentication code
#Date library for getting current date

con=sqlite3.connect("Barbershop database.db")
#this creates the database file

cur=con.cursor()

def create_database():
    cur.execute("""CREATE TABLE "user_table" (
           "username"	TEXT NOT NULL UNIQUE,
            "password"	TEXT NOT NULL,
            "phone_number"	TEXT NOT NULL,
            "email"	TEXT NOT NULL,
            "is_employee"	INTEGER NOT NULL,
            PRIMARY KEY("username")
    )""")
    #creates the user_table with all its fields
    
    cur.execute("""CREATE TABLE "hairstyle_table" (
            "hair_ID"   INTEGER NOT NULL UNIQUE,
            "hairstyle"	TEXT NOT NULL,
            "price"	REAL NOT NULL,
            "face_shape"	TEXT NOT NULL,
            "face_width"	TEXT NOT NULL,
            "maintainence"	TEXT NOT NULL,
            "hair_length"	TEXT NOT NULL,
            PRIMARY KEY("hair_ID" AUTOINCREMENT)
    )""")
    #creates the hairstyle_table with all its field
        
    cur.execute("""CREATE TABLE "reservation_table" (
            "reservationID"	INTEGER NOT NULL UNIQUE,
            "barber_name"	TEXT NOT NULL,
            "reservation_time"	REAL NOT NULL,
            "reservation_date"	DATE NOT NULL,
            "hairstyle"	TEXT NOT NULL,
            "username"	TEXT NOT NULL,
            "message"   TEXT,
            PRIMARY KEY("reservationID" AUTOINCREMENT)
            FOREIGN KEY ("username") REFERENCES user_table,
            FOREIGN KEY ("hairstyle") REFERENCES hairstyle_table,
            
    )""")
    #creates the reservation_table with all its field
    
    con.commit()

    file=open("Hairstyles spreadsheet.csv","r") #opens clients files with all the prices / services
    for line in file:  #ensures every record is inserted
        line=line.strip() #removes any whitespace
        hair_ID,hairstyle,price,face_shape,face_width,maintainence,hair_length=line.split(",")
        cur.execute("INSERT INTO hairstyle_table VALUES (?,?,?,?,?,?,?)",[hair_ID,hairstyle,price,face_shape,face_width,maintainence,hair_length])
        #puts the data from the spreadsheet into the database
    con.commit()

    file=open("Employee detail.csv","r") #opens clients files with their account details
    for line in file:  #ensures every record is inserted
        line=line.strip() #removes any whitespace
        username,password,phone_number,email,is_employee=line.split(",")
        cur.execute("INSERT INTO user_table VALUES (?,?,?,?,?)",[username,password,phone_number,email,is_employee])
        #puts the data from the spreadsheet into the database
    con.commit()
    print("Everything is fine")
    #gives me feedback telling me its fine

from appJar import gui

app=gui("User Login")

#################### Main Code ####################

def tempbutton(*arug):
    pass
tempbutton()


def valid_login ():
    user_username=app.getEntry("inputU") #stores username input as a variable
    user_password=app.getEntry("inputP") #stores password input as a variable
    employee=0
    
    cur.execute("SELECT password FROM user_table WHERE username=? AND is_employee=?", [user_username,employee])
    #Searches if users input is within database
    tbl_password=cur.fetchone() #Stores one result as password
    
    cur.execute("SELECT username FROM user_table WHERE username=? AND is_employee=?", [user_username,employee])
    tbl_username=cur.fetchone() #Stores one result as username
    
    if tbl_username==None: #Checks if username exists
        app.errorBox("Invalid customer username","Username not found")
    else:
        if tbl_password[0]!=user_password: #Compares if password in table match input
            app.errorBox("Invalid customer password","Incorrect password")
        else:
            app.hide("User Login") #Hides login page
            send_authenticate_code() #Send code
            app.showSubWindow("Authenticate") #Displays input code page
            app.setLabel("Welcome",f"Welcome, {user_username} to the reservation system.") #Updates the label
           
def barber_validate():
    app.hide("User Login") #Hides login page
    barber_username=app.getEntry("barberU") #stores username input as a variable
    barber_password=app.getEntry("barberP") #stores password input as a variable
    employee=1 #Variable used to check if details are for a barber account
    
    cur.execute("SELECT password FROM user_table WHERE username=? AND is_employee=?",[barber_username,employee])
    #Searches for passwords that only are from barbers accounts
    tbl_password=cur.fetchone() #Stores a single password value
    
    cur.execute("SELECT username FROM user_table WHERE username=? AND is_employee=?",[barber_username,employee])
    #Sarches for usernames that only from barbers accounts
    tbl_username=cur.fetchone() #Stores a single username value
    
    if tbl_username==None: #Checks if any usernames are found 
        app.errorBox("Invalid username","Username not found")
    else: 
        if tbl_password[0]!=barber_password: #Checks if tables passwords matches barbers input
            app.errorBox("Invalid password","Incorrect password")
        else:
            app.hideAllSubWindows(useStopFunction=False)
            app.hide("User Login")
            app.showSubWindow("Barber: select date") #Success, onto next window
          

def create_account():
    new_Uname=app.getEntry("new_username").strip() #Stores username input as a variable
    new_Pword=app.getEntry("new_password") #Stores password input as a variable
    re_enter_pword=app.getEntry("new_password2") #Stores re enter password as a variable
    new_Pnumber=app.getEntry("new_phone").replace(" ", "").strip() #Stores phone number as a variable
    new_email=app.getEntry("user_email")
    
    employee=0 #Creates a new variable to set is_employee field as 0
    valid=validate_details(new_Uname,new_Pword,new_Pnumber,re_enter_pword,new_email)
    #Runs details through function to check validity

    if valid==True: #Checks if details are valid
        cur.execute("INSERT INTO user_table VALUES (?,?,?,?,?)",[new_Uname,new_Pword,new_Pnumber,new_email,employee,])
        con.commit()
        app.hideAllSubWindows(useStopFunction=False) #Closes all subwindows
        app.show("User Login") #Hides login page
        
        #Inserts details from user into user table
    else:
        pass #Nothing happens till the user fixes details
        
    

def validate_details(new_Uname,new_Pword,new_Pnumber,re_enter_pword,new_email):
    app.hide("User Login")
    #Parameters are taken from the create_account()
    valid=False   #Creates the valid variables and automatically set to false

    for x in new_email:   #Checks if any character have @
        if x=="@":   #Checks indiviual characters for @
            email_valid=True   #If @ found, set valid to True
            break   #Exits loop if capital letter found
        else:
            next  #Goes to next character
            email_valid=False   #If no @ found, set valid to False

    for x in new_Pword:   #Checks if any character are a capital letter
        if x.isupper()==True:   #Checks indiviual characters for capital letters
            capital_valid=True   #If capital letter found, set valid to True
            break   #Exits loop if capital letter found
        else:
            next  #Goes to next character
            capital_valid=False   #If no capital found, set valid to False
       
    for x in new_Pword:    #Checks if any character are an integer
        if x.isdigit()==True:   #Checks indiviual characters for integers
            digit_valid=True   #If integers found, set valid to True
            break    #Exits loop if integers letter found
        else:
            next   #Goes to next character
            digit_valid=False   #If no integers found, set valid to False
            
    cur.execute("SELECT username FROM user_table WHERE username=?", [new_Uname])
    #Searches for username that matchs with user input
    tbl_username=cur.fetchall() #Stores results as variables
    if not tbl_username: #Checks if any results where found
        username_valid=True #If no duplicates, set valid as true
    else:
        username_valid=False #If duplicate, set valid as false
    

    if len(new_Uname)>0 and len(new_Uname)<12 and username_valid==True: #Checks if username is between 0 to 11 characters and unique
         if len(new_Pword)>6 and len(new_Pword)<16 and digit_valid==True and capital_valid==True and re_enter_pword==new_Pword:
         #Checks if password has a capital and interger and if between 7 to 15 characters and if both entered password match
             if len(new_Pnumber)!=11:   #Checks if phone number has 11 characters 
                  app.errorBox("Phone number error","Invalid phone number")   #If not 11 characters, error message

             else:
                 if len(new_email)>0 and email_valid==True:
                     app.infoBox("Correct details","All details are valid, creating account") #Success
                     valid=True   #Set valid to True, used in create_account()
                 else:
                     app.errorBox("Email error","Invalid email address") #If emails incorrect format, error message

         else:
             if re_enter_pword!=new_Pword:   #Checks if re enter password matches password
                 app.errorBox("Re enter password error","Passwords do not match")   #If no matches, error message

             else:
                 app.errorBox("Password error","Invalid password")   #If password doesnt follow requirments, error message
               
                      
    else:
        app.errorBox("Username","invalid username or username already taken")   #If username doesnt follow requirements, error message
    return valid #Used in create account function


def get_times():
    
    d_pick=app.getDatePicker("date")  #Stores customers date input
    b_pick=app.getOptionBox("Barbers: ")  #Stores cutomers barber input

    cur.execute("SELECT reservation_time FROM reservation_table WHERE barber_name=? AND reservation_date=?",[b_pick,d_pick])
    #Finds reservations with barber / date input
    results=cur.fetchall()
    #Stores all the results in a 2D list

    bookedTimes=[] #Creates a blank 1D list 
    for eachTime in results: #Passes through each reult 
        bookedTimes.append(eachTime[0])#Inserts all results into new 1D list

    time_slots=['7:00','8:00','9:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00']
    #Lists with all availible time slots

    availible_times=[] #Create a blank 1D list
    for index_x in time_slots: #Passes through each index in time slots
        if index_x not in bookedTimes: #Checks if searched index found within booked times
            availible_times.append(index_x) #If not, add into new list
        else:
            pass
    app.changeOptionBox("Time Slots: ",availible_times)
    #Updates option box with availible times

def confirmation():
    final_date=app.getDatePicker("date") #Stores customers date input
    final_time=app.getOptionBox("Time Slots: ") #Stores customers time input 
    final_barber=app.getOptionBox("Barbers: ") #Stores customers barber input
    final_hairstyle=app.getOptionBox("Hairstyles: ") #Stores customers hairstyle input
    cur.execute("SELECT price FROM hairstyle_table WHERE hairstyle=?",[final_hairstyle])
    #Searches for the price of the customers hairstyle
    final_price=cur.fetchone() #Stores the price of a variable

    app.setLabel("final date","Date: "+str(final_date)) #Update date label
    app.setLabel("final time","Time: "+str(final_time)) #Update time label
    app.setLabel("final barber","Barber: "+str(final_barber)) #Update barber label
    app.setLabel("final hairstyle","Hairstyle: "+str(final_hairstyle)) #Update hairstyle label
    app.setLabel("final price","Price: £"+str(final_price[0])) #Update price label
    
def insert_reservation():
    username=app.getEntry("inputU")#Stores customers username input
    final_date=app.getDatePicker("date") #Stores customers date input
    final_time=app.getOptionBox("Time Slots: ") #Stores customers time input 
    final_barber=app.getOptionBox("Barbers: ") #Stores customers barber input
    final_hairstyle=app.getOptionBox("Hairstyles: ") #Stores customers hairstyle input
    cur.execute("SELECT price FROM hairstyle_table WHERE hairstyle=?",[final_hairstyle])
    #Searches for the price of the customers hairstyle
    final_price=cur.fetchone() #Stores the price of a variable
    final_message=app.getEntry("message")
    
    cur.execute("INSERT INTO reservation_table (barber_name,reservation_time,reservation_date,hairstyle,username,message)VALUES (?,?,?,?,?,?)",[final_barber,final_time,final_date,final_hairstyle,username,final_message])
    #Creates a new record in reservation table with all relevent fields filled out
    con.commit()
    app.infoBox("Success!","Reservation has been created successfully, a receipt has been sent to your email")
    #Lets customer know that the reservation has been created
    send_reciept()
    app.hideSubWindow("Confirmation")
    app.showSubWindow("Menu")
    #Jumps back to main menu at the end


def generate_RH():
    head_shape=app.getOptionBox("Describe your face shape:        ") #Stores face shape input
    head_width=app.getOptionBox("Describe your face width:        ") #Stores face width input
    u_maintainence=app.getOptionBox("Describe level of hairstyle maintenance:  ") #Stores maintainance input
    hair_length=app.getOptionBox("Describe your desired length of hair:  ") #Stores hair length input

    cur.execute("SELECT hairstyle FROM hairstyle_table WHERE face_shape=? AND face_width=? AND maintainence=? AND hair_length=?",[head_shape,head_width,u_maintainence,hair_length])
    #Searches for hairstyles that attributes matches the customers input
    r_hairstyle=cur.fetchall() #Stores search results into 2D list

    if not r_hairstyle: #Checks if any results where found
        hairstyles=fetch_hairstyle()
        app.changeOptionBox("Hairstyles: ",hairstyles)
        #Resets the option box, incase they have already altered the list
        app.errorBox("No matches","No hairstyles found, please select your own")
        #Error message, alerting no matches where found, so it resets the options 
        
    else: #Run if results where found
        recommended_hairstyle=[] #Creats empty list 
        for x in r_hairstyle: #Checks every index
            recommended_hairstyle.append(x[0]) #Takes the first value and places in list
        app.changeOptionBox("Hairstyles: ",recommended_hairstyle)
        
        #Updates availible option boxes with generated hairstyles
        app.infoBox("Matches","Some recommendation have been found!")
        #Alerts user that matches have been found

def valid_date():
    date=app.getDatePicker("date") #Stores customer date input
    today=date.today() #Stores the current date

    if date<today: #Checks if date picked is in the past
        app.errorBox("Date error","This date is in the past")
        #Error message if in past
    else:
        select_time()
        #Continues the program
    
def get_reservations():
    app.deleteAllGridRows("view_r") #Resets the table
    username=app.getEntry("inputU") #Stores username within variable
    cur.execute("SELECT reservation_date,reservation_time,barber_name,hairstyle FROM reservation_table WHERE username=?",[username])
    #Fetches reservation details with the username inputted
    reservations=cur.fetchall() #Stores reservations within variable

    if not reservations:
        #Checks if varible has reservations 
        app.showSubWindow("Menu") #If no reservations, output an message
        app.infoBox("No reservations present","You have no current reservations")
        #Message presented to the user
    else:
        app.addTableRows("view_r",reservations)
        #If reservations, add the list of reservations within the table
        app.showSubWindow("Reservations") #Display the reservation window
        app.hideSubWindow("Menu") #Hides the previous window, menu

def authenticate_code():
    user_code=app.getEntry("code_input") #Stores user input

    if user_code!=str(verify_code): #Compare user code to actual code
        app.errorBox("Verification failed","Authentication code do not match")
        #Error message if code a message dont match
    else:
        app.hideSubWindow("Authenticate")
        app.showSubWindow("Menu")
        #If code match up, it present the menu page
        

def send_authenticate_code():
    username=app.getEntry("inputU") #Stores the customer username
    cur.execute("SELECT email FROM user_table WHERE username=?",[username])
    #Fetches email within the user table with the customers username
    tbl_email=cur.fetchone() #Stores customer email address
    
    email_from = 'thebarbershop341@gmail.com' #Stores the sender email
    password = 'dvxyukjbjyaaqmas' #Password that gains access to senders emails
    email_to=str(tbl_email[0]) #Sets the recipient email as customer email

    global verify_code
    #Sets the verification code as global to use in other function
    verify_code=random.randint(100000,999999)
    #Generates the authentication code using random library
    email_content=("Verification code - "+str(verify_code))
    #Email content itself that going to be sent 

    context = ssl.create_default_context()
    #Creates a secure connection with server
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_from, password) #Login to senders email address
        server.sendmail(email_from, email_to,email_content)
        #Sends the email with recipient details and email itself

def send_reciept():
    username=app.getEntry("inputU") #Stores the customer username
    cur.execute("SELECT email FROM user_table WHERE username=?",[username])
    #Fetches email within the user table with the customers username
    tbl_email=cur.fetchone() #Stores customer email address
    
    final_date=app.getDatePicker("date") #Stores customers date input
    final_time=app.getOptionBox("Time Slots: ") #Stores customers time input 
    final_barber=app.getOptionBox("Barbers: ") #Stores customers barber input
    final_hairstyle=app.getOptionBox("Hairstyles: ") #Stores customers hairstyle input
    cur.execute("SELECT price FROM hairstyle_table WHERE hairstyle=?",[final_hairstyle])
    #Searches for the price of the customers hairstyle
    final_price=cur.fetchone() #Stores the price of a variable

    email_from = 'thebarbershop341@gmail.com' #Stores the sender email
    password = 'dvxyukjbjyaaqmas' #Password that gains access to senders emails
    email_to=str(tbl_email[0]) #Sets the recipient email as customer email

    email_content=f"""  
    Your reservation details,
    
    Date - {final_date}
    Time - {final_time}
    Price - {final_price[0]}
    Barber - {final_barber}
    Hairstyle - {final_hairstyle}"""
    #Email that will be sent to the user
   
    context = ssl.create_default_context()
    #Creates a secure connection with server
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_from, password) #Login to senders email address
        server.sendmail(email_from, email_to,email_content)
        #Sends the email with recipient details and email itself

def barber_get_reservation():
    app.deleteAllGridRows("B_view") #Resets the table
    barber=app.getEntry("barberU") #Stores barber name within variable
    b_date=app.getDatePicker("b_date")
    cur.execute("SELECT username,reservation_time,hairstyle FROM reservation_table WHERE barber_name=? and reservation_date=?",[barber,b_date])
    #Fetches reservation details with the barber name and date inputted
    b_reservations=cur.fetchall() #Stores reservations within variable

    if not b_reservations: #Checks if varible has reservations 
        app.hideSubWindow("Barber reservations") #Closes this window
        app.showSubWindow("Barber: select date") #Shoes select date window
        app.infoBox("No reservations","No reservation are present on this day")
        #Message presented to the user
    else:
        #If reservations, add the list of reservations within the table
        app.addTableRows("B_view",b_reservations)
        app.showSubWindow("Barber reservations")
        #Displays the barber reservations page

def delete_reservation(row_num):
    delete=app.getTableRow("view_r",row_num) #Stores the reservation being deleted
    result=app.questionBox("Are you sure?",f"Are you sure you want to delete the reservation at {delete[0]}?", parent="Reservations")
    #Ensures user if wants to delete reservation

    if result==True: #If they want to delete
        app.deleteGridRow("view_r",row_num) #First delete the row on the table
        cur.execute("DELETE FROM reservation_table WHERE reservation_date=? AND reservation_time=?",[delete[0],delete[1]])
        con.commit()
        #Next deletes of the reservation table
        app.infoBox("Deleted",f"Reservation on {delete[0]} has been successfuly deleted")
        #Informs user that it has been deleted

def delete_old_reservations():
    today=date.today() #Stores the current date
    cur.execute("SELECT reservation_date FROM reservation_table")
    #Fetches all reservations currently in the table
    all_reservations=cur.fetchall()

    for each_date in all_reservations: #Checks every index
        year,month,day=each_date[0].split("-")
        #Splits date into 3. The year, month and day
        reservation_date=datetime.date(int(year),int(month),int(day))
        #Converts the string into into datetime data type
        if (reservation_date<today): #Checks if reservation is in the past
            cur.execute("DELETE FROM reservation_table WHERE reservation_date=?",[each_date[0]])
            #If in the past, delete from the table
            con.commit()

def view_more(row_num1):
    view_this=app.getTableRow("B_view",row_num1) #Assigns the record selected to a variable
    b_date=app.getDatePicker("b_date") #Assigns the dates to a variable
    barber_username=app.getEntry("barberU") #Stores username input within a variable
    cur.execute("SELECT username,phone_number,email FROM user_table WHERE username=?",[view_this[0]])
    #Fetches all relevent customer details
    user_details=cur.fetchone() #Stores the details within a variable
    cur.execute("SELECT message FROM reservation_table WHERE reservation_date=? AND reservation_time=? AND barber_name=?",[b_date,view_this[1],barber_username])
    #Fetches the message that the user may have inputted
    message=cur.fetchone() #Stores the message within a variable
    con.commit()

    app.setLabel("extra info",f""" 
    Username: {user_details[0]}
    Phone number: {user_details[1]}
    Email: {user_details[2]}
    Message: {message[0]}""")
    #Sets the label with all the inforamtion stored within the variables
    app.showSubWindow("View more")

def edit_details():
    edit_hairstyle=app.getOptionBox("Edit: ") #Retrievs hairstyle name input
    new_price=app.getEntry("New price: ").strip() #Retrievs new price input
    shape=app.getOptionBox("New shape: ") #Stores face shape input
    width=app.getOptionBox("New width: ") #Stores face width input
    maintainence=app.getOptionBox("New maintainence: ") #Stores hair maintainence input
    length=app.getOptionBox("New hair length: ") #Stores length input as variable

    if new_price.replace(".", "").isnumeric()==True: #Validates if input is all integers
        cur.execute("UPDATE hairstyle_table SET price=?,face_shape=?,face_width=?,maintainence=?,hair_length=? WHERE hairstyle=?",[new_price,shape,width,maintainence,length,edit_hairstyle])
        con.commit()
        #If input valid, inserts into the table
        app.infoBox("Successfully updates","New changes have been set")
    else:
        app.errorBox("Format error","Price in incorrect format")
        #If input invalid, error message

def fetch_hairstyle():
    cur.execute("SELECT hairstyle FROM hairstyle_table")
    con.commit()
    #Fetches all  hairstyles from hairstyles table
    hairstyle_tbl=cur.fetchall()
    
    #Stores hairstyles within table
    hairstyles=[] #Creates an empty list
    for each_hairstyle in hairstyle_tbl:
        #Checks through every index in reservations
        hairstyles.append(each_hairstyle[0])
        #Places hairstyles within reservation
    return hairstyles

def insert_hairstyle():
    name=app.getEntry("Name: ") #Stores name input in varible
    price=app.getEntry("Price: ").strip() #Stoes price input in variable
    shape=app.getOptionBox("Face shape: ") #Stores face shape input
    width=app.getOptionBox("Face width: ") #Stores face width input
    maintainence=app.getOptionBox("Maintainence: ") #Stores hair maintainence input
    length=app.getOptionBox("Hair length: ") #Stores length input as variable

    if price.replace(".", "").isnumeric()==True: #Checks if price valid input
        cur.execute("INSERT INTO hairstyle_table (hairstyle,price,face_shape,face_width,maintainence,hair_length)VALUES (?,?,?,?,?,?)",[name,price,shape,width,maintainence,length])
        con.commit()
        #If valid, inserts into the table
        app.infoBox("Successfully updated","New hairstyle has been added")
        #Message box, informing barber
    else:
        #If invalid, error message
        app.errorBox("Incorrect format 2","Price is in incorrect format")
        
def confirm_delete_hairstyle():
    delete_hairstyle=app.getOptionBox("Delete: ") #Retrives hairstyle being deleted
    result=app.questionBox("Delte hairstyle?",f"Are you sure you want to delete the hairstyle, {delete_hairstyle}?", parent="Delete hairstyle")
    #Confirms if barber wants to delete hairstyles

    if result==True: #Checks if they confirm or not
        cur.execute("DELETE FROM hairstyle_table WHERE hairstyle=?",[delete_hairstyle])
        #If confirmed, deletes hairstyle from hairstyle table
        con.commit()
        app.infoBox("Successfully deleted",f"Hairstyle, {delete_hairstyle} has been deleted")
        #Message that informs barber
    
    
def home():
    app.hideAllSubWindows(useStopFunction=False) #Closes all subwindows
    app.showSubwindow("Menu")
    #Go backs to menu
    
def edit_hairstyle():
    hairstyles=fetch_hairstyle() #Retrieves all hairstyles
    app.changeOptionBox("Edit: ",hairstyles) #Updates the option box

    app.hideAllSubWindows(useStopFunction=False) #Closes all subwindows
    app.showSubWindow("Edit hairstyles")

def new_user():
    app.showSubWindow("New user")

def barber_login():
    app.showSubWindow("Barber login")

def reset_hairstyle():
    hairstyles=fetch_hairstyle()
    app.changeOptionBox("Hairstyles: ",hairstyles)

    
def select_barber():
    app.hideAllSubWindows(useStopFunction=False) #Closes all subwindows
    app.showSubWindow("Select barber")

def select_hairstyle():
    hairstyles=fetch_hairstyle() #Runs function to get hairstyles
    app.changeOptionBox("Hairstyles: ",hairstyles) #Updates list of hairstyles
    app.hideAllSubWindows(useStopFunction=False) #Closes all subwindows
    app.showSubWindow("Select hairstyle")

def select_date():
    final_message=app.getEntry("message") #Stores message
    if len(final_message)>20: #Checks if message is valid
        app.errorBox("Message error","Message to large, must be less than 20 characters")
        #If not, error message
    else:
        app.hideAllSubWindows(useStopFunction=False) #Closes all subwindows
        app.showSubWindow("Select date")
        #If valid, next window

def select_time():
    get_times() #Retreives all available time/updates option box
    app.hideAllSubWindows(useStopFunction=False) #Closes all subwindows
    app.showSubWindow("Select time")

def confirmation_screen():
    confirmation()
    app.hideAllSubWindows(useStopFunction=False) #Closes all subwindows
    app.showSubWindow("Confirmation")

def recommend_hairstyle():
    app.hideAllSubWindows(useStopFunction=False) #Closes all subwindows
    app.showSubWindow("Recommend hairstyle")

def generate_hairstyle():
    generate_RH() #Generates recommend hairstyle/update options
    app.hideAllSubWindows(useStopFunction=False) #Closes all subwindows
    app.showSubWindow("Select hairstyle")

def home():
    app.hideAllSubWindows(useStopFunction=False) #Closes all subwindows
    app.showSubWindow("Menu")

def b_home():
    app.deleteAllGridRows("B_view") #Resets tables
    app.hideAllSubWindows(useStopFunction=False) #Closes all subwindows
    #Hides all subwindows
    app.showSubWindow("Barber: select date")
    #Back to select date window

def barber_reservation():
    app.hideAllSubWindows(useStopFunction=False) #Closes all subwindows
    barber_get_reservation() #Retrievs all reservatons


def new_hairstyle():
    app.hideAllSubWindows(useStopFunction=False) #Closes all subwindows
    app.showSubWindow("New hairstyle")

def edit_menu():
    app.hideAllSubWindows(useStopFunction=False) #Closes all subwindows
    app.showSubWindow("Edit menu")

def delete_hairstyle():
    hairstyles=fetch_hairstyle() #Retrieves all hairstyles
    app.changeOptionBox("Delete: ",hairstyles) #Set option box
    app.hideAllSubWindows(useStopFunction=False) #Closes all subwindows
    app.showSubWindow("Delete hairstyle")
            
def interface():
    ##### LOGIN PAGE #####
    app.setSize("450x250")#Sets size of window
    app.setResizable(False) #Prevents window size change
    app.addImage("logo11","logo.png", compound=None)
    #Adds the barbershop logo
    app.addLabel("Login title","Login",1,1)
    app.setFont(size=13, family="Bell MT", weight="bold")
    #Sets the program font/size/weight
    app.setBg("#ded8ca", override=True)
    #Sets the backround colour
    app.getLabelWidget("Login title").config(font=("Bell MT", "16", "bold"))
    #Configurates this widget only
     
    app.addLabel("user", "Username:",2,0)
    app.addEntry("inputU",2,1) #Input box for username
    app.addLabel("password","Password",3,0)
    app.addSecretEntry("inputP",3,1) #Input box for password
    
    app.addButton("Login",valid_login,4,3) #Login button
    app.addButton("Barber login",barber_login,4,0) #Barber login
    app.addButton("New user",new_user,4,1) #Create user button

    ##### 2 FACTOR AUTHENTICATION #####
    app.startSubWindow("Authenticate") #Creates new subwindow
    app.setSize("450x250") #Sets size of window
    app.setResizable(False) #Fixes size of window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo10","logo.png", compound=None)
    
    app.addIcon("Enter verification code sent to your email ","padlock-closed", compound="right")
    app.addSecretEntry("code_input") #Entry box for user to input their code
    app.addButton("Verify",authenticate_code)
    #Once clicked run the validate function
    app.setEntryDefault("code_input","#######")
    app.stopSubWindow() #Stops the window
    
    
    ##### MAIN MENU #####
    app.startSubWindow("Menu") #Create a new subwindow
    app.setSize("500x350") #Sets size of window
    app.setResizable(False) #Fixes size of window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo12","logo.png", compound=None)

    app.addLabel("Welcome",[]) #Title of window
    app.getLabelWidget("Welcome").config(font=("Bell MT", "15", "bold"))

    app.addIconButton("Create reservation",select_barber,"book-alt-2", align="top")
    #New Reservation button
    app.addIconButton("View/delete reservations",get_reservations,"view", align="top")
    #View reservation button
    app.stopSubWindow() #Stops the window

    ##### CREATE NEW USER #####
    app.startSubWindow("New user") #Creating new subwindow
    app.setSize("500x350") #Sets the size of the window
    app.setResizable(False) #Fixes the size of window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo2","logo.png", compound=None)
    
    app.addIcon("Create new account ","register", compound="right") #Title of window
    app.addLabel("username1", "Username:",2,0)
    app.addEntry("new_username",2,1) #Input box for new username
    app.addLabel("password2","Password: ",3,0)
    app.addSecretEntry("new_password",3,1) #Input box for new password
    app.addLabel("repassword2","Re-enter password: ",4,0)
    app.addSecretEntry("new_password2",4,1) #Input box to check if password matches
    app.addLabel("phone","Phone number: ",5,0)
    app.addEntry("new_phone",5,1) #Input box for phone number
    app.addLabel("email","Email address: ",6,0)
    app.addEntry("user_email",6,1) #Input box for email address
    app.addButton("Create account",create_account,7,1) #Button leads to validating / inserting
    app.stopSubWindow() #Stops the window

 
    ##### BARBER LOGIN #####
    app.startSubWindow("Barber login") #Creates a new subwindow
    app.setSize("400x300") #Sets the size of the window
    app.setResizable(True) #Prevents change to size window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo3","logo.png", compound=None)
    
    app.addIcon("Barber login ","cut", compound="right")
    app.addLabel("B_username", "Username: ",2,0)
    app.addEntry("barberU",2,1) #Input box for username
    app.addLabel("B_password","Password: ",3,0)
    app.addSecretEntry("barberP",3,1) #Input box for password

    app.addButton("Login to calendar",barber_validate,4,1)
    #Button leads validate function

    app.stopSubWindow()

    ##### SELECT BARBER #####
    app.startSubWindow("Select barber") #Creates a new subwindow
    app.setSize("500x350") #Sets the size of the window
    app.setResizable(False) #Prevents change to size window
    app.setBg("#ded8ca", override=False)
    app.addImage("logo4","logo.png", compound=None)
    
    app.addIcon("Select a barber ","cut", compound="right")
    app.addLabelOptionBox("Barbers: ", [" Liam ", " Lucus ", " Dave "," Timothy "])
    #Displays all barber options in option box
    app.addIconButton("Hairstyle",select_hairstyle,"arrow-8-right", align="right")
    #Confirms selection and moves to hairstyle subwindow
    app.addIconButton("home0",home,"home", align=None) #Create the icon 
    app.stopSubWindow()

    ##### SELECT HAIRSTYLE #####
    app.startSubWindow("Select hairstyle") #Creates a new subwindow
    app.setSize("500x350") #Sets the size of the window
    app.setResizable(False) #Prevents change to size window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo5","logo.png", compound=None)
    app.addLabel("hairstyle_pick","Select a hairstyle:",)
    app.addLabelOptionBox("Hairstyles: ",[])
    #Displays all hairstyle options in option box
    app.addEntry("message") #Entry box for messages for the barber
    app.setEntryDefault("message", "Fade/additional info")
    app.addIconButton("Not sure ",recommend_hairstyle,"help", align="right")    
    app.addIconButton("Reset",reset_hairstyle,"md-reload", align="right")
    app.addIconButton("Date",select_date,"arrow-8-right", align="right")
    #Confirm hairstyle and moves to date selection
    app.addIconButton("home1",home,"home", align=None)
    app.stopSubWindow()

    ##### SELECT DATE #####
    app.startSubWindow("Select date") #Creates a new subwindow
    app.setSize("500x350") #Sets the size of the window
    app.setResizable(False) #Prevents change to size window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo6","logo.png", compound=None)
    
    app.addIcon("Select a date ","calendar-alt-1", compound="right")
    app.addDatePicker("date",2,0) #Select any days of the year
    app.setDatePickerRange("date", 2023, endYear=2025) #Limits the range to 2023
    app.setDatePicker("date")
    app.addIconButton("Time",valid_date,"arrow-8-right", align="right") #Confirms and moves validate date
    app.addIconButton("home2",home,"home", align=None)
    app.stopSubWindow()

    ##### SELECT TIME #####
    app.startSubWindow("Select time") #Creates a new subwindow
    app.setSize("500x350") #Sets the size of the window
    app.setResizable(False) #Prevents change to size window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo7","logo.png", compound=None)

    app.addIcon("Select an available timeslot ","time", compound="right")
    app.addLabelOptionBox("Time Slots: ",[],4,0)#Creates option box for availible times
    app.addIconButton("Confirmation",confirmation_screen,"arrow-8-right", align="right") #Confirms and moves to confirmation
    app.addIconButton("home3",home,"home", align=None)
    app.stopSubWindow()

    ##### CONFIRMATION SCREEN #####
    app.startSubWindow("Confirmation") #Creates a new subwindow
    app.setSize("500x400") #Sets the size of the window
    app.setResizable(False) #Prevents change to size window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo8","logo.png", compound=None)
    
    app.addLabel("R_details","Reservation details")
    app.getLabelWidget("R_details").config(font=("Bell MT", "16", "bold","underline"))
    app.addLabel("final date",[]) #Add a blank label for final date
    app.addLabel("final time",[]) #Add a blank label for final time
    app.addLabel("final barber",[]) #Add a blank label for final barber
    app.addLabel("final hairstyle",[]) #Add a blank label for final hairstyle
    app.addLabel("final price",[]) #Add a blank label for final price
    app.addIconButton("Confirm",insert_reservation,"checkbox", align="right")
    #Confirms details and runs function to insert into table
    app.addIconButton("home4",home,"home", align=None)
    app.stopSubWindow()

    ##### RECOMMENDED HAIRSTYLE #####
    app.startSubWindow("Recommend hairstyle") #Creates a new subwindow
    app.setSize("500x350") #Sets the size of the window
    app.setResizable(False) #Prevents change to size window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo9","logo.png", compound=None)

    app.addLabel("R_hairstyle","Answer the questions to generate a recommended hairstyle!",1,0)
    #Lets users what to do
    app.addLabelOptionBox("Describe your face shape:        ",["Round","Square"])
    app.addLabelOptionBox("Describe your face width:        ",["Narrow","Wide"])
    app.addLabelOptionBox("Describe level of hairstyle maintenance:  ",["Non/Little","Medium","Lot"])
    app.addLabelOptionBox("Describe your desired length of hair:  ",["Short","Medium","Long"])
    #These provide options for user to select, whilst asking questions
    app.addButton("Generate!",generate_hairstyle)
    #Onces clicked, runs a function to generate hairstyle
    app.addIconButton("home5",home,"home", align=None)
    app.stopSubWindow()

    ##### VIEW RESERVATIONS #####
    app.startSubWindow("Reservations") #Creates a new subwindow
    app.setSize("550x450") #Sets the size of the window
    app.setResizable(False) #Prevents change to size window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo13","logo.png", compound=None)
    app.addLabel("current_r","All current reservations")
    app.getLabelWidget("current_r").config(font=("Bell MT", "16", "bold","underline"))

    app.addTable("view_r",[["Date", "Time", "Barber", "Hairstyle"]], action=delete_reservation,actionButton="Delete")
    #Creates table that sets the headers and leaves the rows blank
    app.addIconButton("home6",home,"home", align=None)
    #Home button to lead to menu
    app.stopSubWindow()

    ##### BARBER SELECTS DATE #####
    app.startSubWindow("Barber: select date") #Creates a new subwindow
    app.setSize("350x350") #Sets the size of the window
    app.setResizable(False) #Prevents change to size window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo112","logo.png", compound=None)

    app.addIcon("Search reservation date ","search", compound="right")
    app.addDatePicker("b_date",2,0) #Select any days of the year
    app.setDatePickerRange("b_date", 2023, endYear=2025) #Limits the range to 2025
    app.setDatePicker("b_date")
    app.addIconButton("View reservation",barber_reservation,"arrow-8-right", align="right") #Confirms and moves to confirmation
    app.addButton("Edit hairstyles",edit_menu)
    app.stopSubWindow()

    ##### BARBER VIEW RESERVATION #####
    app.startSubWindow("Barber reservations") #Creates a new subwindow
    app.setSize("550x450") #Sets the size of the window
    app.setResizable(False) #Prevents change to size window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo14","logo.png", compound=None)
    app.addIcon("All current reservations","book", compound="right")

    app.addTable("B_view",[["Username","Time","Hairstyle"]], action=view_more,actionButton="View more")
    #Creates table with it headers defined and records left blank
    app.addIconButton("home16",b_home,"search", align=None)
    #Home button
    app.stopSubWindow()

    ##### BARBER VIEW MORE INFO #####
    app.startSubWindow("View more")
    app.setSize("400x300") #Sets the size of the window
    app.setResizable(False) #Prevents change to size window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo32","logo.png", compound=None)
    app.addLabel("label2","Additional information")
    
    app.addLabel("extra info",[],2,0)
    #Sets a blank label to set later
    app.stopSubWindow()
    

    ##### BARBER EDIT HAIRSTYLES #####
    app.startSubWindow("Edit hairstyles")
    app.setSize("550x450") #Sets the size of the window
    app.setResizable(False) #Prevents change to size window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo18","logo.png", compound=None)
    app.addOptionBox("Edit: ",[])
    #Displays updated hairstyle options
    app.addLabelEntry("New price: ") #Input new price
    app.addLabelOptionBox("New shape: ",["Square","Round"])
    app.addLabelOptionBox("New width: ",["Narrow","Wide"])
    app.addLabelOptionBox("New maintainence: ",["Non/Little","Medium","Lot"])
    app.addLabelOptionBox("New hair length: ",["Short","Medium","Long"])
    #Input options for hairstyle attributes
    app.addButton("Confirm edit",edit_details)
    #Buttons confirms the edit

    app.addIconButton("home18",b_home,"search", align=None)
    app.stopSubWindow()

    ##### BARBER NEW HAIRSTYLE #####
    app.startSubWindow("New hairstyle")
    app.setSize("550x450") #Sets the size of the window
    app.setResizable(False) #Prevents change to size window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo19","logo.png", compound=None)

    app.addLabelEntry("Name: ") #Input box for name
    app.addLabelEntry("Price: ") #Input box for price
    app.addLabelOptionBox("Face shape: ",["Square","Round"])
    app.addLabelOptionBox("Face width: ",["Narrow","Wide"])
    app.addLabelOptionBox("Maintainence: ",["Non/Little","Medium","Lot"])
    app.addLabelOptionBox("Hair length: ",["Short","Medium","Long"])
    #Input options for hairstyle attributes
    app.addButton("Create hairstyle",insert_hairstyle)
    #Button that creates hairstyle
    app.addIconButton("home24",b_home,"search", align=None)
    #Home button
    app.stopSubWindow()

    ##### BARBER EDIT MENU #####
    app.startSubWindow("Edit menu")
    app.setSize("350x300") #Sets the size of the window
    app.setResizable(False) #Prevents change to size window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo20","logo.png", compound=None)

    app.addIconButton("Edit ",edit_hairstyle,"file-edit", align="right")
    #Leads to change price
    app.addIconButton("Add ",new_hairstyle,"file-upload", align="right")
    #Leads to create new hairstyle
    app.addIconButton("Delete ",delete_hairstyle,"cancel", align="right")
    #Leads to delete hairstyle
    app.addIconButton("home13",b_home,"search", align=None)
    #Home button to select date
    app.stopSubWindow()

    ##### BARBER DELETE HAIRSTYLE #####
    app.startSubWindow("Delete hairstyle")
    app.setSize("400x350") #Sets the size of the window
    app.setResizable(False) #Prevents change to size window
    app.setBg("#ded8ca", override=True)
    app.addImage("logo27","logo.png", compound=None)
    app.addOptionBox("Delete: ",[])
    #Displays updated hairstyle options
    app.addButton("Delete",confirm_delete_hairstyle)
    #Button deletes hairstyle
    app.addIconButton("home15",b_home,"search", align=None)
    #Home button to select date
    app.stopSubWindow()

    app.go()


#create_database()
delete_old_reservations()
interface()



