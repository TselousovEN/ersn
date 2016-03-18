import re

s = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15']

with open ('log_for_cli.txt','r') as infail:
    ActiveAPonShelf = infail.read()

for i in s:
    for j in range(1,9):
        SumONTforPON = re.findall(r'ONT-'+i,ActiveAPonShelf)
        print ('OLT-',i,j)+':'+len(SumONTforPON))
