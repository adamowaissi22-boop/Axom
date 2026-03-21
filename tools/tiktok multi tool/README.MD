tiktok multi tool by Axom! 

- installation
git clone https://github.com/adamowaissi22-boop/Axom
cd Axom
bash install.sh

- Usage
download and remove watermark of tiktok video :

python twr.py -u https://www.tiktok.com/@user/video/123456789

- method selection :
python twr.py -u https://www.tiktok.com/@user/video/123456789 -m delogo
python twr.py -u https://www.tiktok.com/@user/video/123456789 -m crop
python twr.py -u https://www.tiktok.com/@user/video/123456789 -m blur


- position selector (left, right, up, down, left up, etc) 
python twr.py -u URL -p br    
python twr.py -u URL -p bl    
python twr.py -u URL -p tr   
python twr.py -u URL -p tl   

br = bottom right
bl = bottom left
tr = top right
tl = top left. 

- combined args/option, twin 
python twr.py -u https://www.tiktok.com/@user/video/123456789 -m blur -p tr

- using alias :
twr -u https://www.tiktok.com/@user/video/123456789


OUTPUT = /storage/emulated/0/Download/nowm/

Credits :

Creator : Axom
Devs : NONE 

tool under development twin ✌
