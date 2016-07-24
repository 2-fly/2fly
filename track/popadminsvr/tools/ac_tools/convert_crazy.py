import sys

def toCharCode(s):
     encode = ','.join([str(ord(s[i])) for i in xrange(len(s))])
     return encode

def encode_js(page_str):
     encode = toCharCode(page_str)
     s = "var s = String.fromCharCode(%s)\n" % (encode)
     page_str = "eval(s)"
     return [s, page_str]


def convert(input_file, output_file, camp_url, img_url):
    f = open(input_file, "r")
    js = f.read()
    f.close()
    js = js.replace('${cpurl}', camp_url)
    js = js.replace('${imgurl}', img_url)


    f = open(output_file, "w")
    new_js = encode_js(js)
    f.writelines(new_js)
    f.close()


if len(sys.argv) < 3:
    print 'usage: %s campaign_url image_url'%sys.argv[0]
    exit(-1)

input_file_name = '.pop_crazy.js'
output_file_name = input_file_name.strip('.') + '.output'
cpurl = sys.argv[1]
imgurl = sys.argv[2]
parts = cpurl.split('?')
if len(parts) > 1:
    cpurl = parts[0]

print "campaign url: ", cpurl
print "output file: ", output_file_name
convert(input_file_name, output_file_name, cpurl, imgurl)

