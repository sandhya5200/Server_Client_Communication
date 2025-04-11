import socket                  
import io                     
from PIL import Image          
import psycopg2               


conn = psycopg2.connect(      #db connection                                                                      
    dbname="photos", 
    user="postgres", 
    password="thrymr@123", 
    host="localhost", 
    port="5432"      
)
cursor = conn.cursor()         #cursor for executing SQL queries


server = socket.socket()       # Create a TCP socket object
server.bind(('localhost', 12345))  # binding the server to localhost on port 12345
server.listen()                # Start listening for incoming connections
print("Server is started and listening...")

BUFFER_SIZE = 4096                  #size of each chuck 
END_MARKER = b"%Image completed%"  

while True:
    print("Waiting for client connection...")
    client_socket, address = server.accept()  #accept a new client connection
    print(f"Client connected: {address}")
    
    file_stream = io.BytesIO()          #memory to save the images
    print("Receiving image data...")

    while True:
        recv_data = client_socket.recv(BUFFER_SIZE)  #receive data in chunks
        if END_MARKER in recv_data:             
            file_stream.write(recv_data.replace(END_MARKER, b'')) #check id end marker is there in received data and break and exclude it
            break  
        file_stream.write(recv_data)  

    print("Image received")

    file_stream.seek(0)  # Reset stream position to beginning for reading

    try:
        print('converting to black and white')
        image = Image.open(file_stream).convert('L')
    except Exception as e:
        print(f"Failed to open image: {e}")  
        client_socket.close()  
        continue  

    # Save processed black and white image to database
    bw_stream = io.BytesIO()         # Create a new memory stream for B&W image
    image.save(bw_stream, format='JPEG')  # Save image in JPEG format to stream
    bw_data = bw_stream.getvalue()   # Get raw byte data from stream

    # print(bw_data)                   #print binary data


    cursor.execute("INSERT INTO bw_images (image_data) VALUES (%s)", (psycopg2.Binary(bw_data),))  #insert image as binary into PostgreSQL
    conn.commit()  
    print("Image saved to database.")


    decision = client_socket.recv(BUFFER_SIZE).decode().strip().lower()
    if decision == 'yes':
        print("client has requested to see the image ,retrieving from database")

        cursor.execute("SELECT image_data FROM bw_images ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()

        if result:
            image_data = result[0]   # extract the BYTEA image data from the fetched row
            response_stream = io.BytesIO(image_data)  #create an im-memmory byte stream
            response_stream.seek(0) # Reset the stream to the beginning before sending

            print("sending b/w image to the client")
            while chunk := response_stream.read(BUFFER_SIZE):
                client_socket.send(chunk)
            client_socket.send(END_MARKER)
            print("Image sent back to client successfully.")
        else:
            print("No image found in database.")
    else:
        print("client chose not to receive image.")

    client_socket.close()
    print("Client connection closed.\n")


    import socket                    
import io                       
from PIL import Image           

client = socket.socket()         # Create a TCP socket object
client.connect(('localhost', 12345))  # Connect to server on localhost and port 12345
print("Client is ready")

BUFFER_SIZE = 4096              
END_MARKER = b"%Image completed%"  

print("Opening image file to send to the server")
with open('/home/thrymr/Downloads/apple.jpeg', 'rb') as file:  
    while chunk := file.read(BUFFER_SIZE):  # Read image file in chunks
        client.send(chunk)                  # Send each chunk to the server

client.send(END_MARKER)           # Send end marker to indicate image sending is complete
print("Image sent.")


choice = input("Do you want to see the image? (yes/no): ").strip().lower()
client.send(choice.encode())      # Send user's decision to the server

if choice == 'yes':
    response_buffer = io.BytesIO()  # Create a buffer to hold the incoming image data
    print("waiting to receive black and white image from server")
    while True:
        recv_data = client.recv(BUFFER_SIZE)  # Receive data in chunks
        if END_MARKER in recv_data:          
            response_buffer.write(recv_data.replace(END_MARKER, b''))  
            break
        response_buffer.write(recv_data)    

    response_buffer.seek(0)                   
    received_image = Image.open(response_buffer)  # Load image from buffer
    output_path = '/home/thrymr/Downloads/received_image.jpeg'  # File path to save received image
    received_image.save(output_path)          # Save image to local storage
    print(f"Received image saved at: {output_path}")
else:
    print("Chose not to receive image.")       

client.close()                               
print("Connection closed")

