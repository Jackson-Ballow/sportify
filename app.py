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

##### Here are the routes that do not need to worry about admin status #####

# Home page
@app.route('/', methods=['GET'])
def home():
    global connection

    if 'user' not in session:
        session['user'] = None

    # Change the template based on whether or not the user is logged in
    if session['user']:
        # Get the list of organizations the user is in
        with connection.cursor() as cursorObject:
            sql = "SELECT u.org_id, o.name, o.profile_picture, o.bio FROM users_organizations u JOIN organizations o ON u.org_id = o.org_id WHERE u.user_id = {}".format(session['user'])

            cursorObject.execute(sql)
            org_list = cursorObject.fetchall()

            org_list_photos = []
            process_list_with_images(org_list, org_list_photos, 2)

        return render_template('home_user.html', org_list=org_list_photos, user=session['user'])

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
        file = request.files['logo']
        
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

    if 'user' not in session or session['user'] is None:
        return redirect('/login/')

    if request.method == 'GET':
        return render_template('create_organization.html', user=session['user'])

    elif request.method == 'POST':
        org_name = request.form.get('org_name')
        bio = request.form.get('bio')
        file = request.files['logo']

        file_data = file.read()

        sql = "INSERT INTO organizations (org_id, name, bio, profile_picture) VALUES ((SELECT COALESCE(MAX(org_id), 0) + 1 FROM organizations), :org_name, :bio, :blob_data)"


        with connection.cursor() as cursorObject:
            cursorObject.execute(sql, {'org_name': org_name, 'bio': bio, 'blob_data': file_data})

            # Get the new org_id
            cursorObject.execute("SELECT MAX(org_id) FROM organizations")
            org_id = cursorObject.fetchone()[0]

            # Insert into users_organizations
            user_org_sql = "INSERT INTO users_organizations (user_id, org_id) VALUES (:user_id, :org_id)"
            cursorObject.execute(user_org_sql, {'user_id': session['user'], 'org_id': org_id})


            # Insert into organizations_admins
            user_org_sql = "INSERT INTO organizations_admins (user_id, org_id) VALUES (:user_id, :org_id)"
            cursorObject.execute(user_org_sql, {'user_id': session['user'], 'org_id': org_id}) 

            connection.commit()

        return redirect('/')


# About us page - this should not need to change
@app.route('/about_us/', methods=['GET'])
def about_us():
    if 'user' not in session:
        session['user'] = None

    return render_template('about_us.html', user=session['user'])


# Log out the user - clear the session and return a redirect to home
@app.route('/logout/', methods=['GET'])
def logout():
    if not session['user']:
        return redirect('/')

    session.clear()
    return redirect('/')


# Profile page to view stats and log out
@app.route('/profile/', methods=['GET'])
def profile():
    global connection

    if not session['user']:
        return redirect('/')

    with connection.cursor() as cursorObject:
        sql = "SELECT e.event_name, g.team1_name, g.team1_score, g.team2_name, g.team2_score FROM games g, games_users u, events e WHERE u.user_id = {} and u.game_id = g.game_id and g.event_id = e.event_id and e.sport_name = 'basketball'".format(session['user'])
    
        cursorObject.execute(sql)
        basketball_list = cursorObject.fetchall()

        sql = "SELECT e.event_name, g.team1_name, g.team1_score, g.team2_name, g.team2_score FROM games g, games_users u, events e WHERE u.user_id = {} and u.game_id = g.game_id and g.event_id = e.event_id and e.sport_name = 'football'".format(session['user'])
    
        cursorObject.execute(sql)
        football_list = cursorObject.fetchall()
    
        sql = "SELECT e.event_name, g.team1_name, g.team1_score, g.team2_name, g.team2_score FROM games g, games_users u, events e WHERE u.user_id = {} and u.game_id = g.game_id and g.event_id = e.event_id and e.sport_name = 'soccer'".format(session['user'])
    
        cursorObject.execute(sql)
        soccer_list = cursorObject.fetchall()
    
    return render_template('profile.html', user=session['user'], basketball_list=basketball_list, football_list=football_list, soccer_list=soccer_list)


##### START WORRYING ABOUT ADMIN STATUS HERE #####
##### HERE IS THE SECTION FOR A REGULAR USER VIEWING THE ORGANIZATION'S CONTENT #####

