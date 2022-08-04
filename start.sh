echo "WSL IP address: "
echo "Connect with IP:" 

ip addr show eth0 | grep inet | awk '{print $2}' | sed 's/\/[0-9]\+//'

echo "and port number:\n8000\n\n"

uvicorn main:app --reload