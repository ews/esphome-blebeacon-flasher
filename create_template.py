import jinja2
import uuid

def number_to_words(n):
    if n < 0 or n > 60:
        return "Number out of range (0-60 only)"


    ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty"]

    if n == 0:
        return "ZERO"
    elif 1 <= n < 10:
        return ones[n]
    elif 10 <= n < 20:
        return teens[n - 10]
    elif 20 <= n <= 60:
        if n % 10 == 0:
            return tens[n // 10]
        else:
            return tens[n // 10] + "-" + ones[n % 10]

# Read the number from 'number.txt' and convert it to an integer
with open('number.txt', 'r') as numberin:
    number = int(numberin.read().strip())

name = number_to_words(number)
my_uuid = str(uuid.uuid4())

data = {'NAME': name, 'UUID': my_uuid}

#tmpl_loader = jinja2.FileSystemLoader(searchpath='.')
#tmpl_env = jinja2.Environment(loader=tmpl_loader)
#template = tmpl_env.get_template('beacon_config_template.yaml')


# Read the template file as a plain text
with open('beacon_config_template.yaml', 'r') as template_file:
    template_text = template_file.read()

# Replace placeholders manually
template_text = template_text.replace("{{ NAME }}", name)
template_text = template_text.replace("{{ UUID }}", my_uuid)

# Write the result to the output file
with open('template.yaml', 'w') as fout:
    fout.write(template_text)




## Write the rendered template to 'template.yaml'
#with open('template.yaml', 'w') as fout:
#    fout.write(template.render(**data))

# Write the number (converted to a string) to 'number.txt'
with open('number.txt', 'w') as numberout:
    numberout.write(str(number+1))

with open('devices.csv', 'a') as devicesout:
     devicesout.write(str(my_uuid)+','+number_to_words(number)+"\n")
