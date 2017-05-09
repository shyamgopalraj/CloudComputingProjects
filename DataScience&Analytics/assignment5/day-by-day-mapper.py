import sys

infile = sys.stdin
next(infile) # skip first line of input file
for line in infile:
    if not line:
        break
    fields = line.split(',')
    splitfieldzero = fields[0].split('T')
    magnitude = fields[4].strip()

    try:
     magnitude = float(magnitude)
    except ValueError:
     continue

    if magnitude > 0 and magnitude <= 2:
     magnitudeRange = "0_2"
    elif magnitude > 2 and magnitude <= 3:
     magnitudeRange = "2_3"
    elif magnitude > 3 and magnitude <= 4:
     magnitudeRange = "3_4"
    elif magnitude > 4 and magnitude <= 5:
     magnitudeRange = "4_5"
    elif magnitude > 5 and magnitude <= 6:
     magnitudeRange = "5_6"
    elif magnitude > 6 and magnitude <= 7:
     magnitudeRange = "6_7"
    elif magnitude > 7 and magnitude <= 8:
     magnitudeRange = "7_8"
    elif magnitude > 8 and magnitude <= 9:
     magnitudeRange = "8_9"

    print '%s\t%s' % (splitfieldzero[0]+":"+ magnitudeRange,1)

