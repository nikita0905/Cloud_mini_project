import libvirt
import main
import os
import sys
import uuid
import subprocess
from uuid import uuid4
import settings
settings.init()

def create_xml(hypervisor,vm,uuid,filepath,ram,cpu,emulator,archtype):
	xml = "<domain type='" + hypervisor + "'><name>" + vm + "</name>				\
	      <memory>" + ram + "</memory>\
		<currentMemory>" + ram + "</currentMemory>					\
	      <uuid>" + uuid + "</uuid> \
	      <vcpu>" + cpu + "</vcpu>						\
	      <os>							\
	        <type arch='" + archtype + "' machine='pc'>hvm</type>		\
		<boot dev='hd'/>					\
	      </os>							\
	      <features>						\
	        <acpi/>							\
          	<apic/>							\
	      	<pae/>							\
	      </features>						\
	      <on_poweroff>destroy</on_poweroff>			\
  	      <on_reboot>restart</on_reboot>				\
	      <on_crash>restart</on_crash>				\
	      <devices>							\
	        <disk type='file' device='disk'>			\
		<driver name=" + emulator + " type='raw'/>			\
		<source file='" + filepath + "'/>		\
		<target dev='hda' bus='ide'/>				\
		<address type='drive' controller='0' bus='0' unit='0'/>	\
		</disk>							\
	      </devices>						\
   	      </domain>"
    #print xml
	return xml

def create_vm(specs):
    name=specs["name"]
    inst_type=int(specs["itype"])
    img_id=int(specs['img_id'])
    print img_id
    print settings.images[img_id-1]
    user1=settings.images[img_id-1][0]
    ip1=settings.images[img_id-1][1]
    #print name
    #print inst_type
    #print settings.machines
    #print settings.vm_type
    ram=settings.vm_type['types'][inst_type-1]['ram']
    ram=ram*1024
    vcpu=int(settings.vm_type['types'][inst_type-1]['cpu'])
    print ram
    print vcpu
    count_pm=1
    user=settings.machines[settings.pmid][0]
    ip_addr=settings.machines[settings.pmid][1]
    cpu_avail=int(subprocess.check_output("ssh " + user + "@" + ip_addr + " nproc" ,shell=True))
    print user
    print ip_addr
    print cpu_avail
    avail_ram=(subprocess.check_output("ssh " + user + "@" + ip_addr + " free -m" ,shell=True))
    avail_ram=avail_ram.split("\n")
    avail_ram=avail_ram[1].split()
    avail_ram=int(avail_ram[3])    
    avail_ram = avail_ram * 1024
    print avail_ram

    while(cpu_avail < vcpu or avail_ram < ram):
        x=len(settings.machines)
        settings.pmid=(settings.pmid+1)%x
        count_pm=count_pm+1
        if(count_pm > x):
            return {"Error" : "Can't create VM as all the specifications not met" }
        user=settings.machines[settings.pmid][0]
        ip_addr=settings.machines[settings.pmid][1]
        cpu_avail=int(subprocess.check_output("ssh " + user + "@" + ip_addr + " nproc" ,shell=True))
        free_mem=(subprocess.check_output("ssh " + user + "@" + ip_addr + " free -m" ,shell=True))
        free_mem=free_mem.split("\n")
        free_mem=free_mem[1].split()
        avail_ram=int(free_mem[3])    
        avail_ram = avail_ram * 1024
    
    settings.vmid=settings.vmid+1
    settings.vm_list.append([settings.vmid,str(name),inst_type,settings.pmid])
    uid=str(uuid4())
    print settings.vm_list
    connect=libvirt.open("remote+ssh://"+user+"@"+ip_addr+"/")
    s=connect.getCapabilities()
    emul_path=s.split("emulator>")
    emul_path=emul_path[1].split("<")[0]
    emulator=s.split("<domain type=")
    emulator= emulator[1].split(">")[0]
    archtype=s.split("<arch>")
    archtype=archtype[1].split("<")[0]
    print emul_path
    print emulator
    print archtype
    img_path=settings.images[img_id-1][2]
    print user1
    print ip1
    print img_path
    os.system("scp "+user1+"@"+ip1+":"+img_path+" ~/linux.img")
    filepath="/home/"+user+"/linux.img"
    os.system("scp ~/linux.img "+user+"@"+ip_addr+":"+filepath)
    rs=connect.defineXML(create_xml(connect.getType().lower(),name,uid,filepath,str(ram),str(vcpu),emulator,archtype))
    print rs
    try:
        rs.create()
        return {"vmid": settings.vmid}
    except:
        return {"vmid" : 0 }
