#!flask/bin/python
from flask import Flask, jsonify
from flask import request
from flask import abort
from flask import make_response
import json
import os
import sys
import createVM
import uuid
import destroy_vm
import subprocess
import settings
settings.init()

app = Flask(__name__)

@app.route("/server/vm/create", methods=['GET'])
def vm_create():
	vm={}
	name=request.args.get('name')
	itype=request.args.get('instance_type')
	img_id=request.args.get('image_id')
	vm['name']=name
	vm['itype']=itype
	vm['img_id']=img_id
	return jsonify(createVM.create_vm(vm)) 

@app.route("/server/vm/query", methods=['GET'])
def query():
    vm={}
    flag=0
    #print settings.vm_list
    vmid=request.args.get('vmid')
    for i in settings.vm_list:
        if i[0]==int(vmid):
            flag=1
            break
    if flag==1:
        vm['vmid']=i[0]
        vm['name']=i[1]
        vm['instance_type']=i[2]
        vm['pmid']=int(i[3])
        return jsonify(vm)
    else:
        return jsonify({"status":0})

@app.route("/server/vm/destroy", methods=['GET'])
def destroy():
	vm={}
	vmid=request.args.get('vmid')
	vm['vmid']=vmid
	return jsonify(destroy_vm.destroyVM(vmid)) 
@app.route("/server/vm/types", methods=['GET'])
def types():
	vMDescFile=open('types')
        Lines=vMDescFile.readlines()
	st=""
	for i in range(0,len(Lines)):
		st=st+Lines[i]
	vm_type=json.loads(st)
	return jsonify(vm_type)

@app.route("/server/pm/list", methods=['GET'])
def list():
    pm=[]
    pmf={}
    count=0
    for i in settings.machines:
        pm.append(count)
        count=count+1
    pmf['pmids']=pm
    return jsonify(pmf)

@app.route("/server/image/list", methods=['GET'])
def image():
    img=[]
    count=1
    for i in settings.images:
        t={}
        t['id']=count
        count=count+1
        x=i[2]
        x=x.split('/')
        x=x[-1]
        x=x.split('.img')
        x=x[0]
        t['name']=x
        img.append(t)
    print settings.images
    return jsonify({'images': img})

@app.route('/server/pm/listvms', methods=['GET'])
def get_pmid():
	pm={}
	pmid=int(request.args.get('pmid'))
	pm['pmid']=pmid
	vm=[]
	vmf={}
	flag=0
	for i in settings.vm_list:
	    if i[3]==int(pmid):
	        flag=1
	        vm.append(i[0])
	vmf['vmids']=vm
	if flag==1:
	    return jsonify(vmf)
	else:
	    return jsonify({"status":0})

@app.route('/server/pm/query', methods=['GET'])
def get_pms():
    pmid=request.args.get('pmid')
    pm={}
    capacity={}
    free={}
    pm['pmid']=int(pmid)
    vm=0
    for i in settings.vm_list:
        if i[3]==int(pmid):
            vm=vm+1
    pm['vms']=vm
    print vm
    print "pmid" + pmid
    user=settings.machines[int(pmid)][0]
    ip_addr=settings.machines[int(pmid)][1]
    cpu=int(subprocess.check_output("ssh " + user + "@" + ip_addr + " nproc" ,shell=True))
    capacity['cpu']=cpu
    print user
    print ip_addr
    print cpu
    ram=(subprocess.check_output("ssh " + user + "@" + ip_addr + " free -m" ,shell=True))
    ram=ram.split("\n")
    ram=ram[1].split()
    total_ram=int(ram[1])
    avail_ram=int(ram[3])
    capacity['ram']=total_ram
    free['ram']=avail_ram
    print total_ram
    print avail_ram
    disk=subprocess.check_output("ssh " + user+"@"+ip_addr+" df -h --total | grep 'total'",shell=True)
    disk=disk.split()
    free_disk=disk[3]
    disk=disk[1]
    free_disk=free_disk.split('G')
    free_disk=int(free_disk[0])
    disk=disk.split('G')
    disk=int(disk[0])
    capacity['disk']=disk
    free['disk']=free_disk
    print disk
    print free_disk
    s=subprocess.check_output("ssh "+user+"@"+ip_addr+" lscpu | grep 'Socket(s)'",shell=True)
    t=subprocess.check_output("ssh "+user+"@"+ip_addr + " lscpu | grep 'Core(s) per socket'",shell=True)
    s=s.split()
    t=t.split()
    s=int(s[1])
    t=int(t[3])
    free_cpu=s*t
    free['cpu']=free_cpu
    pm['capacity']=capacity
    pm['free']=free
    return jsonify(pm)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

def getmachine(filename):
	x=open(filename)
        l=x.readlines()
	for i in l:
		i=i[:-1]
		d=i.split('@')
		d.append(uuid.uuid4())
		settings.machines.append(d)
	#print machines

def getimg(filename):
	x=open(filename)
        l=x.readlines()
	for i in l:
		i=i[:-1]
		t=[]
		d=i.split('@')
		t.append(d[0])
		s=d[1].split(':')
		t.append(s[0])
		t.append(s[1])
		t.append(uuid.uuid4())
		settings.images.append(t)
	#print images
def get_types(vm):
    vMDescFile=open(vm)
    Lines=vMDescFile.readlines()
    st=""
    for i in range(0,len(Lines)):
        st=st+Lines[i]
    settings.vm_type=json.loads(st)
	
	 	
if __name__ == '__main__':
	if len(sys.argv) < 4:
		print "Format: ./script pm_file image_file type_file"
		exit(1)
	global pm
	pm = sys.argv[1]
	global img 
	img = sys.argv[2]
	global vm 
	vm= sys.argv[3]
	#global machines
	#machines=[]
	getmachine(pm)	
	getimg(img)
	get_types(vm)
    	app.run(debug = True)
