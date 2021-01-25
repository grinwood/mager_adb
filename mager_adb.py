#rianid

import os
import fnmatch
import subprocess
#import pycurl
import requests
from tqdm import tqdm
import lzma
print("""
 +-+-+-+-+-+ +-+-+-+
 |M|a|g|e|r| |A|D|B|
 +-+-+-+-+-+ +-+-+-+
""")
print("""      |\      _,,,---,,_
ZZZzz /,`.-'`'    -.  ;-;;,_
     |,4-  ) )-,_. ,\ (  `'-'
    '---''(_/--'  `-'\_)""")
print("alamat github @rianid")
#masuk ke path adb.exe tersimpan
try:
## Parameterize

	path_adb = "D:\\mobileutil\\platform-tools\\"
	path_device = "/sdcard/"
	nama_file = 'frida-server'

## Param end.
	print("[*] adb.exe ditemukan di "+path_adb)
	os.chdir(path_adb)
except FileNotFoundError:
	print("[?] adb.exe tidak ditemukan di "+path_adb+" periksa adb direktori.")

#cek list device yang terhubung
loop = 8
def init() :
	global loop
	devices = os.popen("adb devices").read().split('\n', 1)[1].split("device")[0].strip()
	print("[*] List Devices")
	if devices =='' :
		print("[!] Perangkat tidak tersedia. Mohon hubungkan perangkat ke komputer anda.")
		loop = 0
	else :
		print(devices)
		#print("[*] Mencoba terhubung dengan "+devices)
		#connect = os.popen("adb connect " + devices ).read()
		#print("[*] "+connect)
		loop = 1

init()

def menu() :
	print("===============================================================================")
	print("1.Lihat semua apps package yang terinstall")
	print("2.Lihat semua base.apk")
	print("3.Pull apk")
	print("4.Push apk")
	print("5.Deploy frida-server")
	print("6.Jalankan frida-server")
	print("00.exit")
def search(target=None) :
	if target == None :
		target = input("[*] Masukan nama apps : ")
	query = os.popen("adb shell pm list packages -f | findstr "+target).read()
	print(query)
	put = input("[*] Extract APK ?(y/n) : ")
	if put =='y' :
		extract(target)
def view_all() :
	query = os.popen("adb shell pm list packages -f").read()
	print(query)
def extract(target=None) :
	if target == None :
		target = input("[*] Masukan nama apps : ")
	query = os.popen("adb shell pm list packages -f | findstr "+target).read()
	query = query.replace('package:','')
	x = query.split("\n")
	final = []
	for i in range(len(x)-1) :
		final.append(x[i].split(".apk=",1)[0]+".apk")
	count = 0
	for i in final :
		print('['+str(count)+'] : ',i)
		count+=1
	if len(final) > 1 :
		put = input("[*] Pilih apk : ")
	else :
		put = 0
	int(put)
	confirm = input("[*] Extract apk ? (y/n) : ")
	if confirm =='y' :
		query2 = os.popen('adb pull "'+final[int(put)]+'"').read()
		print(query2)
	else :
		print("[*] Perintah Dibatalkan.")
def push (file,path) :
	confirm = input("[*] Push "+file+" ke "+path+" ?(y/n) : ")
	if confirm == 'y' :
		query = os.popen('adb push "'+os.path.abspath(file)+'" '+path).read()
		print(query)

def download(info) :
	print("[*] Downloading...")
	url = "https://github.com/frida/frida/releases/download/"+info[0]+"/frida-server-"+info[0]+"-android-"+info[1]+".xz"
	if os.path.isfile("frida-server-"+info[0]+"-android-"+info[1]+".xz") :
		print("[*] File frida-server-"+info[0]+"-android-"+info[1]+".xz telah didownload.")
	else :
	# Streaming, so we can iterate over the response.
		response = requests.get(url, stream=True)
		total_size_in_bytes= int(response.headers.get('content-length', 0))
		block_size = 1024 #1 Kibibyte
		progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
		with open(path_adb+"frida-server-"+info[0]+"-android-"+info[1]+".xz", 'wb') as file:
		    for data in response.iter_content(block_size):
		        progress_bar.update(len(data))
		        file.write(data)
		progress_bar.close()
		if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
		    print("[!] Download gagal.")
		else :
			print("[*] File frida-server-"+info[0]+"-android-"+info[1]+".xz telah didownload.")
