# Makefile

# Define the Python script and output YAML file
PYTHON_SCRIPT = create_template.py
OUTPUT_FILE = template.yaml

# Default target: Run the Python script and Docker command
all: run_script run_docker

# Target to run the Python script
run_script:
	python3 $(PYTHON_SCRIPT)

# Target to run the Docker command
run_docker:
	#FIXME first line does not fucking work, it keeps asking me for a device position
	#docker run --rm --privileged -v "${PWD}":/config --device=/dev/ttyUSB0 -it ghcr.io/esphome/esphome run $(OUTPUT_FILE) --device /dev/ttyUSB0
	docker run --rm --privileged -v "${PWD}":/config --device=/dev/ttyUSB0 -it ghcr.io/esphome/esphome run $(OUTPUT_FILE)

# Clean target (optional): removes the generated YAML file
clean:
	rm -f $(OUTPUT_FILE)
