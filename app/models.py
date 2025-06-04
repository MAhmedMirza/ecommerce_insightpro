from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from . import db

class User(UserMixin, db.Model):
    """User model for SQL Server database"""
    __tablename__ = 'Users'
    
    UserID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50), unique=True, nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(255), nullable=False)
    SignupDate = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_id(self):
        """Override UserMixin.get_id to use UserID instead of id"""
        return str(self.UserID)
    
    def set_password(self, password):
        """Create hashed password"""
        self.PasswordHash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password"""
        return check_password_hash(self.PasswordHash, password)
    
    def __repr__(self):
        return f'<User {self.Username}>'

class PasswordResetToken(db.Model):
    """Password reset token model"""
    __tablename__ = 'PasswordResetTokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=False)
    token = db.Column(db.String(6), nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='reset_tokens')
    
    def is_valid(self):
        """Check if token is valid and not expired"""
        return not self.used and self.expiration > datetime.utcnow()

class UploadedDatasets(db.Model):
    __tablename__ = 'UploadedDatasets'
    
    DatasetID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=False)
    OriginalFileName = db.Column(db.String(255), nullable=False)
    StoredFileName = db.Column(db.String(255), nullable=False)
    UploadDate = db.Column(db.DateTime, default=datetime.utcnow)
    Status = db.Column(db.String(20), default='Uploaded', nullable=False)
    
    user = db.relationship('User', backref='datasets')

class ETLLog(db.Model):
    __tablename__ = 'ETLLogs'
    
    ETLID = db.Column(db.Integer, primary_key=True)
    DatasetID = db.Column(db.Integer, db.ForeignKey('UploadedDatasets.DatasetID'))
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    StartTime = db.Column(db.DateTime, nullable=False)
    EndTime = db.Column(db.DateTime)
    Status = db.Column(db.String(20), nullable=False)  # <-- Here
    ErrorMessage = db.Column(db.Text)


class DimCustomer(db.Model):
    __tablename__ = 'DimCustomers'
    
    CustomerKey = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=False)
    OriginalCustomerID = db.Column(db.String(50), nullable=False)
    City = db.Column(db.String(100))
    FirstPurchaseDate = db.Column(db.Date)
    LastPurchaseDate = db.Column(db.Date)
    TotalPurchases = db.Column(db.Integer)
    TotalSpent = db.Column(db.Float)
    RecencyScore = db.Column(db.Integer)
    FrequencyScore = db.Column(db.Integer)
    MonetaryScore = db.Column(db.Integer)
    RFMScore = db.Column(db.String(3))
    LastRFMUpdate = db.Column(db.DateTime)

    user = db.relationship('User', backref='customers')

class DimProduct(db.Model):
    __tablename__ = 'DimProducts'
    
    ProductKey = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=False)
    OriginalProductID = db.Column(db.String(50), nullable=False)
    ProductName = db.Column(db.String(255))
    Category = db.Column(db.String(100))
    Price = db.Column(db.Float)
    
    user = db.relationship('User', backref='products')

class DimTime(db.Model):
    __tablename__ = 'DimTime'
    
    TimeKey = db.Column(db.Integer, primary_key=True)
    FullDate = db.Column(db.Date, unique=True)
    Day = db.Column(db.Integer)
    Month = db.Column(db.Integer)
    Year = db.Column(db.Integer)
    Quarter = db.Column(db.Integer)
    DayOfWeek = db.Column(db.Integer)
    DayOfYear = db.Column(db.Integer)

class FactSale(db.Model):
    __tablename__ = 'FactSales'
    
    SaleID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=False)
    TimeKey = db.Column(db.Integer, db.ForeignKey('DimTime.TimeKey'))
    CustomerKey = db.Column(db.Integer, db.ForeignKey('DimCustomers.CustomerKey'))
    ProductKey = db.Column(db.Integer, db.ForeignKey('DimProducts.ProductKey'))
    OrderID = db.Column(db.String(50))
    Quantity = db.Column(db.Integer)
    UnitPrice = db.Column(db.Float)
    TotalAmount = db.Column(db.Float)
    
    user = db.relationship('User', backref='sales')
    time = db.relationship('DimTime')
    customer = db.relationship('DimCustomer')
    product = db.relationship('DimProduct')