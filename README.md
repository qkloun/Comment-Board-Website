# Web Comment Board

A simple Flask-based web application that allows users to post comments with hashtags and optional images, and search through existing comments.

## Features

- **Post comments** : Users can share comments with a username, hashtags, and optional image uploads
- **Image upload support** : Upload images alongside comments (supports common image formats)
- **Search Comments** : Search comments by hashtags and filter by author username
- **Persistent Storage** : Comments are saved to a JSON file for persistence
- **Simple Layout** : Clean and basic interface for viewing and posting comments

## Requirements

- Python 3
- FLASK
- FLASK WTF
- FLASK-UPLOADS
- WTFORMS


## JSON-file Data Format
```json
{
  "username": "string",
  "time": "MM/DD/YYYY HH:MM AM/PM",
  "hashtags": "string",
  "comment": "string",
  "image": "/static/filename.ext"
}
```

## How to contribute!

You can contribute to this project by adding features such as:
- making the UI better
- Adding a reply function to comments
- Changing the JSON file to a CSV file

## Future enhancements
- Add like/downvote system
- Add pages to comments for better performance
