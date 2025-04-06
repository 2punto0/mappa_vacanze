from app import db
from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

class Category(db.Model):
    """A category of Points of Interest (POI)"""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # e.g. huts, trails, etc.
    display_name = Column(String, nullable=False)  # e.g. Mountain Huts, Hiking Trails
    pois = relationship("POI", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category {self.name}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name
        }

class POI(db.Model):
    """Point of Interest model"""
    __tablename__ = 'pois'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    description = Column(String)
    url = Column(String)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category = relationship("Category", back_populates="pois")
    path = Column(JSON, nullable=True)  # For trail paths
    difficulty_rating = Column(Float, default=0)  # Average difficulty rating (1-5)
    rating_count = Column(Integer, default=0)  # Number of ratings submitted
    trail_ratings = relationship("TrailRating", back_populates="poi", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<POI {self.name}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "lat": self.lat,
            "lng": self.lng,
            "description": self.description,
            "url": self.url,
            "path": self.path,
            "difficulty_rating": self.difficulty_rating,
            "rating_count": self.rating_count
        }

class TrailRating(db.Model):
    """Trail difficulty rating model"""
    __tablename__ = 'trail_ratings'
    
    id = Column(Integer, primary_key=True)
    poi_id = Column(Integer, ForeignKey('pois.id'), nullable=False)
    poi = relationship("POI", back_populates="trail_ratings")
    rating = Column(Integer, nullable=False)  # 1-5 rating (1=Easy, 5=Very Difficult)
    comment = Column(String)  # Optional comment
    user_identifier = Column(String)  # Simple identifier to prevent duplicate ratings
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TrailRating {self.id} for POI {self.poi_id}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "poi_id": self.poi_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Airbnb(db.Model):
    """Airbnb listing model"""
    __tablename__ = 'airbnbs'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    price = Column(Integer)  # Price per night
    description = Column(String)
    url = Column(String)
    bedrooms = Column(Integer)
    image_url = Column(String)
    
    def __repr__(self):
        return f"<Airbnb {self.name}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "lat": self.lat,
            "lng": self.lng,
            "price": self.price,
            "description": self.description,
            "url": self.url,
            "bedrooms": self.bedrooms,
            "image_url": self.image_url
        }