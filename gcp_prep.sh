#!/bin/bash -ex

# Import ova into virtualbox
VBoxManage import ~/Downloads/nim-2.5.20-NIM_VM_v2-5-20-170127_virtualbox.ova

# Change vm network settings to wifi adapter on mac, en0
VBoxManage modifyvm NIM --nic1 bridged --bridgeadapter1 en0

# Start the vm
VBoxManage startvm NIM --type headless

#get vm ip
nim_ip=$(vboxmanage guestproperty get "NIM" "/VirtualBox/GuestInfo/Net/0/V4/IP" | awk '{ print $2 }')

while [ "$nim_ip" == "value" ]; do
    #nim_ip=$(vboxmanage guestproperty get "NIM" "/VirtualBox/GuestInfo/Net/0/V4/IP" | awk '{ print $2 }')
    
    until [ $nim_ip != "value" ]; do
        sleep 5
        echo "Trying again..."
        nim_ip=$(vboxmanage guestproperty get "NIM" "/VirtualBox/GuestInfo/Net/0/V4/IP" | awk '{ print $2 }')
    done
done

printf "NIM's IP: $nim_ip\n"


function edit_grub() {
    # backup grub file
    sudo cp -v /etc/default/grub /etc/default/grub.bk

    # grub requirements from google docs. https://cloud.google.com/compute/docs/images/import-existing-image
    # edit file
    sudo sed -i -e '/splashimage=/d' \
    -e '/rhgb/d' \
    -e '/quiet/d' \
    -e '/#GRUB_TERMINAL=console/a console=ttyS0,38400n8d' /etc/default/grub
    
    #regenerate grub.cfg
    sudo update-grub
}

# ssh into vm and edit the grub file
function ssh_nim() {
    ssh -t nim@$nim_ip "$(declare -f); edit_grub"
}
eval ssh_nim

# Convert ova to raw
VBoxManage controlvm NIM acpipowerbutton
VBoxManage clonehd NIM \
    ~/disk.raw --format RAW
sudo tar -Sczf ~/compressed-image.tar.gz ~/disk.raw
