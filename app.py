from flask import Flask, request, render_template, redirect, jsonify, session, send_file, url_for, flash
from flask_bootstrap import Bootstrap
import cx_Oracle
from datetime import datetime


app = Flask(__name__)
bootstrap = Bootstrap(app)

user = False

### EXAMPLE CONNECTION TO DATABASE -- REMOVE LATER ###
connection = cx_Oracle.connect('jballow/jballow@localhost:1521/XE')

'''
cursor = connection.cursor()


cursor.execute('SELECT * FROM cat')
rows = cursor.fetchall()
print(rows)

cursor.close()
connection.close()
'''

##### Here are the routes that do not need to worry about admin status #####

# Home page
@app.route('/', methods=['GET'])
def home():
    # Change the template based on whether or not the user is logged in
    if user:
        return render_template('home_user.html', org_list=[1, 2, 3], user=user)

    else:
        return render_template('home_no_user.html')


# Login Page
@app.route('/login/', methods=['GET', 'POST'])
def login():
    global connection

    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        with connection.cursor() as cursorObject:
            sql = "SELECT * FROM users WHERE email = '{email}' and password = '{password}'"
            sql = sql.format(email=email, password=password)
            cursorObject.execute(sql)
            myResult = cursorObject.fetchall()

        if myResult and len(myResult) > 0:
            return 'yes'
        
        return 'no'


# Registeration Page
@app.route('/register/', methods=['GET', 'POST'])
def register():
    global connection

    if request.method == 'GET':
        return render_template('register.html')

    elif request.method == 'POST':
        fullname = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        file = request.files['imageUpload']
        
        if file.filename == '':
            return 'No selected file'

        file_data = file.read()

        sql = "INSERT INTO users (user_id, fullname, email, password, profile_picture) VALUES ((SELECT COALESCE(MAX(user_id), 0) + 1 FROM users), '{}', '{}', '{}', :blob_data)".format(fullname, email, password)

        with connection.cursor() as cursorObject:
            cursorObject.execute(sql, [file_data])
            connection.commit()

        return 'yes'

# Page to create an organization
@app.route('/create_organization/', methods=['GET', 'POST'])
def create_organization():
    global connection

    if request.method == 'GET':
        return render_template('create_organization.html')

    elif request.method == 'POST':
        org_name = request.form.get('org_name')
        bio = request.form.get('bio')
        file = request.files['imageUpload']

        if file.filename == '':
            return 'No selected file'

        file_data = file.read()

        sql = "INSERT INTO organizations (org_id, name, bio, profile_picture) VALUES ((SELECT COALESCE(MAX(org_id), 0) + 1 FROM organizations), '{}', '{}', :blob_data)".format(org_name, bio)

        with connection.cursor() as cursorObject:
            cursorObject.execute(sql, [file_data])

            # TODO ADD THE USER THAT CREATED THE ORG TO organizations_admins

            connection.commit()

        return 'yes'


# About us page - this should not need to change
@app.route('/about_us/', methods=['GET'])
def about_us():
    return render_template('about_us.html')


# Log out the user - clear the session and return a redirect to home
@app.route('/logout/', methods=['GET'])
def logout():
    # TODO Uncomment once we actually have a session
    # session.clear()
    return redirect('/')


# Profile page to view stats and log out
@app.route('/profile/', methods=['GET'])
def profile():
    # IMPORTANT, PLZ READ!
    # Input Notes:
    # For each sport, create a 2d array where each array inside consists of the following:
    # Index 0: Event Name
    # Index 1: Team 1's Name
    # Index 2: Team 1's Score
    # Index 3: Team 2's Name
    # Index 4: Team 2's Score

    # Input examples
    basketball_list = [
        ["Bookstore Basketball 2024", "Shrew's and the Gang", 16, "Other Lame Team", 21],
        ["Bookstore Basketball 2024", "Massive Men", 21, "Losing Team", 16]       
    ]

    football_list = [
        ["2024 CFB Season", "Notre Dame", 55, "Georgia Tech", 0],
        ["2024 CFB Season", "UGA", 45, "Georgia Tech", 0]       
    ]

    soccer_list = [
        ["Some Soccer Season", "Milan", 2, "Manchester United", 0]
    ]
    return render_template('profile.html', user=user, basketball_list=basketball_list, football_list=football_list, soccer_list=soccer_list)


##### START WORRYING ABOUT ADMIN STATUS HERE #####
##### HERE IS THE SECTION FOR A REGULAR USER VIEWING THE ORGANIZATION'S CONTENT #####

# Homepage for the organization
@app.route('/organization/<int:org_id>/', methods=['GET'])
def organization(org_id):
    return render_template('organization_home.html', organization_name='Notre Dame', org_id=0)


# Posts for the organization
@app.route('/organization/<int:org_id>/posts/', methods=['GET', 'POST'])
def organization_posts(org_id):
    return render_template('organization_posts.html', organization_name='Notre Dame', org_id=0, post_list=[1, 2, 3])


# View and leave comments on a post
@app.route('/organization/<int:org_id>/posts/<int:post_id>/', methods=['GET', 'POST'])
def comments(org_id, post_id):
    # This variable post will be the title, content, and pfp of the specific post_id
    post = None
    return render_template('comments.html', organization_name='Notre Dame', org_id=0, post=post, comment_list=[1, 2, 3])


# Page to view the stats of every game for each sport for an organization
@app.route('/organization/<int:org_id>/stats/', methods=['GET'])
def organization_stats(org_id):
    # For detail on how the data is ordered, view the route for profile

    basketball_list = [
        ["Bookstore Basketball 2024", "Shrew's and the Gang", 16, "Other Lame Team", 21],
        ["Bookstore Basketball 2024", "Massive Men", 21, "Losing Team", 16]       
    ]

    football_list = [
        ["2024 CFB Season", "Notre Dame", 55, "Georgia Tech", 0],
        ["2024 CFB Season", "UGA", 45, "Georgia Tech", 0]       
    ]

    soccer_list = [
        ["Some Soccer Season", "Milan", 2, "Manchester United", 0]
    ]

    return render_template('organization_stats.html', user=user, organization_name="Notre Dame", basketball_list=basketball_list, football_list=football_list, soccer_list=soccer_list)

# Page to view the stats of every game for each sport for an organization
@app.route('/organization/<int:org_id>/events/', methods=['GET'])
def organization_events(org_id):
    return render_template('organization_events.html', user=user, org_id=0, organization_name="Notre Dame", event_list=[1, 2, 3])


@app.route('/organization/<int:org_id>/events/<int:event_id>/', methods=['GET'])
def join_event(org_id, event_id):
    # Code to add a user to an event here...
    temp = "/organization/{org}/"

    return redirect(temp.format(org=org_id))

# Run the code
if __name__ == '__main__':
    # run your app
    app.run(host='0.0.0.0', port=8000)
