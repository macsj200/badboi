import csv, sys

bad = sys.argv[1]
with open('data.csv') as input_file:
    input_reader = csv.reader(input_file)
    with open('clean.csv', 'w') as output_file:
        output_writer = csv.writer(output_file)
        for row in input_reader:
            if bad in row:
                continue
            output_writer.writerow(row)
