import libvirt
import createVM
import main
import os
import sys
import settings
settings.init()

def destroyVM(vmid):
    print vmid
    try:
        num=0
        for i in settings.vm_list:
            if i[0]==int(vmid):
                break
            num=num+1
        pmid=i[3]
        name=str(i[1])
        username=settings.machines[pmid][0]
        ip_addr=settings.machines[pmid][1]
        print username
        print ip_addr
        connect =libvirt.open("remote+ssh://"+username+"@"+ip_addr+"/")
        rs=connect.lookupByName(name)
        if rs.isActive():
            rs.destroy()
        rs.undefine()
        del settings.vm_list[int(num)]
        return {"status":"1"}
    except:
        return {"status":"0"}