# Homepage for the organization
@app.route('/organization/<int:org_id>/', methods=['GET'])
def organization(org_id):
    global connection

    if not session['user']:
        return redirect('/')

    usr = membership(session['user'], org_id)

    if not usr["is_member"]:
        return redirect('/')

    with connection.cursor() as cursorObject:
        sql = "SELECT name FROM organizations WHERE org_id = {}".format(org_id)
        cursorObject.execute(sql)
        organization_name = cursorObject.fetchall()[0][0]

    if not usr["is_admin"]:
        return render_template('organization_home.html', organization_name=organization_name, org_id=org_id, user=session['user'])
    else:
        return "we need a template for this" # render_template('organization_home.html', organization_name=organization_name, org_id=org_id, user=session['user'])


# Posts for the organization
@app.route('/organization/<int:org_id>/posts/', methods=['GET', 'POST'])
def organization_posts(org_id):
    global connection

    if not session['user']:
        return redirect('/')

    usr = membership(session['user'], org_id)

    if not usr["is_member"]:
        return redirect('/')

    if request.method == 'GET':
        with connection.cursor() as cursorObject:
            # Note to Jackson: I changed this because I think we want people to see everyone's posts, not just their own
            #sql = "SELECT p.post_id, p.title, p.text, u.fullname, u.profile_picture FROM posts p, users u WHERE p.user_id = u.user_id and p.user_id = {} and p.org_id = {} ORDER BY p.post_id DESC".format(session['user'], org_id)
            sql = "SELECT p.post_id, p.title, p.text, u.fullname, u.profile_picture FROM posts p, users u WHERE p.user_id = u.user_id and p.org_id = {} ORDER BY p.post_id DESC".format(org_id)
            cursorObject.execute(sql)
            post_list = cursorObject.fetchall()

            sql = "SELECT name FROM organizations WHERE org_id = {}".format(org_id)
            cursorObject.execute(sql)
            organization_name = cursorObject.fetchall()[0][0]

            post_list_photos = []
            process_list_with_images(post_list, post_list_photos, 4)

        return render_template('organization_posts.html', organization_name=organization_name, post_list=post_list_photos, org_id=org_id, user=session['user'])

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
    if not session['user']:
        return redirect('/')

    usr = membership(session['user'], org_id)

    if not usr["is_member"]:
        return redirect('/')

    if request.method == 'GET':

        with connection.cursor() as cursorObject:
            # check post exists
            sql = "SELECT p.post_id, p.title, p.text, u.fullname, u.profile_picture FROM posts p, users u WHERE p.user_id = u.user_id and p.org_id = {} ORDER BY p.post_id DESC".format(org_id)
            cursorObject.execute(sql)
            post = cursorObject.fetchall()

            if not post:
                return redirect("/organization/{}/posts/".format(org_id))

            # get comments
            sql = "SELECT c.comment_id, c.text, u.fullname, u.profile_picture FROM comments c, users u WHERE c.post_id = {} AND c.user_id = u.user_id ORDER BY c.comment_id DESC".format(post_id)
            cursorObject.execute(sql)
            comment_list = cursorObject.fetchall()

            sql = "SELECT name FROM organizations WHERE org_id = {}".format(org_id)
            cursorObject.execute(sql)
            organization_name = cursorObject.fetchall()[0][0]

            comment_list_photos = []
            process_list_with_images(comment_list, comment_list_photos, 3)

            post_photo = []
            process_list_with_images(post, post_photo, 4)


        return render_template('comments.html', organization_name=organization_name, org_id=org_id, post=post_photo[0], comment_list=comment_list_photos)


    elif request.method == 'POST':
        text = request.form.get('comment_content')

        sql = "INSERT INTO comments (comment_id, user_id, post_id, text) VALUES ((SELECT COALESCE(MAX(comment_id), 0) + 1 FROM comments), {}, {}, '{}')".format(session['user'], post_id, text.replace("'", "''"))

        with connection.cursor() as cursorObject:
            cursorObject.execute(sql)
            connection.commit()

        return redirect('/organization/{}/posts/{}'.format(org_id, post_id))


