To get started, you need to first set up the Evaluator.
1. You will need at least 3 hosts to run the Evaluator respectively. 
2.Change the host name and host IP in config.py file (in evaluator folder).
3.The key modulus p, generator g are also hardcoded in config file, you can change them accordingly. The private key x and public key y are stored in key*.txt, server_a uses key1.txt, server_b uses key2.txt and server_c uses key3.txt. You can also change the keys.
4.To run the program, you need to have python3 and virtualenv installed.
(1) create a new virtualenv under estimator:
virtualenv –system-site-packages -p python3 .
(2) activate the virtualenv:
source ./bin/activate
(3) install dependencies:
pip3 install -r requirements.txt
(4) Run the program:
python run.py

Then you need to set up Blockchain. 
1. You need at least two hosts to run the blockchain server. 
2. Edit the config.py file under blockchain folder. The “blockchain_address” in the “config.py” file needs to be changed to the “main blockchain IP address” for all blockchain servers. Then change the “CA_address” to one of the Evaluator’s addresses. You can also customize the time to do one mine operation for Blockchain (the default time is 10s).
3. Run blockchain.py on the main blockchain server, then run blockchain.py on all other blockchain servers. 


Then set up ISPs.
1. Open ISP folder. Edit the config.py file, change “blockchain address” to any of the blockchain addresses and “CA_address”, “encrypt_server” to any of the three Evaluator’s addresses.  
2. Run app.py and follow the instructions to set up an ISP.

Set up cloud.
1.Open Cloud folder. Edit the config.py file, change “blockchain address” to any of the blockchain addresses and “CA_address”, “encrypt_server” to any of the three Evaluator’s addresses.  
2.Run app.py and follow the instructions to set up a Cloud.

Perform query to get the number of ISP overlaps.
1.Open User folder. Edit the config.py file, change “blockchain address” to any of the blockchain.
2.Run app.py and follow the instructions to perform a query. 

