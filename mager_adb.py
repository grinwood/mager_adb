# rainid

import os
import sys
import fnmatch
import subprocess
import shutil
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
print("https://github.com/grinwood/mager_adb")


# cek list device yang terhubung
loop = 8
# Parameterize
path_adb = "D:\\Apps\\codes\\Nox\\bin\\"
path_device = "/sdcard/"
nama_file = 'frida-server'
DOWNLOAD_FOLDER = ''
# Param end.

if os.name == "nt":
    DOWNLOAD_FOLDER = f"{os.getenv('USERPROFILE')}\\Downloads\\"
else:  # PORT: For *Nix systems
    DOWNLOAD_FOLDER = f"{os.getenv('HOME')}/Downloads"


def init():
    # masuk ke path adb.exe tersimpan
    try:
        os.chdir(path_adb)
        print("[*] adb.exe ditemukan di "+path_adb)
    except FileNotFoundError:
        print("[?] adb.exe tidak ditemukan di " +
              path_adb+" periksa adb direktori.")
        sys.exit(1)

    global loop
    devices = os.popen("adb devices").read().split(
        '\n', 1)[1].split("device")[0].strip()
    if devices == '':
        print(
            "[!] Perangkat tidak tersedia. Mohon hubungkan perangkat ke komputer anda.")
        loop = 0
    else:
        print("[*] List Devices", devices)
        loop = 1


def menu():
    print("===============================================================================")
    print("1.Lihat semua apps package yang terinstall")
    print("2.Lihat semua base.apk")
    print("3.Pull base.apk")
    print("4.Push apk")
    print("5.Deploy frida-server")
    print("6.Jalankan frida-server")
    print("7.Hentikan frida-server")
    print("00.exit")


def search(target=None):
    if target == None:
        target = input("[*] Masukan nama apps : ")
    query = os.popen("adb shell pm list packages -f | findstr "+target).read()
    print(query)
    put = input("[*] Extract APK ?(y/n) : ")
    if put == 'y':
        extract(target)


def view_all():
    query = os.popen("adb shell pm list packages -f").read()
    print(query)


def extract(target=None):
    if target == None:
        target = input("[*] Masukan nama apps : ")
    query = os.popen("adb shell pm list packages -f | findstr "+target).read()
    query = query.replace('package:', '')
    x = query.split("\n")
    final = []
    for i in range(len(x)-1):
        final.append(x[i].split(".apk=", 1)[0]+".apk")
    count = 0
    for i in final:
        print('['+str(count)+'] : ', i)
        count += 1
    if len(final) > 1:
        put = input("[*] Pilih apk : ")
    else:
        put = 0
    int(put)
    confirm = input("[*] Extract apk ? (y/n) : ")
    if confirm == 'y':
        query2 = os.popen('adb pull "'+final[int(put)]+'"').read()
        print(query2)
    else:
        print("[*] Perintah Dibatalkan.")


def push(file, path):
    confirm = input("[*] Push "+file+" ke "+path+" ?(y/n) : ")
    if confirm == 'y':
        query = os.popen('adb push "'+os.path.abspath(file)+'" '+path).read()
        print(query)


