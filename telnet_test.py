
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
	else:   print('Авторизация прошла успешно')
	return tn
#Активные планы на корзине
def active_ap_on_shelf(tn):
	tn.write(b"\r")
	tn.write(b"en\r")
	tn.write(b"set pagelen 0\r")
	tn.write(b"sh pack state\r")
	tn.write(b"abr\r\r")
	ap = tn.read_until(b"abr").decode('ascii')
	active_ap = re.findall(r'GP8 OLT-+(\d{0,2})',ap)
	return active_ap
#сырой лог с olt с выводом команды sh ont olt-x-y pon
def log_command_pon(tn,active_ap):
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
def ONT_all_serial_namber_on_shelf(tn,active_ap,log_pon):
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
def ONT_all_opticalinfo_on_shelf(tn,active_ap,log_opticalinfo):
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
def sum_of_ONT_on_shelf(tn,active_ap,log_pon):
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
def sum_of_ACTIVE_ONT_on_shelf(tn,active_ap,log_opticalinfo):
	outf = open('Колличество актывных терминалов на OLT.csv','w')
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

user = 'ecelousov'
password = 'egor@1'

tn = telnet(OLT['TTAU-097.OLT-03'],user,password)
active_ap = active_ap_on_shelf(tn)
tn.close()

