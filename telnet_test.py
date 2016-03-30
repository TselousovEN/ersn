
import time
import telnetlib
import re

OLT =  {'KARA-043.OLT-02':'10.61.207.14',
		'KARA-043.OLT-03':'10.61.207.10',
		'KARA-043.OLT-04':'10.61.207.18',
		'KARA-056.OLT-01':'10.61.207.22',
		'KARA-056.OLT-03':'10.61.207.26',
		'KARA-415.OLT-01':'10.61.208.22',
		'TTAU-091.OLT-01':'10.61.208.50',
		'TTAU-091.OLT-02':'10.61.212.66',
		'TTAU-091.OLT-03':'10.61.212.202',
		'TTAU-097.OLT-01':'10.61.208.46',
		'TTAU-097.OLT-02':'10.61.212.70',
		'TTAU-097.OLT-03':'10.61.212.206',
		'ZHEZ-076.OLT-01':'10.61.208.38',
		'ZHEZ-076.OLT-02':'10.61.212.74',
		'ZHEZ-076.OLT-03':'10.61.212.78'}


#телнетимся на корзину
def telnet (OLT,user,password):
	tn = telnetlib.Telnet(OLT,23,1)
	#Попытка подключиться к корзине
	try:
		tn = telnetlib.Telnet(OLT,23,1)

	except TimeoutError:
		print ('Введен неверный IP адрес')
	#Авторизация 
	tn.read_until(b"user: ")
	tn.write(user.encode('ascii') + b"\r")
	if password:
		tn.read_until(b"pass: ")
		tn.write(password.encode('ascii') + b"\r")
	err = tn.read_until(b"(error)",2)
	if err == b'\r\n(error)':
		print ('Ошибка авторизации')
		print ('Обратитесь к инженерам ЦТПРС')
		tn.close()
	else:   
		print('Авторизация прошла успешно')
	tn.write(b"en\rset pagelen 0\r")
	return tn
#Активные планы на корзине
def active_ap_on_shelf(tn):
	tn.write(b"\r")
	tn.write(b"sh pack state\r")
	tn.write(b"abr\r\r")
	ap = tn.read_until(b"abr").decode('ascii')
	active_ap = re.findall(r'GP8 OLT-+(\d{0,2})',ap)
	return active_ap
#сырой лог с olt с выводом команды sh ont olt-x-y pon
def log_command_pon(active_ap):
	for i in active_ap:
		for j in range(1,9):
			J = str(j)
			tn.write(b"sh ont olt-"+i.encode("utf-8")+b"-"+J.encode("utf-8")+b" pon\r")
	tn.write(b"abt\r\r")
	log_pon = tn.read_until(b"abt").decode('ascii')
	return log_pon
#сыройлог с olt с выводом команды sh ont olt-x-y optical-info
def log_command_opticalinfo(tn,active_ap):
	for i in active_ap:
		for j in range(1,9):
			J = str(j)
			tn.write(b"sh ont olt-"+i.encode("utf-8")+b"-"+J.encode("utf-8")+b" optical-info\r")
	tn.write(b"abt\r\r")
	log_opticalinfo = tn.read_until(b"abt").decode('ascii')
	return log_opticalinfo
#вывод с csv файл всех серийников на корзине
def ONT_all_serial_namber_on_shelf(active_ap,log_pon):
	outf = open('Серийные номера терминалов на OLT.csv','w')
	outf.write(',card,port,ont,s/n,\r')
	for i in active_ap:
		for j in range(1,9):
			J = str(j)
			list_of_ONT = re.findall('ONT-'+i+'-'+J+'-\d{0,2}\s{0,3}ERSN\s\w{0,8}',log_pon)
			for x in list_of_ONT:
				ont =  re.findall('ONT-'+i+'-'+J+'-+(\d{0,2})',x)
				outf.write('ont,'+i+','+ J+','+ont[0]+','+str(x[-8:])+','+'\r')
	outf.close()
