from flask import Flask, request, Response

app = Flask(__name__)

# Define the path to the output file
output_file = "out.txt"

# Define a function to handle POST requests
@app.route('/', methods=['POST'])
def handle_post_request():
    # Get the data from the POST request
    data = request.data.decode('utf-8')
    
    # Append the data to the output file with a newline
    with open(output_file, 'a') as file:
        file.write(data + '\n')
    
    return Response(status=200)

# Define a function to handle GET requests
@app.route('/', methods=['GET'])
def handle_get_request():
    # Read the contents of the output file and send as a response
    try:
        with open(output_file, 'r') as file:
            content = file.read()
        return Response(content, status=200, content_type='text/plain')
    except FileNotFoundError:
        return "File not found", 404

if __name__ == '__main__':
    app.run(host='172.17.0.1', debug=True)
