from flask import Flask, request, jsonify
from pymongo import MongoClient
import json

app = Flask(__name__)

# Database configuration and connection
def get_config(key):
    config_file = "C:\\Users\\visha\\sna_project\\config.json"
    with open(config_file, "r") as file:
        config = json.loads(file.read())
    return config[key]

connection_string = get_config("mongodb_connection_string")
client = MongoClient(connection_string)
db = client.mystudents
collection = db.students

# Userbase class to interact with the database
class Userbase:
    def add_user_details(self, full_name: str, group_id: int, user_id: int, user_name: str, is_bot: bool, location: str, profile_link: str, phone_number: int, epoctime: int):
        existing_user = collection.find_one({"user_id": user_id})
        group_name = get_config('group_id').get(str(group_id))
        if existing_user:
            try:
                collection.update_one(
                    {"user_id": user_id},
                    {"$set": {f"groups.{group_id}": group_name}}
                )
                print("[*] Data Updated Successfully")
            except Exception as e:
                print(f"[*] Error updating data: {e}")
        else:
            # Insert a new document
            user_data = {
                "id": 1,
                "full_name": full_name,
                "groups": {f"{group_id}": f"{group_name}"},
                "user_id": user_id,
                "user_name": user_name,
                "epoctime": epoctime,
                "is_bot":is_bot,
                "location":location,
                "profile_link": profile_link,
                "phone_number":phone_number
            }
            try:
                ack = collection.insert_one(user_data)
                if ack.acknowledged:
                    print("[*] Data Inserted Successfully")
                else:
                    print("[*] Unable to insert data")
            except Exception as e:
                print(f"[*] Error inserting data: {e}")

    def group_id_get(self, user_name: str):
        try:
            ack = collection.find_one({}, sort=[('_id', -1)])
            groups = ack.get('groups', {})
            last_updated_group = groups.get(max(groups.keys()), None)
            print("[*] Fetched Successfully Data")
            return last_updated_group
        except MongoClient as e:
            print("[*] Error to Fecth data{e}")
    def update_if_triggered(self, user_id):
        try:
            ack = collection.find_one({"user_id":user_id})
            if ack:
                collection.update_one({"user_id":user_id},{"$set":{"triggered":True}})
                print("[*] User triggerd")
            else:
                print("[*] Not triggerd")
        except:
            print("[*] Unable to fetch")

    def only_in_group(self, full_name: str, group_id: int, user_id: int, user_name: str, is_bot: bool, location: str, profile_link: str, phone_number: int, epoctime: int):
        existing_user = collection.find_one({"user_id": user_id})
        group_name = get_config('group_id').get(str(group_id))
        if existing_user:
            try:
                collection.update_one(
                    {"user_id": user_id},
                    {"$set": {f"groups.{group_id}": group_name}}
                )
                print("[*] Data Updated Successfully")
            except Exception as e:
                print(f"[*] Error updating data: {e}")
        else:
            # Insert a new document
            user_data = {
                "id": 1,
                "full_name": full_name,
                "groups": {f"{group_id}": f"{group_name}"},
                "user_id": user_id,
                "user_name": user_name,
                "epoctime": epoctime,
                "triggerd":True,
                "is_bot":is_bot,
                "location":location,
                "profile_link": profile_link,
                "phone_number":phone_number
            }
            try:
                ack = collection.insert_one(user_data)
                if ack.acknowledged:
                    print("[*] Data Inserted Successfully")
                else:
                    print("[*] Unable to insert data")
            except Exception as e:
                print(f"[*] Error inserting data: {e}")

# Flask route for the webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    # Extract the necessary information from the data
    full_name = data.get('full_name')
    group_id = data.get('group_id')
    user_id = data.get('user_id')
    user_name = data.get('user_name')
    is_bot = data.get('is_bot')
    location = data.get('location')
    profile_link = data.get('profile_link')
    phone_number = data.get('phone_number')
    epoctime = data.get('epoctime')

    # Initialize the Userbase class
    userbase = Userbase()

    # Use the methods from the Userbase class to process the data
    if 'triggered' in data:
        userbase.update_if_triggered(user_id)
    else:
        userbase.add_user_details(full_name, group_id, user_id, user_name, is_bot, location, profile_link, phone_number, epoctime)

    # Return a success response
    return jsonify({"message": "Data processed successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
