from flask import Flask
from flask import session, url_for, request, send_from_directory
from flask import render_template
from flask_uploads import UploadSet,IMAGES,configure_uploads

import json
from markupsafe import escape
from datetime import datetime

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField
app = Flask(__name__)

app.secret_key = b'a9f3a1d21348821a88243c4ac70a7a571ee30bd58617fabdacb7966f916ddf05'
app.config['UPLOADED_PHOTOS_DEST'] = 'static'

photos = UploadSet('photos',IMAGES)

configure_uploads(app,photos)

class UploadForm(FlaskForm):
    """Form for uploading images to comments.
    
    Attributes:
        photo: FileField that accepts only image files.
        submit: Submit button for the form.
    """

    photo = FileField(
        validators = [
            FileAllowed(photos, 'Only images allowed!')
        ]
    )
    submit = SubmitField('Upload')

app_name = "Web Comment Board"

message_data_file = "message-data.json"
message_template = "web-comment-page-tmpl.html"

def updatedata(data_list,new_data):
    """Append new comment data to the existing data list.
    
    Args:
        data_list: List of existing comment dictionaries.
        new_data: Dictionary containing new comment data to append.
        
    Returns:
        None (modifies data_list in place).
    """
    return data_list.append(new_data)

def save_comment(invobj,file):
    """Save comment data to a JSON file.
    
    Args:
        invobj: List or dictionary object containing comment data to save.
        file: String path to the JSON file where data will be saved.
        
    Returns:
        Result of json.dump operation.
    """
    with open(file, "w") as fileobj:
        return json.dump(invobj,fileobj,indent=3)

def load_comments(file):
    """Load comment data from a JSON file.
    
    Args:
        file: String path to the JSON file containing comment data.
        
    Returns:
        List of comment dictionaries loaded from the file.
    """
    with open(file, "r") as fileobj:
        return json.load(fileobj)

@app.route('/search',methods=['POST'])
def Search():
    """Handle comment search requests.
    
    Form parameters:
        searchstr: Text to search for in comment hashtags.
        authorname: Author username to filter by.
        
    Returns:
        HTML string containing search results page with matching comments
        and a search form.
    """

    searchstr = str(request.form.get("searchstr",""))
    auhtorstr = str(request.form.get("authorname",""))

    website_url = url_for("website")

    comment_data = load_comments(message_data_file)

    founddata=[]
    founddatahtml = ""

    for comment in comment_data:
        if searchstr in comment["hashtags"] and auhtorstr in comment["username"]:
            founddata.append(comment)
    if founddata != "":
    #Making the html structure for the comments searched
        for comment in founddata:
            founddatahtml += f"""
            <div style="display: flex; column-gap: 10px;">
                <div class="left-info" style="border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; border-radius: 8px;">
        """
            
            if comment.get("image"):
                founddatahtml += f"""
                    <div>
                        <img src="{comment['image']}" style="width: 400px;">
                    </div>
        """
            
            founddatahtml += f"""
                    <div class="comment" style="display: flex; column-gap: 30px;">
                        <div class="left-info" style="width: 200px;">
                            <div class="username"><b>{comment["username"]}</b></div>
                            <div style="color:gray" class="timestamp">{comment["time"]}</div>
                        </div>
                        <div class="right-content">
                            <div class="comment-text">{comment["comment"]}</div>
                            <div style="color:blue" class="hashtags">{comment["hashtags"]}</div>
                        </div>
                        <div style="color: red;">
                            <p>REPLY</p>
                        </div>
                    </div>
                </div>
            </div>
        """

        return """
    <!doctype html>
    <html>
    <h1>Search results for '""" + searchstr + """'</h1>

    <p>""" + founddatahtml + """</p>

    <h2>Search Comments:</h2>
    <div>
        <form method="POST" action='/search'> 
            <div style="display: flex; margin: 0px;">
                <label style="width: 100px;">Enter Text:</label>
                <input type="text" name="searchstr">
            </div>
            <div style="display: flex; margin: 0px;">
                <label style="width: 100px;">Author:</label>
                <input type="text" name="authorname">
            </div>

            <input style="background:silver; border-radius: 8px;" type="submit" value="Search">
        </form>
    </div>

    <p><a href=""" + website_url + """>Back to the main page</a></p>

    </html>
    """

@app.route('/static/<filename>')
def get_file(filename):
    """Serve uploaded image files from the static directory.
    
    Args:
        filename: Name of the file to retrieve from the uploads directory.
        
    Returns:
        File response for the requested image.
    """
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)

@app.route('/',methods = ['GET','POST'])
def website():
    """Main comment board page route handler.


    account: Username for the current session (optional).
        
    Form parameters (POST):
        account: Username of the comment author.
        hashtags: Hashtags associated with the comment.
        comments: The comment text content.
        photo: Optional image file upload.
        
    Returns:
        Rendered HTML template displaying the comment form and all existing comments.
    """
    
    account_name = request.args.get("account","")
    if not account_name:
        account_name = session.get("account","default")

    form = UploadForm()
    comment_data = load_comments(message_data_file)

    if request.method == 'POST':
        account_name = request.form.get("account", "default")
        hashtags = request.form.get("hashtags", "")
        comments = request.form.get("comments", "Post a comment...")
        time = datetime.now().strftime("%m/%d/%Y %H:%M %p")

        filename = ""
        if form.validate_on_submit():
            filename = photos.save(form.photo.data)
            file_url = url_for('get_file',filename=filename)


        new_comment = {
            "username" : account_name,
            "time" : time,
            "hashtags" : hashtags,
            "comment" : comments,
            "image" : file_url
        }

        updatedata(comment_data,new_comment)
        save_comment(comment_data,message_data_file)


    else:
        account_name = "default"
        hashtags = ""
        comments = ""
        file_url = ""

    html_reply = render_template(message_template,acc_name = account_name,application_name = app_name,
                                comm_data=comment_data,hasht=hashtags,comms = comments,file_url = file_url,form = form)

    return html_reply