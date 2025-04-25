"""
User Data Management System using MongoDB and Python
"""
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables (for MongoDB connection string)
load_dotenv()

class UserDataSystem:
    def __init__(self, connection_string=None, db_name="user_management"):
        """
        Initialize the User Data System with MongoDB connection
        
        Args:
            connection_string (str): MongoDB connection string
            db_name (str): Name of the database
        """
        # Use provided connection string or get from environment variable
        if connection_string is None:
            connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        
        # Connect to MongoDB
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.users = self.db.users
        
        # Create indexes for faster queries
        self.users.create_index("profession")
        self.users.create_index("isAdvertiser")
    
    def add_user(self, name, address, profession, is_advertiser):
        """
        Add a new user to the database
        
        Args:
            name (str): User's name
            address (str): User's address
            profession (str): User's profession
            is_advertiser (bool): True if advertising services, False if looking for services
            
        Returns:
            str: ID of the newly created user
        """
        user_data = {
            "name": name,
            "address": address, 
            "profession": profession,
            "isAdvertiser": is_advertiser
        }
        
        result = self.users.insert_one(user_data)
        return str(result.inserted_id)
    
    def get_user_by_id(self, user_id):
        """
        Retrieve a user by their ID
        
        Args:
            user_id (str): The user's ID
            
        Returns:
            dict: User data or None if not found
        """
        try:
            user = self.users.find_one({"_id": ObjectId(user_id)})
            if user:
                user["_id"] = str(user["_id"])  # Convert ObjectId to string
            return user
        except:
            return None
    
    def get_all_users(self):
        """
        Get all users in the database
        
        Returns:
            list: List of all users
        """
        users_list = list(self.users.find())
        # Convert ObjectId to string for each user
        for user in users_list:
            user["_id"] = str(user["_id"])
        return users_list
    
    def update_user(self, user_id, updated_info):
        """
        Update user information
        
        Args:
            user_id (str): ID of the user to update
            updated_info (dict): Dictionary with fields to update
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            result = self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": updated_info}
            )
            return result.modified_count > 0
        except:
            return False
    
    def delete_user(self, user_id):
        """
        Delete a user from the database
        
        Args:
            user_id (str): ID of the user to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            result = self.users.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def find_by_profession(self, profession):
        """
        Find users by profession
        
        Args:
            profession (str): Profession to search for
            
        Returns:
            list: List of users with the specified profession
        """
        # Use regex for case-insensitive search
        users_list = list(self.users.find(
            {"profession": {"$regex": f"^{profession}$", "$options": "i"}}
        ))
        # Convert ObjectId to string for each user
        for user in users_list:
            user["_id"] = str(user["_id"])
        return users_list
    
    def find_by_role(self, is_advertiser):
        """
        Find users by their role (advertiser or seeker)
        
        Args:
            is_advertiser (bool): True for advertisers, False for seekers
            
        Returns:
            list: List of users with the specified role
        """
        users_list = list(self.users.find({"isAdvertiser": is_advertiser}))
        # Convert ObjectId to string for each user
        for user in users_list:
            user["_id"] = str(user["_id"])
        return users_list
    
    def match_professionals(self):
        """
        Match seekers with advertising professionals based on profession
        
        Returns:
            list: List of matches with seeker and available professionals
        """
        seekers = self.find_by_role(False)
        matches = []
        
        for seeker in seekers:
            # Find professionals with matching profession
            professionals = list(self.users.find({
                "profession": {"$regex": f"^{seeker['profession']}$", "$options": "i"},
                "isAdvertiser": True
            }))
            
            # Convert ObjectId to string for each professional
            for prof in professionals:
                prof["_id"] = str(prof["_id"])
            
            if professionals:
                matches.append({
                    "seeker": seeker,
                    "available_professionals": professionals
                })
        
        return matches
    
    def close_connection(self):
        """Close the MongoDB connection"""
        self.client.close()


# Example usage
def demonstrate_usage():
    """Demonstrate how to use the UserDataSystem class"""
    system = UserDataSystem()
    
    # Add sample users
    john_id = system.add_user("John Smith", "123 Main St, Boston, MA", "Plumber", True)
    jane_id = system.add_user("Jane Doe", "456 Oak Ave, Chicago, IL", "Electrician", True)
    bob_id = system.add_user("Bob Johnson", "789 Pine Rd, New York, NY", "Plumber", False)
    sarah_id = system.add_user("Sarah Wilson", "101 Maple Dr, Seattle, WA", "Electrician", False)
    
    print("All users:")
    all_users = system.get_all_users()
    for user in all_users:
        print(f"ID: {user['_id']}, Name: {user['name']}, Profession: {user['profession']}")
    
    print("\nAll plumbers:")
    plumbers = system.find_by_profession("Plumber")
    for plumber in plumbers:
        role = "Advertiser" if plumber["isAdvertiser"] else "Seeker"
        print(f"Name: {plumber['name']}, Role: {role}")
    
    print("\nMatches between seekers and professionals:")
    matches = system.match_professionals()
    for match in matches:
        seeker = match["seeker"]
        professionals = match["available_professionals"]
        print(f"Seeker {seeker['name']} needs a {seeker['profession']}")
        print(f"Available professionals: {', '.join([p['name'] for p in professionals])}")
    
    # Update a user
    system.update_user(john_id, {"address": "999 New Address, Boston, MA"})
    updated_john = system.get_user_by_id(john_id)
    print(f"\nUpdated user {john_id}:")
    print(f"Name: {updated_john['name']}, Address: {updated_john['address']}")
    
    # Delete a user
    system.delete_user(jane_id)
    print("\nAll users after deletion:")
    remaining_users = system.get_all_users()
    for user in remaining_users:
        print(f"ID: {user['_id']}, Name: {user['name']}")
    
    # Close the MongoDB connection
    system.close_connection()


if __name__ == "__main__":
    # Run the demonstration (uncomment to execute)
    # demonstrate_usage()
    
    print("User Data Management System is ready to use.")
    print("To use this system, import the UserDataSystem class into your application.")