# Page to view the stats of every game for each sport for an organization
@app.route('/organization/<int:org_id>/stats/', methods=['GET'])
def organization_stats(org_id):
    global connection

    if not session['user']:
        return redirect('/')

    usr = membership(session['user'], org_id)

    if not usr["is_member"]:
        return redirect('/')

    with connection.cursor() as cursorObject:
        sql = "SELECT e.event_name, g.team1_name, g.team1_score, g.team2_name, g.team2_score FROM games g, games_users u, events e WHERE e.org_id = {} and u.game_id = g.game_id and g.event_id = e.event_id and e.sport_name = 'basketball'".format(org_id)
    
        cursorObject.execute(sql)
        basketball_list = cursorObject.fetchall()

        sql = "SELECT e.event_name, g.team1_name, g.team1_score, g.team2_name, g.team2_score FROM games g, games_users u, events e WHERE e.org_id = {} and u.game_id = g.game_id and g.event_id = e.event_id and e.sport_name = 'football'".format(org_id)
    
        cursorObject.execute(sql)
        football_list = cursorObject.fetchall()
    
        sql = "SELECT e.event_name, g.team1_name, g.team1_score, g.team2_name, g.team2_score FROM games g, games_users u, events e WHERE e.org_id = {} and u.game_id = g.game_id and g.event_id = e.event_id and e.sport_name = 'soccer'".format(org_id)
    
        cursorObject.execute(sql)
        soccer_list = cursorObject.fetchall()
    

    return render_template('organization_stats.html', user=session['user'], organization_name="Notre Dame", basketball_list=basketball_list, football_list=football_list, soccer_list=soccer_list)


@app.route('/organization/<int:org_id>/events/', methods=['GET'])
def organization_events(org_id):
    if not session['user']:
        return redirect('/')

    usr = membership(session['user'], org_id)

    if not usr["is_member"]:
        return redirect('/')

    
    with connection.cursor() as cursorObject:
            today = str(datetime.today()).split(' ')[0]

            # show events that have not ended yet - I don't know why the date isn't working here
            sql = "SELECT event_id, event_name, sport_name, event_bio, event_logo FROM events WHERE org_id={}".format(org_id)
            #sql = "SELECT event_name, sport_name, event_bio, event_logo FROM events WHERE org_id={} AND end_date >= TO_DATE('{}', 'YYYY-MM-DD')".format(org_id, today)
            cursorObject.execute(sql)
            event_list = cursorObject.fetchall()

            sql = "SELECT name FROM organizations WHERE org_id = {}".format(org_id)
            cursorObject.execute(sql)
            organization_name = cursorObject.fetchall()[0][0]

            print(len(event_list))

            event_list_photos = []
            process_list_with_images(event_list, event_list_photos, 4)

            print(len(event_list_photos))

    return render_template('organization_events.html', user=session['user'], org_id=org_id, organization_name=organization_name, event_list=event_list_photos)


@app.route('/organization/<int:org_id>/events/<int:event_id>/', methods=['GET'])
def join_event(org_id, event_id):
    # Code to add a user to an event here...
    temp = "/organization/{org}/"

    return redirect(temp.format(org=org_id))



@app.route('/hire/', methods=['GET'])
def hire():
    return "We aren't recruiting, idk why you clicked this"

# I really have no idea what this caching stuff does
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.errorhandler(404)
def not_found(e):
    return "We can't find that page. Or maybe the site is just broken because you aren't using a Mac."


# This function checks a user's status as a member/admin/owner of an organization
# It returns a dictionary of booleans {"is_member": ??, "is_admin": ??, "is_owner": ??}
def membership(user_id, org_id):
    with connection.cursor() as cursorObject:
        sql = "SELECT * FROM users_organizations WHERE user_id={} AND org_id={}".format(user_id, org_id)
        cursorObject.execute(sql)
        user_in_org = len(cursorObject.fetchall()) > 0

        sql = "SELECT * FROM organizations_admins WHERE user_id={} AND org_id={}".format(user_id, org_id)
        cursorObject.execute(sql)
        user_is_admin = len(cursorObject.fetchall()) > 0

        # Not implemented yet
        """sql = "SELECT owner_id FROM organizations WHERE org_id={}".format(org_id)
        cursorObject.execute(sql)
        owner_id = cursorObject.fetchall()[0]
        user_is_owner = (owner_id == user_id)
        """

        usr = {
            "is_member": user_in_org,
            "is_admin": user_is_admin,
            "is_owner": False # hard coded for now
        }

        return usr

# this function takes in a list of databases rows containing an image and encodes the image bytes
# it returns the modified list
def process_list_with_images(original, corrected, photo_index):
    cpy = list(original)
    for i, item in enumerate(cpy):
        if item[photo_index] is not None:
            image_stream = BytesIO(item[photo_index].read())
            image_data = base64.b64encode(image_stream.getvalue()).decode('utf-8')
            item = list(item)
            item[photo_index] = f"data:image/jpeg;base64,{image_data}"
        
        corrected.append(tuple(item))


# Run the code
if __name__ == '__main__':
    # run your app
    app.run(host='0.0.0.0', port=8000)
