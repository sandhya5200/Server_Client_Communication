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

