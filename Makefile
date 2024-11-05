# Makefile

# Define the Python script and output YAML file
PYTHON_SCRIPT = create_template.py
OUTPUT_FILE = template.yaml

# Default target: Run the Python script and Docker command
all: run_script run_docker

all_test: run_script_test run_docker

# Target to run the Python script
run_script:
	python3 $(PYTHON_SCRIPT)

run_script_test:
	python3 ${PYTHON_SCRIPT} --test

# Target to run the Docker command
run_docker:
	#docker run --rm --privileged -v "${PWD}":/config  -v "${PWD}/.esphome":/config/.esphome --device=/dev/ttyACM0 -it ghcr.io/esphome/esphome run $(OUTPUT_FILE) --device /dev/ttyACM0
	docker run --rm --privileged -v "${PWD}":/config  --device=/dev/ttyACM0 -it ghcr.io/esphome/esphome run $(OUTPUT_FILE) --device /dev/ttyACM0

# Clean target (optional): removes the generated YAML file
clean:
	rm -f $(OUTPUT_FILE)
