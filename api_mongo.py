from flask import Flask, jsonify, request,render_template
from pymongo import MongoClient
from bson import ObjectId


url = "mongodb+srv://Elodie:1234@cluster0.nj6scgk.mongodb.net/test?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(url)

db = client["critere_hotel"]
mycollection = db['hotel']
update_collection= db['update']

data = {
    "Hotel Names": "ESMT",
    "Star Rating": "None",
    "Rating": "None",
    "Free Parking": "Yes",
    "Fitness Centre": "No",
    "Spa and Wellness Centre": "No",
    "Airport Shuttle": "Yes",
    "Staff": "None",
    "Facilities": "None",
    "Location": "None",
    "Comfort": "None",
    "Cleanliness": "None",
    "Price Per Day($)": 136
}
new_hotel = {
    "Hotel Names": "Vicky’s Corner",
    "Star Rating": "None",
    "Rating": "None",
    "Free Parking": "Yes",
    "Fitness Centre": "No",
    "Spa and Wellness Centre": "No",
    "Airport Shuttle": "Yes",
    "Staff": "None",
    "Facilities": "None",
    "Location": "None",
    "Comfort": "None",
    "Cleanliness": "None",
    "Price Per Day($)": 136
}


app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome!!! Let's show you our different Hotels"

# Méthode GET

#Hotel par nombre d'etoile
@app.route('/hotel/<int:StarRating>', methods=['GET'])
def hotel_by_star_rating(StarRating):
    hotels = mycollection.find({"Star Rating": StarRating})
    hotel_list = []
    
    for hotel in hotels:
        hotel['_id'] = str(hotel['_id'])  
        hotel_list.append(hotel)
    
    return jsonify(hotel_list)


#tous les hotels

@app.route('/hotel', methods=['GET'])
def distinct_hotel_names():
    distinct_names = mycollection.distinct("Hotel Names")
    
    return jsonify(distinct_names)




#Hotel par prix journalier
@app.route('/hotel/price_per_day/<int:min_price>/<int:max_price>', methods=['GET'])
def hotel_by_price_range(min_price, max_price):
    query = {
        "Price Per Day($)": {"$gte": min_price, "$lte": max_price}
    }
    
    hotels = mycollection.find(query)
    hotel_list = []
    
    for hotel in hotels:
        hotel['_id'] = str(hotel['_id'])
        hotel_list.append(hotel)
    
    return jsonify(hotel_list)


# Tri des hotels par prix
@app.route('/hotel/price', methods=['GET'])
def sort_hotels_by_price():
    pipeline = [
        {
            "$match": {
                "Price Per Day($)": {"$exists": True}
            }
        },
        {
            "$sort": {"Price Per Day($)": 1}
        },
        {
            "$project": {
                "_id": 0,
                "Hotel Name": "$Hotel Names",
                "Price Per Day($)": 1
            }
        }
    ]
    
    result = list(mycollection.aggregate(pipeline))
    return jsonify(result)



#Hotel service bien etre
@app.route('/hotel/center/<string:fitness_center>/<string:spa>', methods=['GET'])
def hotel_center(fitness_center, spa):
    query = {
        "Fitness Centre": fitness_center,
        "Spa and Wellness Centre": spa
    }
    
    hotels = mycollection.find(query)
    hotel_list = []
    
    for hotel in hotels:
        hotel['_id'] = str(hotel['_id'])
        hotel_list.append({
            "Hotel Name": hotel["Hotel Names"],
            "Fitness Centre": hotel["Fitness Centre"],
            "Spa and Wellness Centre": hotel["Spa and Wellness Centre"]
        })
    
    return jsonify(hotel_list)



#Nombre d'hotels offrant des services

@app.route('/hotel/count', methods=['GET'])
def count_hotels_with_services():
    pipeline = [
        {
            "$match": {
                "Free Parking": "Yes",
                "Airport Shuttle": "Yes"
            }
        },
        {
            "$group": {
                "_id": None,
                "nbr_hotel": {"$sum": 1}
            }
        }
    ]
    
    result = list(mycollection.aggregate(pipeline))
    
    return jsonify(result)



#service parking

@app.route('/hotel/parkings/<string:airport>/<string:parking>', methods=['GET'])
def hotel_parkings(airport, parking):
    query = {
        "Airport Shuttle": airport,
        "Free Parking": parking
    }
    
    hotels = mycollection.find(query)
    hotel_list = []
    
    for hotel in hotels:
        hotel['_id'] = str(hotel['_id'])
        hotel_list.append({
            "Hotel Name": hotel["Hotel Names"],
            "Airport Shuttle": hotel["Airport Shuttle"],
            "Free Parking": hotel["Free Parking"]
        })
    
    return jsonify(hotel_list)


#Information sur un hotel specifique

@app.route('/hotel/name/<name>', methods=['GET'])
def hotel_by_name(name):
    hotels = mycollection.find({"Hotel Names": name})
    hotel_list = []
    
    for hotel in hotels:
        hotel['_id'] = str(hotel['_id'])
        hotel_list.append(hotel)
    
    return jsonify(hotel_list)


#Confort et prix

@app.route('/hotel/comfort_price/<int:comfort>/<int:price>', methods=['GET'])
def hotels_with_high_confort_low_price(comfort, price):
    query = {
        "Comfort": {"$gt": comfort},
        "Price Per Day($)": {"$lt": price}
    }
    
    hotels = mycollection.find(query)
    hotel_list = []
    
    for hotel in hotels:
        hotel['_id'] = str(hotel['_id'])
        hotel_list.append(hotel)
    
    return jsonify(hotel_list)


#score

@app.route('/hotel/ratings/<int:staff>/<int:facilities>/<int:comfort>', methods=['GET'])
def hotels_with_high_ratings(staff, facilities, comfort):
    query = {
        "Staff": {"$gt": staff},
        "Facilities": {"$gt": facilities},
        "Comfort": {"$gt": comfort}
    }
    
    hotels = mycollection.find(query)
    hotel_list = []
    
    for hotel in hotels:
        hotel['_id'] = str(hotel['_id'])
        hotel_list.append({
            "Hotel Name": hotel["Hotel Names"],
            "Staff": hotel["Staff"],
            "Facilities": hotel["Facilities"],
            "Comfort": hotel["Comfort"]
        })
    
    return jsonify(hotel_list)


    

# Route pour ajouter un nouvel hôtel

@app.route('/hotel/add', methods=['POST'])
def add_hotel():
    result = update_collection.insert_one(new_hotel)
    return jsonify({"message": "Hotel added successfully", "inserted_id": str(result.inserted_id)}), 201


#Update
@app.route('/hotel/update/<id>', methods=['PUT'])
def update_hotel(id):

    result = update_collection.update_one({'_id': ObjectId(id)}, {'$set': data})

    return jsonify({"message": "Hotel update successfully", "updated_id": str(id)}), 200






#DELETE

# Route pour ajouter un nouvel hôtel
@app.route('/hotel/delete/<id>', methods=['DELETE'])
def delete_hotel(id):

    result = update_collection.delete_one({'_id':ObjectId(id)})

    return jsonify({"message": "Hotel deleted successfully", "deleted_id": str(id)}), 200


if __name__ == "__main__":
    app.run(debug=True)
