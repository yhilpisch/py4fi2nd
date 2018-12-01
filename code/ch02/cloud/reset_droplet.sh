#
# Reset Droplet after
# Python Installation via Miniconda
#
# Python for Finance, 2nd ed.
# (c) Dr. Yves J. Hilpisch
#
# CAUTION
# This might delete also notebooks
# and other files that have been created
# after the Python installtion.
#
rm -rf /root/miniconda3/
rm -rf /root/.jupyter
rm -rf /root/notebook
head -n -2 /root/.bashrc > /root/.bashrc_new
mv /root/.bashrc_new /root/.bashrc
rm install.sh
pkill -f jupyter

# show Jupyter Notebook instances
# jupyter notebook list
# ... or ...
# ps aux | grep 'jupyter'

# kill all Jupyter Notebook instances
# pkill -f jupyter