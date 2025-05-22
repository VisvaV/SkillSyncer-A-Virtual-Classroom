class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:visva2005@localhost:3306/skillsyncer'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key for session management
    SECRET_KEY = 'visva2005'

    # Upload folder for file uploads (if needed)
    UPLOAD_FOLDER = 'uploads'