#вывод с csv файл все знаяения затухании ont на корзине
def ONT_all_opticalinfo_on_shelf(active_ap,log_opticalinfo):
	outf = open('Оптический сигнал на ont.csv','w')
	outf.write(',card,port,ont,optical-info,\r')
	for i in active_ap:
		for j in range(1,9):
			J = str(j)
			list_of_ONT = re.findall('ONT-'+i+'-'+J+'-\d{0,2}\s{0,3}boase_v20\s{0,8}-\d{0,2}.\d{0,2}',log_opticalinfo)
			for x in list_of_ONT:
				ont =  re.findall('ONT-'+i+'-'+J+'-+(\d{0,2})',x)
				opt = re.findall('ONT-'+i+'-'+J+'-\d{0,2}\s{0,3}boase_v20\s{0,8}(-\d{0,2}.\d{0,2})',x)
				outf.write('ont,'+i+','+ J+','+ont[0]+','+opt[0]+','+'\r')
	outf.close()
#вывод в csv файл колличество ont на корзине по портам и общее
def sum_of_ONT_on_shelf(active_ap,log_pon):
	outf = open('Колличество терминалов на OLT.csv','w')
	outf.write(',card,port,sum,\r')
	sum_of_ONT_total = 0
	for i in active_ap:
		for j in range(1,9):
			J = str(j)
			list_of_ONT = re.findall('ONT-'+i+'-'+J+'-\d{0,2}\s{0,3}(ERSN)',log_pon)
			sum_of_ONT = len(list_of_ONT)
			sum_of_ONT_total += sum_of_ONT
			outf.write('OLT,'+i+','+ J+','+str(sum_of_ONT)+',\r')
			sum_of_ONT = 0
	outf.write('total,,,'+str(sum_of_ONT_total)+',\r')
	outf.close()

#вывод в csv файл колличество АКТИВНЫХ ont на корзине по портам и общее
def sum_of_ACTIVE_ONT_on_shelf(active_ap,log_opticalinfo):
	outf = open('Колличество активных терминалов на OLT.csv','w')
	outf.write(',card,port,sum,\r')
	sum_of_ONT_total = 0
	for i in active_ap:
		for j in range(1,9):
			J = str(j)
			list_of_ONT = re.findall('ONT-'+i+'-'+J+'-\d{0,2}\s{0,3}(boase_v20)',log_opticalinfo)
			sum_of_ONT = len(list_of_ONT)
			sum_of_ONT_total += sum_of_ONT
			outf.write('OLT,'+i+','+ J+','+str(sum_of_ONT)+',\r')
			sum_of_ONT = 0
	outf.write('total,,,'+str(sum_of_ONT_total)+',\r')
	outf.close()


def log_alarm (tn):
	tn.write(b"msg query send  all\r")
	tn.write(b"abt\r\r")
	alarm = tn.read_until(b"abt").decode('ascii')	
	return (alarm)
#проверка статуса онт
def ont_status (tn,x,y,z):
	tn.write(b"sh ont ont-"+x.encode("utf-8")+b"-"+y.encode("utf-8")+b"-"+z.encode("utf-8")+b" state\r")
	tn.write(b"abt_st\r\r")
	log_status = tn.read_until(b"abt_st").decode('ascii')
	status = re.findall('ONT-'+x+'-'+y+'-'+z+'\s+(\S+)'+'\s+(\S+)',log_status)
	if status[0][0] == 'IS-NR' and status[0][1] == 'ACT':
		print ('активна, БЛЕАТЬ!')
		return True
	elif status[0][0] == 'OOS-AU' and status[0][1] == 'FLT':
		print ('отключена, БЛЕАТЬ!')
		tn.write(b"msg query send  all\r")
		tn.write(b"abt_st1\r\r")
		log_alarm = tn.read_until(b"abt_st1").decode('ascii')
		ont_alarm = re.findall('ONT-'+x+'-'+y+'-'+z+'\s+(\w+)\s+(\d\d/\d\d\s\d\d:\d\d)',log_alarm)
		if ont_alarm[0][0] == 'NTDYGSP':
			print ('по питанию, БЛЕАТЬ! с '+ ont_alarm[0][1])
		elif ont_alarm[0][0] == 'LOS':
			print ('по оптике, БЛЕАТЬ! с '+ ont_alarm[0][1])
		elif ont_alarm[0][0] == 'SUF':
			print ('Хер понять ваще, БЛЕАТЬ! с '+ ont_alarm[0][1])
		return False
	elif status[0][0] == 'OOS-MA' and status[0][1] == 'MT':
		print ('ONT с замочком, БЛЕАТЬ!')
		return False
	elif status[0][0] == 'OOS-AUMA' and status[0][1] == 'UAS':
		print ('ONT не прописана на порту, БЛЕАТЬ!')
		return False
