cp /home/dxflearn/config/celeyd /etc/init.d/
cp /home/dxflearn/config/defaultcelery /etc/default/
mv /etc/default/defaultcelery /etc/default/celeyd
/etc/init.d/celeyd start