def download(info):
    print("[*] Downloading frida-server-" +
          info[0]+"-android-"+info[1]+".xz ...")
    url = "https://github.com/frida/frida/releases/download/" + \
        info[0]+"/frida-server-"+info[0]+"-android-"+info[1]+".xz"
    #URL = "https://instagram.com/favicon.ico"
    # try:
    #     response = requests.get(URL)
    #     open(DOWNLOAD_FOLDER+"instagram.ico", "wb").write(response.content)
    #     print(DOWNLOAD_FOLDER)
    # except (e):
    #     print (e)
    # cekfile("instagram.ico")
    if os.path.isfile("frida-server-"+info[0]+"-android-"+info[1]+".xz"):
        print("[*] File frida-server-"+info[0] +
              "-android-"+info[1]+".xz telah didownload.")
    else:
        # Streaming, so we can iterate over the response.
        response = requests.get(url, stream=True)
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte
        progress_bar = tqdm(total=total_size_in_bytes,
                            unit='iB', unit_scale=True)
        with open(DOWNLOAD_FOLDER+"frida-server-"+info[0]+"-android-"+info[1]+".xz", 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print("[!] Download gagal.")
        else:
            print("[*] File frida-server-"+info[0] +
                  "-android-"+info[1]+".xz telah didownload.")


def cekfile(nama_file,dir):
    files = fnmatch.filter(os.listdir(dir), nama_file)
    if len(files) == 0:
        print("[!] File "+nama_file+" tidak ditemukan di "+dir)
        return False
    else:
# print("ada", nama_file)
        return True


def cekfiledevices():
    print("[*] Cek frida-server on devices...")
    query = os.popen(
        'adb shell ls /data/local/tmp | findstr "frida-server"').read()
    if (query.strip('\n') == "frida-server"):
        return True
    else:
        print("[!] File "+nama_file +
              " tidak ditemukan pada devices, harap deploy dahulu")
        return False


def deploy():
    info = []
    if cekfile(nama_file,DOWNLOAD_FOLDER) == False:
        put = input("[*] Download frida-server ?(y/n) : ")
        if put == 'y':
            try:
                p = subprocess.Popen(
                    ['frida'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                query = os.popen('frida --version').read()
                info.append(query.split("\n")[0])
                query = os.popen("adb shell getprop ro.product.cpu.abi").read()
                info.append(query.split("\n")[0].split("-", 1)[0])
                writeable = os.access(DOWNLOAD_FOLDER, os.W_OK)
                if writeable == True:
                    download(info)
                    with lzma.open(DOWNLOAD_FOLDER+"frida-server-"+info[0]+"-android-"+info[1]+".xz") as f, open(DOWNLOAD_FOLDER+nama_file, 'wb') as fout:
                        file_content = f.read()
                        fout.write(file_content)
                    print('[*] File terekstrak dengan nama '+nama_file)
                else:
                    print("[!] Tidak dapat menyimpan file pada folder "+DOWNLOAD_FOLDER +
                          " cek kembali permission write pada folder tersebut.")
            except EOFError:
                print("[!] File yang didownload korup. Hapus file berikut secara manual : frida-server-" +
                      info[0]+"-android-"+info[1]+".xz")
            except FileNotFoundError:
                print(
                    "[!] Frida tidak ditemukan dalam sistem anda. Mohon install frida terlebih dahulu.")
    if cekfile(nama_file,path_adb) == False:
        shutil.copyfile(DOWNLOAD_FOLDER+"frida-server", path_adb+"frida-server")
    else:
        print("[*] File frida-server ditemukan, melakukan push ...")
        push(nama_file, '/data/local/tmp/')
        os.popen('''adb shell "su -c 'chmod 755 /data/local/tmp/frida-server'"''')


def cekrun():
    query = os.popen('adb shell ps | findstr "frida-server"').read()
    if ("frida-server" in query):
        print("[*] frida-server sudah berjalan pada perangkat anda.")
        return True
    else:
        print("[*] frida-server belum berjalan pada perangkat anda.")
        return False


def runfrida():
    global loop
    if (cekrun() == False):
        if cekfiledevices() != False:
            print('[*] Menjalankan frida-server ...')
            p = subprocess.Popen(
                path_adb+'''adb shell "su -c '/data/local/tmp/frida-server & echo "[*] Frida-server berhasil dijalankan." && echo "[!] Akhiri Sesi berikut untuk memulai kembali script. [CTRL+C]" '"''', stdout=subprocess.PIPE, shell=True, universal_newlines=True)
            # out,err = p.communicate()
            # p.wait()
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
            if (cekrun() == True):
                print("[*] Frida-server berhasil dijalankan.")
                print("[!] Akhiri Sesi berikut untuk memulai kembali script. [CTRL+C]")
            else:
                print("[!] Frida-server gagal dijalankan.")

def killfrida():
    if (cekrun() == True):
        print('[*] Menghentikan frida-server ...')
        query = os.popen('adb shell ps | findstr "frida-server"').read().split(" ")
        query = list(filter(None, query))
        # print(query[1])
        p = subprocess.Popen(path_adb+'''adb shell "su -c 'kill -9 '''+query[1]+''''"''', stdout=subprocess.PIPE, shell=True, universal_newlines=True)

def summonmenu():
    try:
        while loop != 0:
            menu()
            put = input("Pilih menu : ")
            if put == "1":
                view_all()
            elif put == "2":
                val = "base.apk"
                search(val)
            elif put == "3":
                extract()
            elif put == "00":
                break
            elif put == "4":
                files = fnmatch.filter(os.listdir(path_adb), "*.apk")
                count = 0
                for i in range(len(files)):
                    print("["+str(count)+"] : ", files[i])
                    count += 1
                put = input("[*] Pilih file : ")
                push(files[int(put)], path_device)
            elif put == "5":
                deploy()
            elif put == "6":
                runfrida()
            elif put == "7":
                killfrida()
            else:
                print("[!] Invalid Menu")
    except IndexError:
        print("[!] Nomor tidak Valid.")
    except ValueError:
        print("[!] Nomor tidak Valid.")
    except KeyboardInterrupt:
        print("[!] Script Berakhir.")


init()
summonmenu()
# download('xxx')
# killfrida()
