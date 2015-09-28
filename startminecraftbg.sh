# Start the Minecraft server in a background Screen session.
# Add this to crontab for automatic start as:
#     @reboot /home/minecraft/minecraft/startminecraftbg.sh
BASE=/home/minecraft/minecraft/
JAVA=/usr/java/jre1.8.0_45/bin/java
cd ${BASE}/server
screen -d -m -S server $JAVA -Xms8G -Xmx8G -jar ../minecraft_server.jar nogui
