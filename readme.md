docker build -t mpremote-bridge .
docker run --rm -p 2217:2217 -p 2218:2218 mpremote-bridge