#затуание на онт
def ont_optical_info (tn,x,y,z):
	tn.write(b"\r")
	tn.write(b"sh ont ont-"+x.encode("utf-8")+b"-"+y.encode("utf-8")+b"-"+z.encode("utf-8")+b" optical-info\r")
	tn.write(b"abt_opt\r\r")
	log_optical = tn.read_until(b"abt_opt").decode('ascii')
	optical_ont = re.findall('boase_v20\s+(-\d+.\d+)',log_optical)
	print ('Затухание на ONT = ',optical_ont[0])
	print ('Блеать!')
#прямая линия на онт и серийный номер 
def ont_config (tn,x,y,z):
	tn.write(b"sh ont ont-"+x.encode("utf-8")+b"-"+y.encode("utf-8")+b"-"+z.encode("utf-8")+b" config\r")
	tn.write(b"abt_conf\r\r")
	conf = tn.read_until(b"abt_conf").decode('ascii')
	sn = re.findall('Serial #\s+\|\s(\w+)',conf)
	vpl = re.findall('DHCP-INVENTORY\s+\|\s(\w+)',conf)
	print ('ВПЛ = ',vpl[0][3:])
	print ('серийный номер = ',sn[0])

def ont_software (tn,x,y,z):
	tn.write(b"sh ont ont-"+x.encode("utf-8")+b"-"+y.encode("utf-8")+b"-"+z.encode("utf-8")+b" software\r")
	tn.write(b"abt_soft\r\r")
	log_soft = tn.read_until(b"abt_soft").decode('ascii')
	soft = re.findall('CAV\s(\S+)',log_soft)
	print('ПО = ',soft[0])

def ont_crs (tn,x,y,z):
	tn.write(b"sh crs gem ont-"+x.encode("utf-8")+b"-"+y.encode("utf-8")+b"-"+z.encode("utf-8")+b"\r")
	tn.write(b"abt_crs\r\r")
	log_crs = tn.read_until(b"abt_crs").decode('ascii')
	crs = re.findall('GSX-\d-B1\s+(\d+)\sA\s(\d+)\sR\s(\d+)\s+(\w+)',log_crs)
	print ("На ONT",len(crs),"сервесов:",sep = ' ')
	for i in crs:
		if i[1] == '40':
			print ('ID NET | GEM =',i[0],'; flow =',i[3])
			try:
				tn.write(b"sh svc flow "+i[3].encode("utf-8")+b"\r")
				tn.write(b"abt_40\r\r")
				log_idnet = tn.read_until(b"abt_40").decode('ascii')
				mac_inet = re.findall('MAC\s+(\S+)',log_idnet)
				ip_inet = re.findall('IP\s+(\S+)',log_idnet)
				lease_inet = re.findall('LEASE\s+(\d+)',log_idnet)
				print ('mac =',mac_inet[0],'\r\nIP =',ip_inet[0],'\r\nlease time =',lease_inet[0],'min')
			except IndexError:
				print('ЕПТЬ! не работает')
		elif i[1] == '41':
			print ('SIP DKP | GEM =',i[0],'| flow =',i[3])
		elif i[1] == '42':
			print ('ID TV | GEM =',i[0],'| flow =',i[3])
		elif i[1] == '43':
			print ('SIP ODT | GEM =',i[0],'| flow =',i[3])
		else:
			print ('ХЗ чё с vlan -',i[1],'| GEM =',i[0],'| flow =',i[3])

user = 'ecelousov'
password = 'egor@1'

tn = telnet(OLT['KARA-043.OLT-02'],user,password)
x,y,z = '3','7','1'


status_ont = ont_status (tn,x,y,z)
if status_ont == True:
	ont_config (tn,x,y,z)
	ont_software (tn,x,y,z)
	ont_optical_info (tn,x,y,z)
	ont_crs (tn,x,y,z)

tn.close()

