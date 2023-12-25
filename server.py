from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/store_data', methods=['POST'])
def store_data():
    try:
        # Get the JSON data from the POST request
        data = request.get_json()

        # Check if the data is empty
        if not data:
            return jsonify({'message': 'No data provided'}), 400

        # Open a text file for writing (you can change the filename as needed)
        with open('stored_data.txt', 'a') as file:
            # Write the JSON data to the file
            file.write(str(data) + '\n')

        return jsonify({'message': 'Data stored successfully'}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='172.17.0.1', debug=True)
