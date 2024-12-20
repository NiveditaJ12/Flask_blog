from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, LoginManager, current_user, logout_user, login_required
import flask_bcrypt # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash
from config import session, Base, engine
import models
import datetime

app = Flask(__name__)
app.secret_key = 'MySecreteKey'

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
 
bcrypt = flask_bcrypt.Bcrypt(app)

Base.metadata.bind = engine
Base.metadata.create_all(engine)

@login_manager.user_loader
def load_user(id):
     try:
        return session.get(models.User,id)
     except:
         return None


@app.route('/')
def index():
    page = request.args.get('page',1,type=int)
    per_page=3
    start = (page-1)*per_page
    end = start+per_page
    all_posts = session.query(models.Post).all()
    total_pages = (len(all_posts) + per_page -1)//per_page
    posts = all_posts[start:end]
    
    return render_template('index.html',posts = posts, total_pages=total_pages, page=page)

@app.route('/register', methods = ['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            passsword1 = request.form.get('password1')
            checkbox = request.form.get('checkbox')
            if password==passsword1:
                confirm_pass = password
                hashed_password = bcrypt.generate_password_hash(confirm_pass).decode('utf-8')
                if checkbox:
                    print(firstname, lastname,username,email,passsword1, password)
                    new_user = models.User(firstname=firstname, lastname=lastname, username=username, email=email, password=hashed_password)
                    session.add(new_user)
                    session.commit()
                    return redirect(url_for('login'))
                else:
                    flash('Please check the box','secondary')
                    return render_template('register.html')
            else:
                flash('Incorrect password','secondary')
                return render_template('register.html')
            
        else:
            return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return render_template('user_acc.html')
    else:
        if request.method=='POST':
                fusername = request.form.get('username')
                fpassword = request.form.get('password')
                remember_me = request.form.get('remember_me')
                user_account = session.query(models.User).filter(models.User.username==fusername).first()
                if user_account:
                    if bcrypt.check_password_hash(user_account.password, fpassword):
                        
                        login_user(user_account,remember=remember_me)
                        print(user_account.password)
                        next_page = request.args.get('next')
                        return redirect(next_page) if next_page else render_template('user_acc.html')
                        
                    else:
                        flash('Invalid Credentials','secondary')
                        return render_template('login.html')
                else:
                    return render_template('register.html')
        else:

            return render_template('login.html')
        
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        message = request.form.get('message')

        contact_us = models.Contact(fullname=fullname, email=email, message=message)
        session.add(contact_us)
        session.commit()
        return render_template('index.html')
    else:
        return render_template('contact.html')
    
@app.route('/post/new_post', methods=['GET','POST'])
@login_required
def create_post():
     if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        new_post = models.Post(title=title, posted_date = datetime.datetime.now(), content=content, author = current_user)
        session.add(new_post)
        session.commit()
        return redirect(url_for('index'))
     else:
         return render_template('create_post.html')

@app.route('/post/view_posts')
def posts():
    page = request.args.get('page',1,type=int)
    per_page=2
    start = (page-1)*per_page
    end = start+per_page
    all_posts = session.query(models.Post).all()
    total_pages = (len(all_posts) + per_page -1)//per_page
    posts = all_posts[start:end]
    
    
    return render_template('post.html', posts = posts, total_pages = total_pages, page=page)

@app.route('/post/<int:id>/delete', methods=['POST','GET'])
@login_required
def del_post(id):
    post = session.query(models.Post).get(id)
    print(post.title)
    if post.author != current_user:
        abort(403)
    session.delete(post)
    session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('posts'))

@app.route('/post/<int:id>/update', methods=['GET','POST'])
@login_required
def update_post(id):
    post = session.query(models.Post).filter(models.Post.id==id).first()
   
    if post.author != current_user:
        
        abort(403)   
    else:
        print(post.id)
        if request.method == 'POST':
            title =  request.form.get('title')
            content = request.form.get('content')
            post.title = title
            post.content = content
           
            session.commit()
            flash('Post updated successfully!','success')
            return redirect(url_for('posts'))
        else:
            return render_template('edit_post.html', post=post)
        
@app.route('/create_comment/<post_id>', methods=['GET', 'POST'])
@login_required
def create_comment(post_id):
    if request.method == 'POST':
        text = request.form.get('message')
        if not text:
            flash('Comment cannot be empty', category='error')
        else:
            post = session.query(models.Post).filter(models.Post.id == post_id)
            if post:
                comments = models.Comments(name=current_user.firstname, email=current_user.email, text=text, author = current_user, post_id=post_id)
                session.add(comments)
                session.commit()
                flash('Your comment has been posted successfully', category='success')
            else:
                flash('The post does not exist.')
            return render_template('post.html')
    else:
        return redirect(url_for('posts', post_id=post_id))

@app.route('/view_comment/<post_id>')
@login_required
def view_comment(post_id):
    post = session.query(models.Post).filter(models.Post.id == post_id).first()
    
    comments = session.query(models.Comments).filter(models.Comments.post_id==post_id).first()
    print(comments)
    if not post:
          flash('Post does not exist.')
    else:
        if not comments:
            flash('No comments for this post.')
        else:
            return render_template('view_comment.html',comments=post.comments,post=post)
    return redirect(url_for('post'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/account', methods=['GET','POST'])
@login_required
def reset_password():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        conf_password = request.form.get('conf_password')
        
        if current_user:
            if new_password==conf_password:
                hashed_new_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                current_user.password = hashed_new_password
                session.commit()
                flash('The password is changed successfully!')
            else:
                flash('Difference in two passwords!')
        else:
            flash('The password does not exist!')
    else:
        flash('Something went wrong')
    return render_template('account.html')
    

if __name__ == '__main__':
    app.run(debug=True)