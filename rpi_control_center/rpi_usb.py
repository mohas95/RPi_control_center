import os, time

def get_devices(mount = False):
    '''
    initiate and return a list of USB_SD objects obtained at the state it was called.
    '''
    storage_devices = []
    devices = os.popen('blkid').readlines()

    for dev_str in devices:
        loc, params = dev_str.split(': ')
        if "/sd" not in loc:
            continue
        device_attrs = {'loc':loc}
        for attr in params.split(' '): device_attrs[attr.split('=')[0]] = attr.split('=')[1].strip('"\n')
        storage_devices.append(USB_SD(attrs = device_attrs, mount=mount))

    return storage_devices

class USB_SD:
    '''
    USB_SD Class takes  a dictionary of device attributes obtained from the linux-based
    command line utility blkid as  a string, and is passed through as a dictionary
    {'loc':'/dev/<dev interface>', ...}. This class has methods for mounting,
    transfering files and unmounting on block usb storage device. Primarily made for the Raspberry pi,
    but can esentially work for any Debian based OS.
    '''
    def __init__(self, attrs, mnt_base_dir = '/mnt/', mount=False):
        '''
        '''
        self.attrs = attrs
        self.loc = attrs['loc']
        self.dev_name = attrs['loc'].split("/")[-1]
        self.mnt = f'{mnt_base_dir}{self.dev_name}'
        if mount:
            self.mnt_usb()
            time.sleep(5)

    def __call__(self, data_file, fldr_name=None):
        '''
        Transfer data_file into fldr_name located in self.mnt directory
        '''
        filename = data_file.split('/')[-1]
        transfer_dir = f'{self.mnt}/{fldr_name}/' if fldr_name else f'{self.mnt}/pi_data/'
        if not os.path.isdir(transfer_dir): os.system(f'sudo mkdir {transfer_dir}')
        os.system(f'sudo cp {data_file} {transfer_dir+filename}')

    def mnt_usb(self):
        '''
        Mount storage device
        '''
        if not os.path.isdir(self.mnt): os.system(f'sudo mkdir {self.mnt}')
        os.system(f'sudo mount {self.loc} {self.mnt}')

        return self.mnt

    def umnt_usb(self):
        '''
        Unmount storage device
        '''
        if not os.path.isdir(self.mnt):
            print(f'{self.mnt}: no mount point exists')
            return None
        os.system(f'sudo umount {self.mnt}')
        os.system(f'sudo rm -d {self.mnt}')

        return True

if __name__ == '__main__':

    storage_devices = get_devices(True)
    print(storage_devices)
    for dev in storage_devices:
        dev('test.txt')
        time.sleep(5)
        os.system(f'sudo ls {dev.mnt}')
        dev.umnt_usb()
        os.system(f'sudo ls /mnt')
