##Tea Sepolia Auto send token

Deploy SmartContract

```bash
wget https://raw.githubusercontent.com/choir94/Airdropguide/refs/heads/main/Teh.sh && chmod +x Teh.sh && ./Teh.sh
```

Clone

```bash
git clone https://github.com/choir94/Send.git
cd Send
```

Install Dependencie
```
sudo apt install python3 python3-pip -y
```

```bash
pip3 install -r requirements.txt
```

Jalankan Bot
screen

```bash
screen -S autosend
```
```bash
python3 Tea-send.py
```
Atau pakai ini untuk via .env, transaksi delay, address kyc auto download.
Ganti private key
```bash
nano .env
```
Jalankan
```bash
python3 bot.py
```

-- Done
