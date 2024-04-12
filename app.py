from flask import Flask, request, render_template, redirect, jsonify, session, send_file, url_for, flash
from flask_bootstrap import Bootstrap
import cx_Oracle
from datetime import datetime
import base64
from io import BytesIO


app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config["SECRET_KEY"] = 'Verysecr3tkey'

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

    if 'user' not in session:
        session['user'] = None

    # Change the template based on whether or not the user is logged in
    if session['user']:
        return render_template('home_user.html', org_list=[1, 2, 3], user=session['user'])

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
            session['user'] = myResult[0][0]
            return redirect('/')
        
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
    return render_template('organization_home.html', organization_name='Notre Dame', org_id=org_id)


# Posts for the organization
@app.route('/organization/<int:org_id>/posts/', methods=['GET', 'POST'])
def organization_posts(org_id):
    global connection

    if request.method == 'GET':
        with connection.cursor() as cursorObject:
            sql = "SELECT p.post_id, p.title, p.text, u.fullname, u.profile_picture FROM posts p, users u WHERE p.user_id = u.user_id and p.user_id = {} and p.org_id = {} ORDER BY p.post_id DESC".format(session['user'], org_id)
            cursorObject.execute(sql)
            post_list = cursorObject.fetchall()

            sql = "SELECT name FROM organizations WHERE org_id = {}".format(org_id)
            cursorObject.execute(sql)
            organization_name = cursorObject.fetchall()[0][0]

            post_list = list(post_list)
            for i, post in enumerate(post_list):
                if post[4] is not None:
                    image_stream = BytesIO(post[4].read())
                    image_data = base64.b64encode(image_stream.getvalue()).decode('utf-8')
                    post = list(post)
                    post[4] = f"data:image/jpeg;base64,{image_data}"
                    post_list[i] = tuple(post)

        return render_template('organization_posts.html', organization_name=organization_name, post_list=post_list, org_id=org_id, user=session['user'])

    elif request.method == 'POST':
        title = request.form.get('post_title')
        text = request.form.get('post_content')

        sql = "INSERT INTO posts (post_id, user_id, org_id, title, text) VALUES ((SELECT COALESCE(MAX(post_id), 0) + 1 FROM posts), {}, {}, '{}', '{}')".format(session['user'], org_id, title.replace("'", "''"), text.replace("'", "''"))


        with connection.cursor() as cursorObject:
            cursorObject.execute(sql)
            connection.commit()

        return redirect('/organization/{}/posts'.format(org_id))

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