def deploy() :
	files = fnmatch.filter(os.listdir(path_adb),nama_file)
	info =[]
	if len(files) == 0 :
		print("[!] File frida-server tidak ditemukan di "+path_adb)
		put = input("[*] Download frida-server ?(y/n) : ")
		if put == 'y' :
			try :
				p = subprocess.Popen(['frida'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				query = os.popen('frida --version').read()
				info.append(query.split("\n")[0])
				query = os.popen("adb shell getprop ro.product.cpu.abi").read()
				info.append(query.split("\n")[0].split("-",1)[0])
				writeable = os.access(path_adb,os.W_OK)
				if writeable == True :
					download(info)
					with lzma.open(path_adb+"frida-server-"+info[0]+"-android-"+info[1]+".xz") as f, open(path_adb+nama_file, 'wb') as fout:
					    file_content = f.read()
					    fout.write(file_content)
					print('[*] File terekstrak dengan nama '+nama_file)
				else :
					print("[!] Tidak dapat menyimpan file pada folder "+path_adb+" cek kembali permission write pada folder tersebut.")
			except EOFError :
				print("[!] File yang didownload korup. Hapus file berikut secara manual : frida-server-"+info[0]+"-android-"+info[1]+".xz")
			except FileNotFoundError :
				print("[!] Frida tidak ditemukan dalam sistem anda. Mohon install frida terlebih dahulu.")
	print("[*] File frida-server ditemukan, melakukan push ...")
	push(nama_file,'/data/local/tmp/')
	os.popen('''adb shell "su -c 'chmod 755 /data/local/tmp/frida-server'"''')

def runfrida():
	global loop
	print('[*] Menjalankan frida-server ...')
	query = os.popen("frida-ps -U | findstr frida-server").read()
	if ("Failed to enumerate processes" in query) == False :
		print("[*] frida-server sudah berjalan pada perangkat anda.")
	else :
		#os.popen('''adb shell "su -c '/data/local/tmp/frida-server &'"''')
		total =path_adb+'''adb.exe shell "su -c '/data/local/tmp/frida-server &'"'''
		p = subprocess.Popen(path_adb+'''adb shell "su -c '/data/local/tmp/frida-server & echo "[*] Frida-server berhasil dijalankan." && echo "[!] Akhiri Sesi berikut untuk memulai kembali script. [CTRL+C]" '"''', stdout=subprocess.PIPE,shell=True,universal_newlines=True)
		#out,err = p.communicate()
		#p.wait()
		while True:
		    output = p.stdout.readline()
		    print(output.strip())
		    # Do something else
		    return_code = p.poll()
		    if return_code is not None:
		        print('RETURN CODE', return_code)
		        # Process has finished, read rest of the output 
		        for output in p.stdout.readlines():
		            print(output.strip())
		        break
		#query = os.popen("frida-ps -U | findstr frida-server").read()
		#print(query)
		#input("tes : ")
		#p.terminate()
		print("[*] Frida-server berhasil dijalankan.")
		print("[!] Akhiri Sesi berikut untuk memulai kembali script. [CTRL+C]")


#deploy()


try :
	while loop !=0 :
		menu()
		put = input("Pilih menu : ")
		if put == "1" :
			view_all()
		elif put == "2" :
			val = "base.apk"
			search(val)
		elif put =="3" :
			extract()
		elif put == "00" :
			break
		elif put =="4" :
			files = fnmatch.filter(os.listdir(path_adb),"*.apk")
			count = 0
			for i in range(len(files)) :
				print("["+str(count)+"] : ",files[i] )
				count += 1
			put = input("[*] Pilih file : ")
			push(files[int(put)],path_device)
		elif put =="5" :
			deploy()
		elif put == "6" :
			runfrida()
		else :
			print("[!] Invalid Menu")
except IndexError:
	print("[!] Nomor tidak Valid.")
except ValueError:
	print("[!] Nomor tidak Valid.")
except KeyboardInterrupt:
	print("[!] Script Berakhir.")
