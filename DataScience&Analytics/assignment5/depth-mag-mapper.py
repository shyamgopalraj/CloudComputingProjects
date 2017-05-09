import sys

infile = sys.stdin
next(infile) # skip first line of input file
for line in infile:
 if not line:
  break
 #print line
 fields = line.split(',')
 depth = fields[3].strip()
 magnitude = fields[4].strip()

 try:
  magnitude = float(magnitude)
  depth = int(depth)
 except ValueError:
  continue

 if depth > -5 and depth <= 95:
     depthRange = "-5-95"
 elif depth > 96 and depth <= 195:
     depthRange = "96-195"
 elif depth > 196 and depth <= 295:
     depthRange = "196-295"
 elif depth > 296 and depth <= 395:
     depthRange = "296-395"
 elif depth > 396 and depth <= 495:
     depthRange = "396-495"
 elif depth > 496 and depth <= 595:
     depthRange = "496-595"
 elif depth > 596 and depth <= 695:
     depthRange = "596-695"

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

 print '%s\t%s' % (depthRange+":"+ magnitudeRange, 1)
     
